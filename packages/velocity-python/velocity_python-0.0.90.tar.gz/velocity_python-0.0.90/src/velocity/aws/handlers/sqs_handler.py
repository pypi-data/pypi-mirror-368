from velocity.misc.format import to_json
import json
import sys
import os
import traceback
from velocity.aws import DEBUG
from velocity.aws.handlers import context as VelocityContext


class SqsHandler:

    def __init__(self, aws_event, aws_context, context_class=VelocityContext.Context):
        self.aws_event = aws_event
        self.aws_context = aws_context
        self.serve_action_default = True
        self.skip_action = False
        self.ContextClass = context_class

    def log(self, tx, message, function=None):
        if not function:
            function = "<Unknown>"
            idx = 0
            while True:
                try:
                    temp = sys._getframe(idx).f_code.co_name
                except ValueError as e:
                    break
                if temp in ["x", "log", "_transaction"]:
                    idx += 1
                    continue
                function = temp
                break

        data = {
            "app_name": os.environ["ProjectName"],
            "referer": "SQS",
            "user_agent": "QueueHandler",
            "device_type": "Lambda",
            "function": function,
            "message": message,
            "sys_modified_by": "lambda:BackOfficeQueueHandler",
        }
        tx.table("sys_log").insert(data)

    def serve(self, tx):
        records = self.aws_event.get("Records", [])
        for record in records:
            attrs = record.get("attributes")
            postdata = {}
            if record.get("body"):
                postdata = json.loads(record.get("body"))

            local_context = self.ContextClass(
                aws_event=self.aws_event,
                aws_context=self.aws_context,
                args=attrs,
                postdata=postdata,
                response=None,
                session=None,
            )
            try:
                if hasattr(self, "beforeAction"):
                    self.beforeAction(local_context)
                actions = []
                action = local_context.action()
                if action:
                    actions.append(
                        f"on action {action.replace('-', ' ').replace('_', ' ')}".title().replace(
                            " ", ""
                        )
                    )
                if self.serve_action_default:
                    actions.append("OnActionDefault")
                for action in actions:
                    if self.skip_action:
                        return
                    if hasattr(self, action):
                        getattr(self, action)(local_context)
                        break
                if hasattr(self, "afterAction"):
                    self.afterAction(local_context)
            except Exception as e:
                if hasattr(self, "onError"):
                    self.onError(
                        local_context,
                        exc=e.__class__.__name__,
                        tb=traceback.format_exc(),
                    )

    def OnActionDefault(self, tx, context):
        print(
            f"""
            [Warn] Action handler not found. Calling default action `SqsHandler.OnActionDefault` with the following parameters for attrs, and postdata:
            attrs: {str(context.args())}
            postdata: {str(context.postdata())}
            """
        )
