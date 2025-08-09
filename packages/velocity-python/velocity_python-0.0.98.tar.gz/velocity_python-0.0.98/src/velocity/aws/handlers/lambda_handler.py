from velocity.misc.format import to_json
import json
import sys
import os
import traceback
from support.app import DEBUG
from support.app import helpers, AlertError, enqueue

from velocity.aws.handlers import Response

from . import context


class LambdaHandler:
    def __init__(self, aws_event, aws_context, context_class=context.Context):
        self.aws_event = aws_event
        self.aws_context = aws_context
        self.serve_action_default = True  # Set to False to disable OnActionDefault
        self.skip_action = False  # Set to True to skip all actions

        requestContext = aws_event.get("requestContext") or {}
        identity = requestContext.get("identity") or {}
        headers = aws_event.get("headers") or {}
        auth = identity.get("cognitoAuthenticationProvider")
        self.session = {
            "authentication_provider": identity.get("cognitoAuthenticationProvider"),
            "authentication_type": identity.get("cognitoAuthenticationType"),
            "cognito_user": identity.get("user"),
            "is_desktop": headers.get("CloudFront-Is-Desktop-Viewer") == "true",
            "is_mobile": headers.get("CloudFront-Is-Mobile-Viewer") == "true",
            "is_smart_tv": headers.get("CloudFront-Is-SmartTV-Viewer") == "true",
            "is_tablet": headers.get("CloudFront-Is-Tablet-Viewer") == "true",
            "origin": headers.get("origin"),
            "path": aws_event.get("path"),
            "referer": headers.get("Referer"),
            "source_ip": identity.get("sourceIp"),
            "user_agent": identity.get("userAgent"),
            "sub": auth.split(":")[-1] if auth else None,
        }
        if self.session.get("is_mobile"):
            self.session["device_type"] = "mobile"
        elif self.session.get("is_desktop"):
            self.session["device_type"] = "desktop"
        elif self.session.get("is_tablet"):
            self.session["device_type"] = "tablet"
        elif self.session.get("is_smart_tv"):
            self.session["device_type"] = "smart_tv"
        else:
            self.session["device_type"] = "unknown"

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
            "source_ip": self.session["source_ip"],
            "referer": self.session["referer"],
            "user_agent": self.session["user_agent"],
            "device_type": self.session["device_type"],
            "function": function,
            "message": message,
        }
        if "email_address" in self.session:
            data["sys_modified_by"] = self.session["email_address"]
        tx.table("sys_log").insert(data)

    def serve(self, tx):
        response = Response()
        body = self.aws_event.get("body")
        postdata = {}
        if isinstance(body, str) and len(body) > 0:
            try:
                postdata = json.loads(body)
            except:
                postdata = {"raw_body": body}
        elif isinstance(body, dict):
            postdata = body
        elif isinstance(body, list) and len(body) > 0:
            try:
                new = "\n".join(body)
                postdata = json.loads(new)
            except:
                postdata = {"raw_body": body}

        req_params = self.aws_event.get("queryStringParameters") or {}
        local_context = self.ContextClass(
            aws_event=self.aws_event,
            aws_context=self.aws_context,
            args=req_params,
            postdata=postdata,
            response=response,
            session=self.session,
            log=lambda message, function=None: self.log(message, function),
        )
        try:
            if hasattr(self, "beforeAction"):
                self.beforeAction(local_context)
            actions = []
            action = postdata.get("action", req_params.get("action"))
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
                    break
                if hasattr(self, action):
                    result = getattr(self, action)(local_context)
                    if result is not None:
                        raise Exception(
                            f"Deprecated Feature Error: Action {action} returned a response but this is not allowed. Use Repsonse object instead: {type(result)}"
                        )
                    break
            if hasattr(self, "afterAction"):
                self.afterAction(local_context)
        except AlertError as e:
            response.alert(e.get_payload())
        except Exception as e:
            response.exception()
            if hasattr(self, "onError"):
                self.onError(
                    local_context,
                    exc=e.__class__.__name__,
                    tb=traceback.format_exc(),
                )

        return response.render()

    def track(self, tx, data={}, user=None):
        data = data.copy()
        data.update(
            {
                "source_ip": self.session["source_ip"],
                "referer": self.session["referer"],
                "user_agent": self.session["user_agent"],
                "device_type": self.session["device_type"],
                "sys_modified_by": self.session["email_address"],
            }
        )
        tx.table(helpers.get_tracking_table(user or self.session)).insert(data)

    def OnActionDefault(self, tx, context):
        context.response().set_body(
            {"event": self.aws_event, "postdata": context.postdata()}
        )

    def OnActionTracking(self, tx, context):
        self.track(tx, context.payload().get("data", {}))

    def enqueue(self, tx, action, payload={}):
        enqueue(tx, action, payload, self.session["email_address"])
