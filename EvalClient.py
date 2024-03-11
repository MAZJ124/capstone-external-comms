import asyncio
import base64
import json
from random import random
import socket
import sys
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes

from GameState import Player
from Helper import Action, ice_print_group_name

class EvalClient:

    def __init__(self, ip_addr, port_num, secret_key, default_gamestate):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_addr = (ip_addr, port_num)
        self.secret_key = secret_key
        self.predicted_gamestate = default_gamestate
        self.p1 = Player()
        self.p2 = Player()
        self.timeout = 60
        self.is_running = True
    
    def _encrypt_message(self, message):
        try:
            # Convert secret key to bytes
            secret_key_bytes = bytes(str(self.secret_key), encoding="utf8")
            
            # Generate a random IV (Initialization Vector)
            iv = get_random_bytes(AES.block_size)
            
            # Create an AES cipher object with CBC mode
            cipher = AES.new(secret_key_bytes, AES.MODE_CBC, iv)
            
            # Pad the message to the appropriate block size
            padded_message = pad(message.encode('utf-8'), AES.block_size)
            
            # Encrypt the padded message
            cipher_text = cipher.encrypt(padded_message)
            
            # Combine the IV and cipher text
            encrypted_message = iv + cipher_text
            
            # Encode the encrypted message in base64
            encoded_message = base64.b64encode(encrypted_message)
            
            return encoded_message.decode('utf-8')
        except Exception as e:
            print("Exception in encrypt_message:", e)
            return None

    def send_data(self, data=None, isHelloPacket=False):
        # Hello packet will be passed in as string
        # Gamestate will be passed in as JSON
        message = 'hello' if isHelloPacket else json.dumps(data)
        # actual content of gamestate
        cipher_string = self._encrypt_message(message)
        # length of packet + '_'
        string_padding = str(len(cipher_string)) + '_'
        try:
            self.socket.sendall(string_padding.encode('utf8'))
            self.socket.sendall(cipher_string.encode('utf-8'))
        except OSError:
            print('Error while sending data')
            return False 
        return True 
    
    async def recv_text(self, timeout):
        text_received   = ""
        success         = False

        if self.is_running:
            loop = asyncio.get_event_loop()
            try:
                while True:
                    # recv length followed by '_' followed by cypher
                    data = b''
                    while not data.endswith(b'_'):
                        start_time = time.perf_counter()
                        task = loop.sock_recv(self.socket, 1)
                        _d = await asyncio.wait_for(task, timeout=timeout)
                        timeout -= (time.perf_counter() - start_time)
                        if not _d:
                            data = b''
                            break
                        data += _d
                    if len(data) == 0:
                        ice_print_group_name(self.group_name, 'recv_text: client disconnected')
                        self.stop()
                        break
                    data = data.decode("utf-8")
                    length = int(data[:-1])

                    data = b''
                    while len(data) < length:
                        start_time = time.perf_counter()
                        task = loop.sock_recv(self.socket, length - len(data))
                        _d = await asyncio.wait_for(task, timeout=timeout)
                        timeout -= (time.perf_counter() - start_time)
                        if not _d:
                            data = b''
                            break
                        data += _d
                    if len(data) == 0:
                        ice_print_group_name(self.group_name, 'recv_text: client disconnected')
                        self.stop()
                        break
                    msg = data.decode("utf8")  # Decode raw bytes to UTF-8
                    text_received = msg
                    success = True
                    break
            except ConnectionResetError:
                ice_print_group_name(self.group_name, 'recv_text: Connection Reset')
                self.stop()
            except asyncio.TimeoutError:
                ice_print_group_name(self.group_name, 'recv_text: Timeout while receiving data')
                timeout = -1
        else:
            timeout = -1

        return success, timeout, text_received

    
    # def receive_data(self):
    #     self.socket.setblocking(False)
    #     try:
    #         data = b''
    #         # process front padding: length of data and '_'
    #         while not data.endswith(b'_'):
    #             _d = self.socket.recv(1)
    #             if not _d:
    #                 data = b''
    #                 break
    #             data += _d
    #         if len(data) == 0:
    #             self.stop()
            
    #         data = data.decode('utf8')
    #         length = int(data[:-1])
    #         self.socket.setblocking(True)

    #         data = b''
    #         # process actual gametstate data 
    #         while len(data) < length:
    #             _d = self.socket.recv(length - len(data))
    #             if not _d:
    #                 data = b''
    #                 break
    #             data += _d
    #         if len(data) == 0:
    #             self.stop()
    #         data_string = data.decode('utf8')
    #         self.socket.setblocking(False)
    #         return data_string
    #     except ConnectionResetError:
    #         print('Connection reset')
    #         sys.exit()
    #     except BlockingIOError:
    #         # placeholder to be changed in future
    #         return 'NIL'
    
    async def send_data_with_response(self, data):
        self.send_data(data)
        _, _, response = await self.recv_text(self.timeout)
        return response
    
    def handle_action(self, action):
        # Not compatible with Python version on FPGA
        # match action:
        #     case Action.shoot:
        #         self.p1.shoot(self.p2, True)
        #     case Action.shield:
        #         self.p1.shield()
        #     case Action.reload:
        #         self.p1.reload()
        #     case Action.bomb:
        #         self.p1.bomb(self.p2, 0, True)
        #     case Action.ironMan | Action.hulk | Action.captAmerica | Action.shangChi:
        #         self.p1.harm_AI(self.p2, True)
        if action == Action.shoot:
            self.p1.shoot(self.p2, True)
        elif action == Action.shield:
            self.p1.shield()
        elif action == Action.reload:
            self.p1.reload()
        elif action == Action.bomb:
            self.p1.bomb(self.p2, 0, True)
        else:
            self.p1.harm_AI(self.p2, True)

    def generate_dummy_data(self):
        player_id = 1 # fixed value at this stage since only consider one player game
        dummy_action = Action.get_random_action()
        self.handle_action(dummy_action)
        p1_dict = self.p1.get_dict()
        p2_dict = self.p2.get_dict()
        gamestate = {
            'p1': p1_dict,
            'p2': p2_dict,
        }
        self.predicted_gamestate = gamestate
        dummy_data = {
            'player_id': player_id,
            'action': dummy_action,
            'game_state': gamestate,
        }
        return dummy_data
    
    def generate_data_from_input_action(self, action):
        player_id = 1 # fixed value at this stage since only consider one player game
        self.handle_action(action)
        p1_dict = self.p1.get_dict()
        p2_dict = self.p2.get_dict()
        gamestate = {
            'p1': p1_dict,
            'p2': p2_dict,
        }
        self.predicted_gamestate = gamestate
        dummy_data = {
            'player_id': player_id,
            'action': action,
            'game_state': gamestate,
        }
        return dummy_data
    
    async def eval_client_task(self, engine_to_eval_action, eval_client_to_server, eval_client_to_engine):
        while True:
            try:
                action = engine_to_eval_action.get()
                print('Action being sent to eval server:', action)
                eval_client_to_server.put(action)
                to_send = self.generate_data_from_input_action(action)
                # print('Data being sent to eval server:', to_send)
                time.sleep(0.02)
                response = await self.send_data_with_response(to_send)
                if response:
                    print('Response from eval server:', response)
                    eval_client_to_engine.put(response)
            except Exception as e:
                print(e)

    def initialize(self):
        self.socket.connect(self.server_addr)
        print('Evaluation client connected to Evaluation Server...')
        self.send_data(isHelloPacket=True)

    def eval_client_process_main(self, engine_to_eval_action, eval_client_to_server, eval_client_to_engine):
        while self.is_running:
            try:
                '''
                One single process for sending and receiving data to and from evaluation server 
                One receive happens after one send, thus no point using multiple processes for the process
                '''
                print('running')
                asyncio.run(self.eval_client_task(engine_to_eval_action, eval_client_to_server, eval_client_to_engine))
            except Exception as e:
                print(e)
            except:
                break

    # def test_main(self):
    #     self.socket.connect(self.server_addr)
    #     print('Evaluation client connected to Evaluation Server')
    #     self.send_data(isHelloPacket=True)        
    #     while True:
    #         try:
    #             # get input from terminal to input action 
    #             input_action = input('Choose an action to perform: ')
    #             if input_action not in Action.all:
    #                 print('Enter valid action')
    #                 continue
    #             to_send = self.generate_data_from_input_action(input_action)
    #             response = self.send_data_with_response(to_send)
    #             print(response + '\n')
    #         except Exception as e:
    #             print(e)


        
