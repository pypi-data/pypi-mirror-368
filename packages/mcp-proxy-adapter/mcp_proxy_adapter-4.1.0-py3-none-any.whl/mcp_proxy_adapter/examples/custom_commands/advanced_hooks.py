"""
Advanced Hooks Example

This module demonstrates advanced hook capabilities:
1. Data transformation hooks - modify input data before command execution and format output after
2. Interception hooks - completely bypass command execution based on conditions
"""

import time
import logging
from typing import Dict, Any
from datetime import datetime

from mcp_proxy_adapter.commands.hooks import HookContext, HookType
from mcp_proxy_adapter.commands.result import CommandResult


# Setup logging for advanced hooks
logger = logging.getLogger("mcp_proxy_adapter.examples.advanced_hooks")


def data_transform_before_hook(context: HookContext) -> None:
    """
    Before hook for data_transform command - modifies input data.
    
    Args:
        context: Hook context with command information
    """
    logger.info(f"🔄 Data transform before hook: {context.params}")
    
    # Get original data
    original_data = context.params.get("data", {})
    
    # Transform data before command execution
    transformed_data = {}
    for key, value in original_data.items():
        if isinstance(value, str):
            # Add prefix and suffix to string values
            transformed_data[f"pre_{key}_post"] = f"ENHANCED_{value}_PROCESSED"
        elif isinstance(value, (int, float)):
            # Multiply numeric values by 2
            transformed_data[f"doubled_{key}"] = value * 2
        else:
            # Keep other types as is
            transformed_data[key] = value
    
    # Add metadata
    transformed_data["_hook_modified"] = True
    transformed_data["_modification_time"] = datetime.now().isoformat()
    
    # Replace original data with transformed data
    context.params["data"] = transformed_data
    context.params["data_modified"] = True
    
    logger.info(f"📊 Original data: {original_data}")
    logger.info(f"🔄 Transformed data: {transformed_data}")


def data_transform_after_hook(context: HookContext) -> None:
    """
    After hook for data_transform command - formats output data.
    
    Args:
        context: Hook context with command information
    """
    logger.info(f"🔄 Data transform after hook: {context.result}")
    
    if context.result and hasattr(context.result, 'transformed_data'):
        # Get the transformed data from command result
        transformed_data = context.result.transformed_data
        
        # Apply additional formatting
        formatted_data = {}
        for key, value in transformed_data.items():
            if isinstance(value, str):
                # Add formatting to string values
                formatted_data[f"formatted_{key}"] = f"✨ {value} ✨"
            else:
                formatted_data[key] = value
        
        # Add formatting metadata
        formatted_data["_formatted_by_hook"] = True
        formatted_data["_formatting_time"] = datetime.now().isoformat()
        
        # Update the result with formatted data
        context.result.transformed_data = formatted_data
        
        logger.info(f"✨ Formatted data: {formatted_data}")


def intercept_before_hook(context: HookContext) -> None:
    """
    Before hook for intercept command - can completely bypass execution.
    
    Args:
        context: Hook context with command information
    """
    logger.info(f"🚫 Intercept before hook: {context.params}")
    
    # Check bypass flag
    bypass_flag = context.params.get("bypass_flag", 1)
    
    if bypass_flag == 0:
        # Completely bypass command execution
        logger.info(f"🚫 Intercepting command execution - bypass_flag = 0")
        
        # Create a mock result without calling the actual command
        from .intercept_command import InterceptResult
        
        mock_result = InterceptResult(
            message="Command intercepted by hook - not executed",
            executed=False,
            intercept_reason="bypass_flag = 0",
            hook_data={
                "intercepted_by": "intercept_before_hook",
                "interception_time": datetime.now().isoformat(),
                "original_params": context.params.copy()
            }
        )
        
        # Set the result and stop standard processing
        context.result = mock_result
        context.standard_processing = False
        
        logger.info(f"✅ Command intercepted successfully")
    else:
        # Allow normal execution
        logger.info(f"✅ Allowing normal execution - bypass_flag = {bypass_flag}")
        context.params["hook_processed"] = True


