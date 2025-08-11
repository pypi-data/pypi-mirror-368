"""
Scheduling module for appointment booking and time slot management.
"""
import inspect
import logging
from datetime import datetime
import asyncio
import random
import aiohttp
import httpx
from pipecat.frames.frames import FunctionCallResultProperties
from pipecat.services.llm_service import FunctionCallParams
from pipecat_tools.core.consts import get_constant


async def convert_slot_to_iso_format(time_slot: str, date_str: str) -> dict:
    """
    Converts a time slot and date to ISO format for start_date and end_date.
    
    Args:
        time_slot (str): Time slot in format "HH:MM - HH:MM"
        date_str (str): Date in format "YYYY-MM-DD"
        
    Returns:
        dict: Dictionary with start_date and end_date in ISO format
    """
    start_time, end_time = time_slot.split(' - ')
    
    # Parse the date
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    
    # Parse start and end times
    start_hours, start_minutes = map(int, start_time.split(':'))
    end_hours, end_minutes = map(int, end_time.split(':'))
    
    # Create datetime objects for start and end
    start_datetime = date_obj.replace(hour=start_hours, minute=start_minutes, second=0, microsecond=0)
    end_datetime = date_obj.replace(hour=end_hours, minute=end_minutes, second=0, microsecond=0)
    
    # Return ISO format with Z at the end (UTC)
    return {
        'start_date': start_datetime.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
        'end_date': end_datetime.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    }


async def check_slot_availability(session, time_slot: str, date_str: str, webhook_url: str) -> dict:
    """
    Asynchronously checks slot availability via webhook.
    
    Args:
        session: aiohttp session
        time_slot (str): Time slot in format "HH:MM - HH:MM"
        date_str (str): Date in format "YYYY-MM-DD"
        webhook_url (str): URL to check availability
        
    Returns:
        dict: Dictionary with slot information and availability status
    """
    # Convert slot to ISO format
    slot_params = await convert_slot_to_iso_format(time_slot, date_str)
    
    # Send request to webhook
    try:
        async with session.get(webhook_url, params=slot_params) as response:
            # By default, slot is unavailable
            is_available = False
            
            if response.status == 200:
                try:
                    # Try to read response as JSON
                    result = await response.json()
                    
                    # Check response structure: [{"available": true/false}]
                    if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
                        is_available = result[0].get('available', False)
                    # Also check alternative structure: {"is_available": true/false}
                    elif isinstance(result, dict):
                        is_available = result.get('is_available', result.get('available', False))
                except Exception as json_error:
                    print(f"Error parsing JSON for slot {time_slot} on {date_str}: {json_error}")
                    # If JSON parsing fails, use text response
                    try:
                        text_response = await response.text()
                        # Simple check for keywords in response
                        is_available = 'true' in text_response.lower() or 'available' in text_response.lower()
                    except:
                        pass
            
            # Return result
            return {
                'time_slot': time_slot,
                'is_available': is_available,
                'date': date_str
            }
    except Exception as e:
        # Handle connection errors
        print(f"Error checking slot {time_slot} on {date_str}: {e}")
        return {
            'time_slot': time_slot,
            'is_available': False,
            'date': date_str
        }


async def get_available_time_slots(params: FunctionCallParams):
    """
    Asynchronously gets all available time slots for a list of dates.
    
    Args:
        params: Pipecat function call parameters containing:
            - dates (List[str]): List of dates in format "YYYY-MM-DD"
        
    Returns:
        None: Result is sent via callback containing list of dictionaries with dates and available slots
    """
    # Extract arguments from the standard Pipecat wrapper
    dates = params.arguments["dates"]
    agent_id = params.arguments["agent_id"]

    # getting webhook_url for current function
    webhook_url = get_constant(agent_id, inspect.currentframe().f_code.co_name, "webhook_url")

    time_slots = [
        "09:00 - 09:30", "09:30 - 10:00", "10:00 - 10:30", "10:30 - 11:00",
        "11:00 - 11:30", "11:30 - 12:00", "13:00 - 13:30", "13:30 - 14:00",
        "14:00 - 14:30", "14:30 - 15:00", "15:00 - 15:30", "15:30 - 16:00",
        "16:00 - 16:30", "16:30 - 17:00"
    ]
    
    result = []
    
    # Create a single session for all requests
    async with aiohttp.ClientSession() as session:
        for date_str in dates:
            dt_obj = datetime.strptime(date_str, "%Y-%m-%d")
            formatted_date = f"{date_str}, {dt_obj.strftime('%A')}"
            
            # Skip weekends
            if dt_obj.weekday() in [5, 6]:  # 5 = Saturday, 6 = Sunday
                result.append({
                    "date": formatted_date,
                    "free_slots": []
                })
                continue
            
            # If webhook is not set, use pseudo-random slot selection
            if not webhook_url:
                logger = logging.getLogger(__name__)
                logger.info(f"Webhook URL is not set as get_available_time_slots() tool constant, generating dummy available_time_slots.")

                random.seed(int(dt_obj.timestamp()))
                free_slots_count = random.randint(0, 7)
                free_slots = random.sample(time_slots, free_slots_count) if free_slots_count > 0 else []
                result.append({
                    "date": formatted_date,
                    "free_slots": sorted(free_slots)
                })
                continue
            
            # Create a list of tasks to check all slots for the current date
            tasks = [
                check_slot_availability(session, slot, date_str, webhook_url)
                for slot in time_slots
            ]
            
            # Run all tasks concurrently
            slot_results = await asyncio.gather(*tasks)
            
            # Filter only available slots
            available_slots = [
                item['time_slot'] for item in slot_results 
                if item['is_available']
            ]
            
            result.append({
                "date": formatted_date,
                "free_slots": sorted(available_slots)
            })

    properties = FunctionCallResultProperties(run_llm=True)
    await params.result_callback(result, properties=properties)


async def book_appointment(params: FunctionCallParams):
    """
    Book an appointment for a client.

    Args:
        params: Pipecat function call parameters containing:
            - name (str): Client's full name.
            - email (str): Client's email address.
            - phone_number (str): Client's phone number.
            - selected_time_slot (str): Appointment slot in the format "YYYY-MM-DD, HH:MM - HH:MM".


    Returns:
        None: Result is sent via callback containing { status: "success"|"error", message: str }
    """
    name = params.arguments["name"]
    email = params.arguments["email"]
    phone_number = params.arguments["phone_number"]
    selected_time_slot = params.arguments["selected_time_slot"]
    agent_id = params.arguments["agent_id"]

    # getting webhook_url for current function
    webhook_url = get_constant(agent_id, inspect.currentframe().f_code.co_name, "webhook_url")

    # Use provided webhook_url or get from environment
    if not webhook_url:
        result = {"status": "error", "message": "Webhook URL is not set as book_appointment() tool constant."}
        await params.result_callback(result)
        return

    payload = {
        "name": name,
        "email": email,
        "phone_number": phone_number,
        "selected_time_slot": selected_time_slot
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = {"status": "success", "message": "Appointment booked successfully."}
        else:
            result = {"status": "error", "message": "Sorry, I can't book an appointment right now."}
        
        await params.result_callback(result)
    except Exception as e:
        result = {"status": "error", "message": f"Booking error: {e}"}
        await params.result_callback(result) 