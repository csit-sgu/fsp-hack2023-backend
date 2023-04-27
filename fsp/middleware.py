from flask import Request, abort

class CheckFields:

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = Request(environ)
        if request.content_type.lower() == "application/json":
            if request.json is None or any([d is None for d in dict(request.json).values()]):
                abort(400)

        return self.app(environ, start_response)
