import asyncio
from multiprocessing import Process
from time import perf_counter
from socket import *
import time


class RelayNode:
    def __init__(self):
        self.server_hostname = 'localhost'
        self.server_port = 36481
        self.conn_socket = None 
        self.timeout = 600 

    async def recv_text(self, timeout, conn_socket):
        text_received   = ""
        success         = False
        if True:
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
                        break
                    text_received = data.decode("utf8")  # Decode raw bytes to UTF-8
                    success = True
                    break
            except ConnectionResetError:
                print('recv_text: Connection Reset for relay')
            except asyncio.TimeoutError:
                print('recv_text: Timeout while receiving data from relay')
                self.close_connection()
                timeout = -1
        else:
            timeout = -1

        return success, timeout, text_received
    
    async def receive_from_relay_server(self):
        _, _, text = await self.recv_text(self.timeout, self.conn_socket)
        print('Gamestate received from relay server is: ', text)
        return text 
    
    def send_to_relay_server(self, msg):
        self.conn_socket.send(msg.encode('utf8'))
        return msg 
    
    def connect_to_relay_server(self):
        self.conn_socket = socket(AF_INET, SOCK_STREAM)
        self.conn_socket.connect((self.server_hostname, self.server_port))
    
    def close_relay_node(self):
        self.conn_socket.close()

    def receive_from_relay_server_task(self):
        while True:
            try:
                asyncio.run(self.receive_from_relay_server())
            except Exception as e:
                print(e)
                break 
    
    def send_to_relay_server_task(self):
        msg = str([1,1,1])
        while True:
            self.send_to_relay_server(str(len(msg)) + '_' + msg)
            time.sleep(3)
    
if __name__ == '__main__':
    relay_node = RelayNode()
    relay_node.connect_to_relay_server()
    processes = []

    try:
        send_to_relay_server_process = Process(target=relay_node.send_to_relay_server_task, args=(), daemon=True)
        processes.append(send_to_relay_server_process)
        send_to_relay_server_process.start()

        receive_from_relay_server_process = Process(target=relay_node.receive_from_relay_server_task, args=(), daemon=True)
        processes.append(receive_from_relay_server_process)
        receive_from_relay_server_process.start()
    except Exception as e:
        print(e)

    for p in processes:
        p.join()



