"""
SQS Handler Module

This module provides a base class for handling AWS SQS events in Lambda functions.
It includes logging capabilities, action routing, and error handling.
"""

import json
import os
import sys
import traceback
from typing import Any, Dict, Optional

from velocity.aws import DEBUG
from velocity.aws.handlers import context as VelocityContext
from velocity.misc.format import to_json


class SqsHandler:
    """
    Base class for handling SQS events in AWS Lambda functions.
    
    Provides structured processing of SQS records with automatic action routing,
    logging capabilities, and error handling hooks.
    """

    def __init__(self, aws_event: Dict[str, Any], aws_context: Any, 
                 context_class=VelocityContext.Context):
        """
        Initialize the SQS handler.
        
        Args:
            aws_event: The AWS Lambda event containing SQS records
            aws_context: The AWS Lambda context object
            context_class: The context class to use for processing
        """
        self.aws_event = aws_event
        self.aws_context = aws_context
        self.serve_action_default = True
        self.skip_action = False
        self.ContextClass = context_class

    def log(self, tx, message: str, function: Optional[str] = None):
        """
        Log a message to the system log table.
        
        Args:
            tx: Database transaction object
            message: The message to log
            function: Optional function name, auto-detected if not provided
        """
        if not function:
            function = self._get_calling_function()

        data = {
            "app_name": os.environ.get("ProjectName", "Unknown"),
            "referer": "SQS",
            "user_agent": "QueueHandler",
            "device_type": "Lambda",
            "function": function,
            "message": message,
            "sys_modified_by": "Lambda:BackOfficeQueueHandler",
        }
        tx.table("sys_log").insert(data)
    
    def _get_calling_function(self) -> str:
        """
        Get the name of the calling function by inspecting the call stack.
        
        Returns:
            The name of the calling function or "<Unknown>" if not found
        """
        skip_functions = {"x", "log", "_transaction", "_get_calling_function"}
        
        for idx in range(10):  # Limit search to prevent infinite loops
            try:
                frame = sys._getframe(idx)
                function_name = frame.f_code.co_name
                
                if function_name not in skip_functions:
                    return function_name
                    
            except ValueError:
                # No more frames in the stack
                break
                
        return "<Unknown>"

    def serve(self, tx):
        """
        Process all SQS records in the event.
        
        Args:
            tx: Database transaction object
        """
        records = self.aws_event.get("Records", [])
        
        for record in records:
            self._process_record(tx, record)
    
    def _process_record(self, tx, record: Dict[str, Any]):
        """
        Process a single SQS record.
        
        Args:
            tx: Database transaction object
            record: Individual SQS record to process
        """
        attrs = record.get("attributes", {})
        postdata = {}
        
        # Parse message body if present
        body = record.get("body")
        if body:
            try:
                postdata = json.loads(body)
            except json.JSONDecodeError as e:
                print(f"Failed to parse SQS message body as JSON: {e}")
                postdata = {"raw_body": body}

        # Create local context for this record
        local_context = self.ContextClass(
            aws_event=self.aws_event,
            aws_context=self.aws_context,
            args=attrs,
            postdata=postdata,
            response=None,
            session=None,
        )
        
        try:
            self._execute_actions(local_context)
        except Exception as e:
            if hasattr(self, "onError"):
                self.onError(
                    local_context,
                    exc=e.__class__.__name__,
                    tb=traceback.format_exc(),
                )
            else:
                # Re-raise if no error handler is defined
                raise
    
    def _execute_actions(self, local_context):
        """
        Execute the appropriate actions for the given context.
        
        Args:
            local_context: The context object for this record
        """
        # Execute beforeAction hook if available
        if hasattr(self, "beforeAction"):
            self.beforeAction(local_context)
        
        # Determine which actions to execute
        actions = self._get_actions_to_execute(local_context)
        
        # Execute the first matching action
        for action in actions:
            if self.skip_action:
                return
                
            if hasattr(self, action):
                getattr(self, action)(local_context)
                break
        
        # Execute afterAction hook if available
        if hasattr(self, "afterAction"):
            self.afterAction(local_context)
    
    def _get_actions_to_execute(self, local_context) -> list:
        """
        Get the list of actions to execute for the given context.
        
        Args:
            local_context: The context object for this record
            
        Returns:
            List of action method names to try executing
        """
        actions = []
        
        # Add specific action if available
        action = local_context.action()
        if action:
            action_method = self._format_action_name(action)
            actions.append(action_method)
        
        # Add default action if enabled
        if self.serve_action_default:
            actions.append("OnActionDefault")
            
        return actions
    
    def _format_action_name(self, action: str) -> str:
        """
        Format an action string into a method name.
        
        Args:
            action: The raw action string
            
        Returns:
            Formatted method name
        """
        formatted = action.replace('-', ' ').replace('_', ' ')
        return f"on action {formatted}".title().replace(" ", "")

    def OnActionDefault(self, tx, context):
        """
        Default action handler when no specific action is found.
        
        Args:
            tx: Database transaction object
            context: The context object for this record
        """
        action = context.action() if hasattr(context, 'action') else 'unknown'
        warning_message = (
            f"[Warn] Action handler not found. Calling default action "
            f"`SqsHandler.OnActionDefault` with the following parameters:\n"
            f"  - action: {action}\n"
            f"  - attrs: {context.args()}\n"
            f"  - postdata: {context.postdata()}"
        )
        print(warning_message)
