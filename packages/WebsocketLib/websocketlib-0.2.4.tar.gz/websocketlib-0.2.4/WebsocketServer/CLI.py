import code
import sys
import argparse
import WebsocketServer as ws


def new_client(client):
    print('a new client connected')


def client_left(client):
    print('a client left')


def message_received(client, msg):
    print(f'a client sent: {msg}')


def main():
    parser = argparse.ArgumentParser(usage='''\n
this command create an instance of the websocket server class.

example usage:\n
websocketserver myserver 127.0.0.1 5001 # create an instance on port 5001 and host 127.0.0.1
>>>from mymodule import new_client, message_received, client_left # import the functions you want to use
>>>myserver.set_fn_client_left(client_left) # set the client_left function
>>>myserver.set_fn_message_received(message_received) # set the message_received function
>>>myserver.set_fn_new_client(new_client) # set the new_client function
>>>server.start() # start the server
server running on 127.0.0.1:5001...
                                    ''')
    parser.add_argument('server_name', default='server', type=str, help="The name of the server instance (e.g., 'MyServer').")
    parser.add_argument('host', default='127.0.0.1', help="The host address for the WebSocket server.")
    parser.add_argument('port', default='5001', type=int, help="The port number for the WebSocket server.")
    args = parser.parse_args()
    server_name = args.server_name
    host = args.host
    port = args.port
    globals()[server_name] = ws.WebsocketServer(host, port)
    globals()[server_name].set_fn_client_left(client_left)
    globals()[server_name].set_fn_message_received(message_received)
    globals()[server_name].set_fn_new_client(new_client)
    banner = f"python {sys.version} on {sys.platform}\nImporting WebsocketServer..."
    console = code.InteractiveConsole(locals=globals())
    console.interact(banner=banner)
