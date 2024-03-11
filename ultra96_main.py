
import asyncio
import json
from multiprocessing import Array, Process, Queue, Value
import sys

import numpy as np
from EvalClient import EvalClient
from MockGameEngineProcess import MockGameEngineProcess
from RelayServerProcess import RelayServerProcess
from MQTTClientProcess import MqttClientProcess

# evaluation cleint parameters
EVAL_IP = '127.0.0.1'
# EVAL_PORT = 60650
GROUP_ID = 'B05'
SECRET_KEY = 1111111111111111

# gamestate at the beginning 
DEFAULT_GAME_STATE = {
    'p1': {
        'hp': 100,
        'bullets': 6,
        'bombs': 2,
        'sheild_hp': 0,
        'deaths': 0,
        'shields': 3,
    },
    'p2': {
        'hp': 100,
        'bullets': 6,
        'bombs': 2,
        'sheild_hp': 0,
        'deaths': 0,
        'shields': 3,
    },
}

DUMMY_HW_DATA = [
        [ 1.45194718e+00, -6.15968296e-01,  8.72134691e-01,
            7.34305300e-01, -7.67589348e-01, -8.96998862e-01],
        [ 1.45194718e+00, -1.42716447e+00,  7.59236996e-01,
            1.15187070e+00,  7.23870512e-01, -1.37709656e+00],
        [ 1.25160589e+00, -1.05401423e+00,  1.52411888e-01,
            1.06918449e+00,  9.96873762e-01, -1.37709656e+00],
        [ 2.70987964e-01, -3.72609444e-01, -3.13291103e-01,
            9.41020847e-01,  1.03193313e+00, -1.37709656e+00],
        [-3.93301598e-01,  2.92571421e-01, -6.94320822e-01,
            5.35858375e-01,  9.07788491e-01, -1.37709656e+00],
        [-7.93984190e-01,  1.62780033e-01, -1.00478948e+00,
            2.10281390e-01,  1.30321215e+00, -1.37709656e+00],
        [-1.26847673e+00, -5.67296526e-01, -1.25880930e+00,
            1.05373250e-01,  8.14105271e-01, -1.37709656e+00],
        [-2.75522004e+00, -8.75551073e-01, -1.16002381e+00,
            -1.58705861e-01,  4.22245027e-02, -1.11605218e+00],
        [-1.91167774e+00, -7.78207532e-01, -7.22545246e-01,
            6.16994227e-01,  1.30723535e+00,  1.03144021e+00],
        [-1.62698221e+00, -4.86176908e-01, -1.59750238e+00,
            4.92964900e-01, -4.99758792e-01,  1.40865983e+00],
        [-9.94325487e-01,  7.79289126e-01, -1.68217565e+00,
            3.63250894e-01, -1.06128337e+00,  1.40865983e+00],
        [-6.04187173e-01,  1.63915707e+00, -1.79507334e+00,
            -4.01596628e-01, -8.61847313e-01,  1.17071054e+00],
        [ 3.86975030e-01,  1.49314176e+00, -1.42815584e+00,
            -1.94472818e+00, -1.50326126e+00,  7.42051879e-01],
        [ 7.87657623e-01,  9.09080515e-01,  1.38299676e-01,
            -2.21862628e+00, -2.21421920e+00, -1.11766184e-01],
        [ 1.13561882e+00,  5.35930274e-01,  1.98699943e+00,
            -1.90596902e+00, -1.81707132e+00, -7.14687710e-01],
        [ 1.86633734e-01,  5.40797451e-04,  1.46484759e+00,
            -1.50339049e+00, -6.15857016e-01, -8.64455796e-01],
        [-3.40580204e-01,  2.60123574e-01,  1.09793008e+00,
            -7.51979479e-01, -3.24461968e-01, -2.20942920e-01],
        [ 5.55683491e-01,  5.68378121e-01,  7.31012573e-01,
            6.88311091e-01,  9.22157083e-01,  5.27897512e-01],
        [ 1.55000898e-01, -1.13513385e+00,  9.85032386e-01,
            1.15083713e+00,  8.99167336e-01,  1.40865983e+00],
        [ 1.55000898e-01, -2.20591280e+00,  7.45124784e-01,
            1.35031763e+00,  1.16929687e+00,  1.40865983e+00],
        [ 5.76772048e-01, -2.38437596e+00,  7.59236996e-01,
            1.24437591e+00, -1.82500278e-01,  1.40865983e+00],
        [ 1.45194718e+00, -5.99744373e-01, -7.50769669e-01,
            1.44488999e+00, -2.19180420e+00,  1.40865983e+00],
        [ 1.01963176e+00,  9.73976209e-01, -7.50769669e-01,
            2.08731023e-01,  2.84766337e-01,  1.60125879e-01],
        [ 4.18607867e-01,  1.10376760e+00,  1.80636311e-01,
            -2.95654910e-01,  1.91657861e-01, -3.58323646e-02],
        [ 1.97178013e-01,  1.10376760e+00,  5.33441607e-01,
            -1.53021183e-01, -2.06064769e-01, -1.10716408e-01],
        [ 1.02279504e-01,  8.76632668e-01,  5.61666031e-01,
            -2.43459235e-01,  5.37653558e-01, -6.66258029e-02],
        [-2.66770253e-01,  7.14393432e-01,  5.75778243e-01,
            -3.77307551e-01,  4.18106872e-01,  8.24424326e-02],
        [-4.53403987e-02,  4.06138885e-01,  6.04002666e-01,
            -5.30277056e-01, -1.38245014e-01,  1.25833187e-01],
        [-2.35137416e-01,  3.08795344e-01,  6.32227090e-01,
            -6.88414449e-01,  4.88225602e-01, -1.76362420e-02],
        [-3.19491646e-01,  3.73691038e-01,  3.78207277e-01,
            -1.13543682e+00,  3.45689168e-01,  1.25833187e-01]
]


