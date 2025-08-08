"""
MCP tools for plan management: upload_plan and validate_plan - simplified for text plans.
"""

from typing import Dict, Any, Optional
from fastmcp import Context

from src.services.plan_service import PlanService
# NO AUTHENTICATION - Local MCP server


# NO AUTH REQUIRED
async def upload_plan(
    plan_data: str,
    auto_create_tasks: bool = False,
    context: Optional[Context] = None
) -> Dict[str, Any]:
    """
    Upload a new plan to the system.
    
    Args:
        plan_data: Text string containing the plan
        auto_create_tasks: Not used (kept for compatibility)
        context: MCP context for logging
        
    Returns:
        Dict containing upload result with plan_id and success status
    """
    try:
        # Log the upload attempt
        if context:
            await context.info(f"Uploading text plan")
        
        # Simple service to save the text plan
        plan_service = PlanService()
        
        # Save the plan as text
        plan_id = await plan_service.save_text_plan(plan_data)
        
        if context:
            await context.info(f"Successfully uploaded plan with ID {plan_id}")
        
        return {
            "success": True,
            "data": {
                "plan_id": plan_id,
                "message": "Plan uploaded successfully"
            }
        }
        
    except Exception as e:
        error_msg = f"Failed to upload plan: {str(e)}"
        if context:
            await context.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }


# NO AUTH REQUIRED
async def validate_plan(plan_data: str, context: Optional[Context] = None) -> Dict[str, Any]:
    """
    Validate a plan - simplified to just check if text is provided.
    
    Args:
        plan_data: Text string containing plan data
        context: MCP context for logging
        
    Returns:
        Dict containing validation results
    """
    try:
        if context:
            await context.info("Validating plan data")
        
        # Simple validation - just check if we have text
        if not plan_data or not plan_data.strip():
            return {
                "success": False,
                "error": "Plan cannot be empty"
            }
        
        if context:
            await context.info("Plan validation successful")
        
        return {
            "success": True,
            "data": {
                "valid": True,
                "message": "Plan text is valid"
            }
        }
        
    except Exception as e:
        error_msg = f"Plan validation error: {str(e)}"
        if context:
            await context.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }