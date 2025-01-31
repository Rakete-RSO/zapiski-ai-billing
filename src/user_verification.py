import os
import grpc
from functools import lru_cache
from src import user_verification_pb2
from src import user_verification_pb2_grpc
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class UserVerificationClient:
    def __init__(self, host: str = "localhost", port: int = 50051):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = user_verification_pb2_grpc.UserVerificationStub(self.channel)

    def verify_user(self, username: str) -> bool:
        try:
            request = user_verification_pb2.UserRequest(username=username)
            response = self.stub.VerifyUser(request)
            return response.exists
        except grpc.RpcError as e:
            print(f"gRPC error: {e}")
            return False


@lru_cache()
def get_user_verification_client() -> UserVerificationClient:
    host = os.getenv("AUTH_SERVICE_HOST", "auth-service")
    port = int(os.getenv("AUTH_SERVICE_GRPC_PORT", "50051"))
    logger.debug(f"Creating client with host={host}, port={port}")
    return UserVerificationClient(host, port)
