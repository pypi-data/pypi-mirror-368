from enum import Enum
from typing import Any, Protocol

from flask import Blueprint
from labfreed.pac_attributes.server.server import AttributeGroupDataSource, AttributeServerRequestHandler, InvalidRequestError, TranslationDataSource

try:
    from flask import Flask, Response, request
except ImportError:
    raise ImportError("Please install labfreed with the [extended] extra: pip install labfreed[extended]")


# from fastapi import FastAPI, Request

class Authenticator(Protocol):
    def __call__(self, request) -> bool: ...
    
class NoAuthRequiredAuthenticator(Authenticator):
    def __call__(self, request) -> bool:
        return True

class Webframework(Enum):
    FLASK = "flask"
    FASTAPI = 'fastapi'
    

class AttributeServerFactory():
    @staticmethod
    def create_server_app( datasources:list[AttributeGroupDataSource], 
                           default_language:str,
                           translation_data_sources:list[TranslationDataSource],
                           authenticator: Authenticator|None,
                           framework:Webframework=Webframework.FLASK
                           ):
        
        if not authenticator:
            raise ValueError("authenticator missing. Either define your own authenticator by implementing the 'Authenticator' Protocol, or - if you do not need authentication - explicitly pass a 'NoAuthRequiredAuthenticator' object")
            
        request_handler = AttributeServerRequestHandler(data_sources=datasources, 
                                                        translation_data_sources= translation_data_sources, 
                                                        default_language=default_language
                                                        )
            
        match(framework):
            case Webframework.FLASK:
                app = AttributeFlaskApp(request_handler,authenticator=authenticator)
                return app
            case Webframework.FASTAPI:
                raise NotImplementedError('FastAPI webapp not implemented')

            


            
class AttributeFlaskApp(Flask):
    def __init__(self, request_handler: AttributeServerRequestHandler, authenticator: Authenticator | None = None, **kwargs: Any):
        super().__init__(__name__, **kwargs)
        self.config['ATTRIBUTE_REQUEST_HANDLER'] = request_handler
        self.config['AUTHENTICATOR'] = authenticator
        
        bp = self.create_attribute_blueprint(request_handler, authenticator)
        self.register_blueprint(bp)

    @staticmethod
    def create_attribute_blueprint(
        request_handler: AttributeServerRequestHandler,
        authenticator: Authenticator | None = None,
    ) -> Blueprint:
        bp = Blueprint("attribute", __name__)

        @bp.route("/", methods=["POST"])
        def handle_attribute_request():
            if authenticator and not authenticator(request):
                return Response(
                    "Unauthorized", 401,
                    {"WWW-Authenticate": 'Basic realm="Login required"'}
                )
            try:
                json_request_body = request.get_data(as_text=True)
                response_body = request_handler.handle_attribute_request(json_request_body)
            except InvalidRequestError as e:
                print(e)
                return "Invalid request", 400
            except Exception as e:
                print(e)
                return "The request was valid, but the server encountered an error", 500
            return response_body

        @bp.route("/capabilities", methods=["GET"])
        def capabilities():
            return request_handler.capabilities()

        return bp
    
    



    

    
    
    