def intercept_after_hook(context: HookContext) -> None:
    """
    After hook for intercept command.
    
    Args:
        context: Hook context with command information
    """
    if context.standard_processing:
        logger.info(f"✅ Intercept command executed normally")
    else:
        logger.info(f"🚫 Intercept command was intercepted by hook")
    
    # Add execution metadata
    if context.result and hasattr(context.result, 'hook_data'):
        context.result.hook_data["after_hook_processed"] = True
        context.result.hook_data["after_hook_time"] = datetime.now().isoformat()


def conditional_transform_hook(context: HookContext) -> None:
    """
    Conditional transformation hook - applies different transformations based on data.
    
    Args:
        context: Hook context with command information
    """
    if context.hook_type == HookType.BEFORE_EXECUTION:
        logger.info(f"🎯 Conditional transform before hook: {context.command_name}")
        
        # Check if this is a data_transform command
        if context.command_name == "data_transform":
            data = context.params.get("data", {})
            transform_type = context.params.get("transform_type", "default")
            
            # Apply conditional transformation based on data content
            if "special" in str(data).lower():
                logger.info(f"🎯 Special data detected - applying enhanced transformation")
                context.params["transform_type"] = "uppercase"
                context.params["_special_enhancement"] = True
            elif "test" in str(data).lower():
                logger.info(f"🎯 Test data detected - applying test transformation")
                context.params["transform_type"] = "reverse"
                context.params["_test_mode"] = True
    
    elif context.hook_type == HookType.AFTER_EXECUTION:
        logger.info(f"🎯 Conditional transform after hook: {context.command_name}")
        
        # Add conditional metadata to result
        if context.result and hasattr(context.result, 'processing_info'):
            context.result.processing_info["conditional_processed"] = True
            context.result.processing_info["conditional_time"] = datetime.now().isoformat()


def smart_intercept_hook(context: HookContext) -> None:
    """
    Smart interception hook - intercepts based on multiple conditions.
    
    Args:
        context: Hook context with command information
    """
    if context.hook_type == HookType.BEFORE_EXECUTION:
        logger.info(f"🧠 Smart intercept before hook: {context.command_name}")
        
        # Check multiple conditions for interception
        action = context.params.get("action", "")
        bypass_flag = context.params.get("bypass_flag", 1)
        
        # Intercept if action is "blocked" or bypass_flag is 0
        if action == "blocked" or bypass_flag == 0:
            logger.info(f"🧠 Smart intercept: action='{action}', bypass_flag={bypass_flag}")
            
            # Create intercepted result
            from .intercept_command import InterceptResult
            
            intercept_reason = "blocked_action" if action == "blocked" else "bypass_flag_zero"
            
            mock_result = InterceptResult(
                message=f"Command intercepted by smart hook - reason: {intercept_reason}",
                executed=False,
                intercept_reason=intercept_reason,
                hook_data={
                    "intercepted_by": "smart_intercept_hook",
                    "interception_time": datetime.now().isoformat(),
                    "original_params": context.params.copy(),
                    "smart_analysis": True
                }
            )
            
            # Set the result and stop standard processing
            context.result = mock_result
            context.standard_processing = False
            
            logger.info(f"✅ Smart interception completed")


def register_advanced_hooks(hooks_manager) -> None:
    """
    Register advanced hooks with the hooks manager.
    
    Args:
        hooks_manager: The hooks manager instance
    """
    logger.info("🔧 Registering advanced hooks...")
    
    # Register data transformation hooks
    hooks_manager.register_before_hook("data_transform", data_transform_before_hook)
    hooks_manager.register_after_hook("data_transform", data_transform_after_hook)
    
    # Register interception hooks
    hooks_manager.register_before_hook("intercept", intercept_before_hook)
    hooks_manager.register_after_hook("intercept", intercept_after_hook)
    
    # Register conditional hooks
    hooks_manager.register_global_before_hook(conditional_transform_hook)
    hooks_manager.register_global_after_hook(conditional_transform_hook)
    
    # Register smart interception hooks
    hooks_manager.register_global_before_hook(smart_intercept_hook)
    
    logger.info("✅ Advanced hooks registered successfully") 