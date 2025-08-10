import support.app

engine = support.app.postgres()


@engine.transaction
class Context:

    def __init__(
        self, aws_event, aws_context, args, postdata, response, session, log=None
    ):
        self.__args = args
        self.__postdata = postdata
        self.__response = response
        self.__session = session
        self.__aws_event = aws_event
        self.__aws_context = aws_context
        self.__log = log

    def postdata(self, keys=-1, default=None):
        if keys == -1:
            return self.__postdata
        if not isinstance(keys, list):
            keys = [keys]
        data = self.__postdata
        for key in keys:
            if key in data:
                data = data[key]
            else:
                return default
        return data

    def payload(self, keys=-1, default={}):
        if "payload" not in self.__postdata:
            return default
        if keys == -1:
            return self.__postdata["payload"]
        if not isinstance(keys, list):
            keys = [keys]
        data = self.__postdata["payload"]
        for key in keys:
            if key in data:
                data = data[key]
            else:
                return default
        return data

    def action(self):
        return self.__postdata.get("action", self.__args.get("action", ""))

    def args(self):
        return self.__args

    def response(self):
        return self.__response

    def session(self):
        return self.__session

    def dataset(self):
        return self.payload().get("dataset", {})

    def log(self, message, function=None):
        if self.__log:
            return self.__log(message, function)
        else:
            if function:
                print(f"{function}: {message}")
            else:
                print(f"{message}")
