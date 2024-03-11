import asyncio
from socket import * 
from time import perf_counter


class RelayServer:

    def __init__(self):
        self.name = 'makerslab-fpga-17.d2.comp.nus.edu.sg'
        self.port1 = 36481
        self.is_running = True 
        self.timeout = 600
        self.connection_socket = None
        self.listen_socket = None
        self.is_connected = True

    async def recv_text(self, timeout):
        # len_data
        conn_socket = self.connection_socket
        text_received   = "localhost"
        success         = False
        if self.is_running:
            loop = asyncio.get_event_loop()
            try:
                while True:
                    # recv length followed by '_' followed by json
                    data = b''
                    while not data.endswith(b'_'):
                        start_time = perf_counter()
                        task = loop.sock_recv(conn_socket, 1)
                        _d = await asyncio.wait_for(task, timeout=timeout)
                        timeout -= (perf_counter() - start_time)
                        if not _d:
                            data = b''
                            break
                        data += _d
                    if len(data) == 0:
                        print('recv_text: relay client disconnected')
                        raise Exception
                        break
                    data = data.decode("utf-8")
                    length = int(data[:-1])
                    data = b''
                    while len(data) < length:
                        start_time = perf_counter()
                        task = loop.sock_recv(conn_socket, length - len(data))
                        _d = await asyncio.wait_for(task, timeout=timeout)
                        timeout -= (perf_counter() - start_time)
                        if not _d:
                            data = b''
                            break
                        data += _d
                    if len(data) == 0:
                        print('recv_text: relay client disconnected')
                        raise Exception
                        break
                    text_received = data.decode("utf8")  # Decode raw bytes to UTF-8
                    success = True
                    break
            except ConnectionResetError:
                print('recv_text: Connection Reset for relay')
                raise Exception
            except asyncio.TimeoutError:
                print('recv_text: Timeout while receiving data from relay')
                self.close_connection()
                timeout = -1
        else:
            timeout = -1

        return success, timeout, text_received
    

    async def receive_from_relay_node(self):
        _, _, text = await self.recv_text(self.timeout)
        return text 
    
    def send_to_relay_node(self, msg):
        self.connection_socket.send(msg)
        return msg
    
    def start_connection(self):
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind((self.name, self.port1))
        server_socket.listen()
        print('Relay server listening for connection on: ', self.name, self.port1)
        self.listen_socket = server_socket
        self.is_running = True 
        conn_socket, _ = server_socket.accept()
        self.connection_socket = conn_socket
        self.is_connected = True 

    def close_connection(self):
        if self.is_running:
            self.is_running = False
            conn, listen = self.connection_socket, self.listen_socket
            if conn:
                conn.shutdown(SHUT_RDWR)
                conn.close()
            if listen:
                listen.close()