if __name__ == '__main__':

    EVAL_PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8888
    try:
        processes = []

        '''
        Processes ran on ultra-96:
        - Relay Server (to communicate with relay node)
        - Mock Game Engine (placeholder of actual game engine)
        - Evaluation Client (to send data over to evaluation server)
        - MQTT client (to receive gamestate from game engine, and pubish gamestate to visualizer)
        '''

        # relay server
        relay_server_process_instance = RelayServerProcess()
        # to_node = json.dumps(DEFAULT_GAME_STATE)
        ai_to_engine_action = Queue()
        engine_to_eval_action = Queue() # action sent to eval client for processing
        relay_server_to_node_gamestate = Queue()
        # relay_server_to_node_gamestate.put(to_node)

        relay_node_to_server_data = Array('f', 30 * 6)
        relay_node_to_server_data_np = np.frombuffer(relay_node_to_server_data.get_obj(), dtype=np.float32).reshape((30, 6))
        np.copyto(relay_node_to_server_data_np, DUMMY_HW_DATA)

        relay_server_process = Process(target=relay_server_process_instance.relay_server_process_main, args=(relay_node_to_server_data_np, relay_server_to_node_gamestate, ai_to_engine_action))
        processes.append(relay_server_process)
        relay_server_process.start()

        # mock game engine 
        mock_game_engine_instance = MockGameEngineProcess()
        eval_to_engine_gamestate = Queue()
        engine_to_viz_gamestate = Queue()
        eval_client_to_engine = Queue()

        mock_game_engine_process = Process(target=mock_game_engine_instance.mock_game_engine_process_main, args=(ai_to_engine_action, engine_to_eval_action, eval_client_to_engine, engine_to_viz_gamestate, relay_server_to_node_gamestate))
        processes.append(mock_game_engine_process)
        mock_game_engine_process.start()

        # MQTT client 
        mqtt_client_process_instance = MqttClientProcess()

        mqtt_client_process = Process(target=mqtt_client_process_instance.Mqtt_client_process_main, args=(engine_to_viz_gamestate,))
        processes.append(mqtt_client_process)
        mqtt_client_process.start()

        # eval client
        eval_client_to_server = Queue() # action
        eval_client_instance = EvalClient(EVAL_IP, EVAL_PORT, SECRET_KEY, DEFAULT_GAME_STATE)
        eval_client_instance.initialize()

        eval_client_process = Process(target=eval_client_instance.eval_client_process_main, args=(engine_to_eval_action, eval_client_to_server, eval_client_to_engine))
        processes.append(eval_client_process)
        eval_client_process.start()

        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print('Terminating ultra96 main')
    finally:
        relay_server_process_instance.close_instance()

