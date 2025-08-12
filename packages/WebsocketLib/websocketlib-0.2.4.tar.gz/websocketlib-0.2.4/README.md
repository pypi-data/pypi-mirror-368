# WebsocketServerLibrary: a simple websocket server.
## main features :
1. automaticly calls the event functions.
2. simple client manager.
- sending messages: client().send(msg)
3. set event functions:
- server().set_fn_new_client(fn)
- server().set_fn_client_left(fn)
- server().set_fn_message_recived(fn)
