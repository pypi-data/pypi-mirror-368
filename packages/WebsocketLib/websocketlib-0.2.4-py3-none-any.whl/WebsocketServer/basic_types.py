from typing import Callable, Self, TypeAlias
import socket
import struct


class Client:
        """
        a class for managing the websocket server clients.
        """
        def __init__(self, sock: socket.socket) -> None:
            """
            store the socket itself.

            <code>sock: socket: </code> the websocket.

            <code>return: None. </code>
            """
            self.sock = sock


        def frame_message(self, message: str) -> bytes:
            """
            frame a websocket message.

            <code>message: string: </code> the message.

            <code>return: bytes: </code> the frame header in bytes.
            """
            message_bytes = message.encode()
            length = len(message_bytes)
            frame_header = bytearray([0b10000001])
            if length <= 125:
                frame_header.append(length)
            elif length <= 65535:
                frame_header.append(126)
                frame_header.extend(struct.pack('>H', length))
            else:
                frame_header.append(127)
                frame_header.extend(struct.pack('>Q', length))
            frame_header.extend(message_bytes)
            return bytes(frame_header)
        

        def send(self, msg: str) -> None:
            """
            send data to the client.

            <code>msg: string: </code> the data to be sent.

            <code>return: None. </code>
            """
            response = self.frame_message(msg)
            self.sock.send(response)



_new_client_t: TypeAlias = Callable[[Self, Client], None]

_client_left_t: TypeAlias = Callable[[Self, Client], None]
    

_message_received_t: TypeAlias = Callable[[Self, Client, str], None]
