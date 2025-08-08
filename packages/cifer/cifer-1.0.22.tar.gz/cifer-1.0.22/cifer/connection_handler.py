from urllib.parse import urlparse
import asyncio
import websockets
import json
import ssl
import numpy as np
import jwt
import grpc
import base64

from cifer.training import train_custom_model
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

import federated_pb2
import federated_pb2_grpc

SECRET_KEY = "your_jwt_secret_key"

class FederatedGRPCHandler(federated_pb2_grpc.FederatedServiceServicer):
    def __init__(self, server):
        self.server = server

    async def SendModel(self, request, context):
        try:
            if self.server.use_homomorphic:
                model_weights = self.server.decrypt_data(request.weights)
            else:
                model_weights = [np.frombuffer(w, dtype=np.float32) for w in request.weights]

            self.server.model_weights_list.append(model_weights)

            if len(self.server.model_weights_list) == self.server.n_round_clients:
                print("[gRPC] Aggregating model weights...")
                aggregated = [np.mean([client[i] for client in self.server.model_weights_list], axis=0)
                              for i in range(len(self.server.model_weights_list[0]))]
                self.server.model_weights_list.clear()

                x_train, y_train = np.random.rand(1000, 28, 28), np.random.randint(0, 10, 1000)
                train_custom_model(self.server.custom_model, x_train, y_train, epochs=10)

            return federated_pb2.ServerResponse(status="success", message="Model received and aggregated")
        except Exception as e:
            return federated_pb2.ServerResponse(status="error", message=str(e))

    async def RequestPublicKey(self, request, context):
        if self.server.use_homomorphic:
            pubkey = self.server.public_key.export_key().decode()
            return federated_pb2.KeyResponse(public_key=pubkey)
        return federated_pb2.KeyResponse(public_key="")


class FederatedServer:
    def __init__(self, ip_address='ws://127.0.0.1', port=8765, n_round_clients=3,
                 use_homomorphic=False, certfile='certificate.pem', keyfile='private_key.pem'):
        self.url = urlparse(ip_address)
        self.host = self.url.hostname or "127.0.0.1"
        self.port = port
        self.scheme = self.url.scheme
        self.use_homomorphic = use_homomorphic
        self.certfile = certfile
        self.keyfile = keyfile
        self.n_round_clients = n_round_clients
        self.connected_clients = set()
        self.model_weights_list = []

        if self.use_homomorphic:
            self.private_key = RSA.generate(3072)
            self.public_key = self.private_key.publickey()

    def decrypt_data(self, encrypted_data):
        cipher = PKCS1_OAEP.new(self.private_key)
        return [np.frombuffer(cipher.decrypt(base64.b64decode(w)), dtype=np.float32) for w in encrypted_data]

    async def authenticate_client(self, websocket):
        token = await websocket.recv()
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            print(f"Authenticated user: {payload['user_id']}")
            return True
        except jwt.InvalidTokenError:
            await websocket.close()
            return False

    async def receive_message(self, websocket, path):
        if not await self.authenticate_client(websocket):
            return

        self.connected_clients.add(websocket)

        if len(self.connected_clients) == self.n_round_clients:
            print("[WebSocket] All clients connected.")
            for client in list(self.connected_clients):
                try:
                    if client.open:
                        await client.send(json.dumps({"status": "ready", "message": "Server is ready. Send your model."}))
                except websockets.exceptions.ConnectionClosedError:
                    self.connected_clients.remove(client)

        try:
            async for message in websocket:
                data = json.loads(message)
                if data['type'] == 'request_public_key' and self.use_homomorphic:
                    await websocket.send(self.public_key.export_key().decode())
                elif data['type'] == 'send_model':
                    await self.handle_model_data(data, websocket)
        except websockets.exceptions.ConnectionClosedError:
            pass
        finally:
            self.connected_clients.remove(websocket)

    async def handle_model_data(self, data, websocket):
        try:
            if self.use_homomorphic:
                model_weights = self.decrypt_data(data['weights'])
            else:
                model_weights = [np.array(w) for w in data['weights']]
            self.model_weights_list.append(model_weights)

            if len(self.model_weights_list) == self.n_round_clients:
                print("[WebSocket] Aggregating model weights...")
                aggregated = [np.mean([client[i] for client in self.model_weights_list], axis=0)
                              for i in range(len(self.model_weights_list[0]))]
                self.model_weights_list.clear()

                x_train, y_train = np.random.rand(1000, 28, 28), np.random.randint(0, 10, 1000)
                train_custom_model(self.custom_model, x_train, y_train, epochs=10)

                for client in list(self.connected_clients):
                    try:
                        if client.open:
                            await client.send(json.dumps({
                                "status": "success",
                                "message": "Model aggregated and trained successfully"
                            }))
                    except websockets.exceptions.ConnectionClosedError:
                        self.connected_clients.remove(client)
        except Exception as e:
            await websocket.send(json.dumps({
                "status": "error",
                "message": f"Failed to process model weights: {str(e)}"
            }))

    def set_custom_model(self, model):
        self.custom_model = model

    async def start_grpc_server(self):
        server = grpc.aio.server()
        federated_pb2_grpc.add_FederatedServiceServicer_to_server(FederatedGRPCHandler(self), server)
        server.add_insecure_port(f"{self.host}:{self.port}")
        print(f"✅ gRPC server running at grpc://{self.host}:{self.port}")
        await server.start()
        await server.wait_for_termination()

    async def start_websocket_server(self):
        ssl_context = None
        if self.scheme == "wss":
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(self.certfile, self.keyfile)
        print(f"✅ WebSocket server running at {self.scheme}://{self.host}:{self.port}")
        return await websockets.serve(self.receive_message, self.host, self.port, ssl=ssl_context)

    async def start_server(self):
        if self.scheme in ["grpc", "http"]:
            await self.start_grpc_server()
        elif self.scheme in ["ws", "wss"]:
            await self.start_websocket_server()
            await asyncio.Future()
        else:
            raise ValueError(f"Unsupported scheme: {self.scheme}")


def run_federated_server(ip_address='ws://127.0.0.1', port=8765, n_round_clients=3,
                         custom_model=None, use_homomorphic=False,
                         certfile='certificate.pem', keyfile='private_key.pem'):
    server = FederatedServer(ip_address, port, n_round_clients, use_homomorphic, certfile, keyfile)
    server.set_custom_model(custom_model)
    asyncio.run(server.start_server())
