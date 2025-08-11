"""
Call management module for handling calls and call-related utilities.
"""

from datetime import datetime

from pipecat.frames.frames import EndFrame, FunctionCallResultProperties
from pipecat.services.llm_service import FunctionCallParams


async def transfer_call(params: FunctionCallParams):
    """
    Transfer the call to a licensed agent.
    
    Args:
        params: Pipecat function call parameters
        
    Returns:
        None: Result is sent via callback
    """
    await params.result_callback("Transferring the call")


async def await_call_transfer(params: FunctionCallParams):
    """
    Transfer the call to a licensed agent.

    Args:
        params: Pipecat function call parameters
        
    Returns:
        None: Result is sent via callback
    """
    await params.result_callback(
        "The call is being transferred", 
        properties=FunctionCallResultProperties(run_llm=False)
    )


async def end_call(params: FunctionCallParams):
    """
    End the current call.
    
    Args:
        params: Pipecat function call parameters
        
    Returns:
        None: Result is sent via callback
    """

    async def on_update():
        await params.llm.push_frame(EndFrame())

    await params.result_callback(
        "Call ended.", 
        properties=FunctionCallResultProperties(
            run_llm=True, 
            on_context_updated=on_update
        )
    )


async def get_weekday(params: FunctionCallParams):
    """
    Takes a date string in YYYY-MM-DD format and returns a formatted response indicating
    the day of the week that date falls on.
    
    Args:
        params: Pipecat function call parameters containing:
            - date (str): Date in YYYY-MM-DD format
        
    Returns:
        None: Result is sent via callback
    """
    try:
        dt = datetime.strptime(params.arguments["date"], "%Y-%m-%d")
        weekday = dt.strftime("%A")
        result = f"User asked to be scheduled to {weekday}"
    except ValueError:
        result = "Invalid date format. Please use YYYY-MM-DD."

    properties = FunctionCallResultProperties(run_llm=True)
    await params.result_callback(result, properties=properties) 