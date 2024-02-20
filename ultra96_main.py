
import asyncio
import json
from multiprocessing import Array, Process, Queue, Value
import sys
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

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print('Wrong number of input, plaese specify eval client port number only')
        sys.exit(1)
    EVAL_PORT = int(sys.argv[1])
    try:
        processes = []

        # relay server
        relay_server_process_instance = RelayServerProcess()
        # to_node = json.dumps(DEFAULT_GAME_STATE)
        ai_to_engine_action = Queue()
        engine_to_eval_action = Queue() # action sent to eval client for processing
        relay_server_to_node_gamestate = Queue()
        # relay_server_to_node_gamestate.put(to_node)

        relay_server_process = Process(target=relay_server_process_instance.relay_server_process_main, args=(relay_server_to_node_gamestate, ai_to_engine_action))
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

