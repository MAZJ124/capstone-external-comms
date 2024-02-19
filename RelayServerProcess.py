import asyncio
from multiprocessing import Process, Value, Queue
import multiprocessing
import time

from RelayServer import RelayServer

class RelayServerProcess:
    def __init__(self):
        self.relay_server = RelayServer()
        self.processes = []
        self.client_connected = Value('i', 1)
        self.client_socket_update = Queue()

    def __getstate__(self) -> object:
        state = self.__dict__.copy()
        # for k in state:
        #     try:
        #         pickle.dumps(state[k])
        #     except Exception as e:
        #         print(e)
        #         print(k)
        #         print(state[k])
        #         print()
        # del state['processes']
        return state

    async def receive_from_relay_node(self):
        try:
            msg = await self.relay_server.receive_from_relay_node()
            if self.relay_server.is_running:
                print('Data received from relay node is: ' + msg)
        except Exception:
            self.relay_server.close_connection()
    
    def receive_from_relay_node_task(self):
        print('Receiving')
        while self.relay_server.is_running:
            try:
                asyncio.run(self.receive_from_relay_node())
            except Exception as e:
                print(e)
                break
    
    def format_packet(self, packet):
        encoded = packet.encode()
        return str(len(encoded)) + '_' + encoded.decode()

    def send_to_relay_node_task(self, to_send, is_connected):
        print('Sending')
        while True:
            try:
                msg = to_send.get()
                if is_connected.value:
                    self.relay_server.send_to_relay_node(self.format_packet(msg).encode())
                    time.sleep(3)
            except Exception as e:
                print(e)
                break

    def relay_server_process_main(self, to_node, action):
        self.relay_server.start_connection()
        multiprocessing.set_forkserver_preload(['dill'])
        try:

            receive_from_relay_node_process = Process(target=self.receive_from_relay_node_task, args=(), daemon=True)
            receive_from_relay_node_process.start()
            
            send_to_relay_node_process = Process(target=self.send_to_relay_node_task, args=(to_node, self.client_connected), daemon=True)
            send_to_relay_node_process.start()
                
        except Exception as e:
            print('Exception raised:', e)
        
        try:
            self.processes.append(receive_from_relay_node_process)
            self.processes.append(send_to_relay_node_process)
            for p in self.processes:
                p.join()
        except KeyboardInterrupt:
            print('Relay Server Process terminated')
        
        self.close_instance()
        return True 
    
    def close_instance(self):
        self.relay_server.close_connection()

