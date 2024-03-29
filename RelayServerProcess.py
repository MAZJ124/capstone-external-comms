import asyncio
from multiprocessing import Process, Value, Queue
import multiprocessing
import time

import numpy as np
from Helper import Action

from RelayServer import RelayServer
from driver import Model

class RelayServerProcess:
    def __init__(self):
        self.relay_server = RelayServer()
        self.processes = []
        self.client_connected = Value('i', 1)
        self.client_socket_update = Queue()

    async def receive_from_relay_node(self, identified_action):
        try:
            action = await self.relay_server.receive_from_relay_node()
            if self.relay_server.is_running:
                print('Data received from relay node is: ' + action)
                identified_action.put(action)
        except Exception:
            self.relay_server.close_connection()
    
    def receive_from_relay_node_task(self, identified_action):
        while self.relay_server.is_running:
            try:
                asyncio.run(self.receive_from_relay_node(identified_action))
            except Exception as e:
                print(e)
                break
    
    def format_packet(self, packet):
        encoded = packet.encode()
        return str(len(encoded)) + '_' + encoded.decode()

    def send_to_relay_node_task(self, to_send, is_connected):
        while True:
            try:
                msg = to_send.get()
                if is_connected.value:
                    self.relay_server.send_to_relay_node(self.format_packet(msg).encode())
                    time.sleep(3)
            except Exception as e:
                print(e)
                break

    # def generate_random_ai_event_task(self, identified_action):
    #     while True:
    #         try:
    #             generated_action = Action.get_random_action()
    #             identified_action.put(generated_action)
    #             # print('action generated is:', generated_action)
    #             # engine_to_eval_action.put(generated_action)
    #             time.sleep(3)
    #         except Exception as e:
    #             print(e)

    def send_data_to_ai_task(self, from_node, identified_action):
        input_data = from_node
        print(f'Shape of input data is: {np.array(input_data).shape}')
        model = Model(r'/home/xilinx/fpga_deployment/week8.bit')
        predictions = model.get_prediction(input_data)
        predictions = np.array(predictions)
        predicted_action = model.get_action(np.argmax(predictions))
        print(f'Final predicted action is: {predicted_action}')
        identified_action.put(predicted_action)
        
    def relay_server_process_main(self, from_node, to_node, identified_action):
        # self.relay_server.start_connection()
        try:

            # receive_from_relay_node_process = Process(target=self.receive_from_relay_node_task, args=(identified_action,))
            # receive_from_relay_node_process.start()

            send_data_to_ai_process = Process(target=self.send_data_to_ai_task, args=(from_node, identified_action))
            send_data_to_ai_process.start()
            
            # send_to_relay_node_process = Process(target=self.send_to_relay_node_task, args=(to_node, self.client_connected))
            # send_to_relay_node_process.start()
                
        except Exception as e:
            print('Exception raised:', e)
        
        try:
            # self.processes.append(receive_from_relay_node_process)
            self.processes.append(send_data_to_ai_process)
            # self.processes.append(send_to_relay_node_process)
            for p in self.processes:
                p.join()
        except KeyboardInterrupt:
            print('Relay Server Process terminated')
        
        self.close_instance()
        return True 
    
    def close_instance(self):
        self.relay_server.close_connection()

