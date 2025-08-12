from .basic_types import Client, _new_client_t, _client_left_t, _message_received_t
import socket
import hashlib
import base64
import struct
import threading
from typing import Never


class WebsocketServer:
    def __init__(self, host: str, port: int) -> None:
        """
        a websocket server waiting for clients to connect.

        <code>host: string: </code> the server host address.<br>
        <code>port: integer: </code> the host port.
        """
        self.host = host
        self.port = port


    _new_client: _new_client_t
    _client_left: _client_left_t
    _message_received: _message_received_t


    def set_fn_new_client(self, fn: _new_client_t):
        """
        set the new client function.

        <code>fn: callable: </code> the new function.

        <code>return: None. </code>
        """
        self._new_client = fn
        return self


    def set_fn_client_left(self, fn: _client_left_t):
        """
        set the client left function.

        <code>fn: callable: </code> the new function.

        <code>return: None. </code>
        """
        self._client_left = fn
        return self


    def set_fn_message_received(self, fn: _message_received_t):
        """
        set the message_received function.

        <code>fn: callable: </code> the new function.

        <code>return: None. </code>
        """
        self._message_received = fn
        return self


    def create_accept_key(self, request_key: str) -> str:
        """
        generate the accept key for the websocket handshake.

        <code>request_key: string: </code> the request key.

        <code>return: string: </code> the accept key.
        """
        magic_string = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        combined = request_key + magic_string
        sha1_hash = hashlib.sha1(combined.encode()).digest()
        accept_key = base64.b64encode(sha1_hash).decode()
        return accept_key


    def parse_websocket_frame(self, data: bytes) -> str:
        """
        parse a websocket frame.

        <code>data: bytes: </code> the frame.

        <code>retrun: string: </code> the message from the frame.
        """
        first_byte, second_byte = data[0], data[1]
        length = second_byte & 0x7F
        is_masked = second_byte & 0x80 != 0
        if length == 126:
            length = struct.unpack('>H', data[2:4])[0]
            header_size = 4
        elif length == 127:
            length = struct.unpack('>Q', data[2:10])[0]
            header_size = 10
        else:
            header_size = 2
        if is_masked:
            mask_key = data[header_size:header_size+4]
            payload_data = data[header_size+4:header_size+4+length]
            payload = bytearray([payload_data[i] ^ mask_key[i % 4] for i in range(len(payload_data))])
        else:
            payload = data[header_size:header_size+length]
        return payload.decode()


    def handle_client(self, client_socket: Client) -> None:
        """
        handle the client websocket connection.

        <code>client_socket: Client: </code> the client socket.

        <code>return: None. </code>
        """
        try:
            request = client_socket.sock.recv(1024).decode()
            if not request:
                print("Client disconnected during handshake.")
                return
            headers = {line.split(":")[0].strip(): line.split(":")[1].strip() for line in request.split("\r\n")[1:-2]}
            webkey = headers.get('Sec-WebSocket-Key', '')
            if webkey:
                accept_key = self.create_accept_key(webkey)
                response = (
                    'HTTP/1.1 101 Switching Protocols\r\n'
                    'Upgrade: websocket\r\n'
                    'Connection: Upgrade\r\n'
                    f'Sec-WebSocket-Accept: {accept_key}\r\n\r\n'
                )
                client_socket.sock.send(response.encode())
            else:
                client_socket.sock.close()
                return
            self._new_client(client_socket)
            while True:
                try:
                    data = client_socket.sock.recv(1024)
                    if not data:
                        break
                    message = self.parse_websocket_frame(data)
                    self._message_received(client_socket, message)
                except socket.error as e:
                    break
                except Exception as e:
                    break
        except Exception as e:
            pass
        finally:
            try:
                client_socket.sock.close()
                self._client_left(client_socket)
            except socket.error:
                pass

    
    def run_forever(self) -> Never:
        """
        run the websocket server forever.
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        while True:
            client_socket, client_address = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(Client(client_socket),))
            client_thread.start()


    def start(self, threaded: bool = False) -> None:
        """
        start the websocket server.
        """
        print(f'server running on {self.host}:{self.port}...')
        if threaded:
            self.thread = threading.Thread(target=self.run_forever, daemon=True)
            self.thread.start()
        else:
            self.run_forever()
