
import asyncio
import json
from multiprocessing import Array, Process, Queue, Value
from eval_client import Eval_client
from RelayServerProcess import RelayServerProcess

# evaluation cleint parameters
EVAL_IP = '127.0.0.1'
EVAL_PORT = 57791
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

    # eval_client = Eval_client(EVAL_IP, EVAL_PORT, SECRET_KEY, DEFAULT_GAME_STATE)
    # eval_client.main()

    try:
        processes = []

        relay_server_process_instance = RelayServerProcess()
        action = Value('i', 0)
        to_node = json.dumps(DEFAULT_GAME_STATE)
        q = Queue()
        q.put(to_node)
        relay_server_process = Process(target=relay_server_process_instance.relay_server_process_main, args=(q, action))
        processes.append(relay_server_process)
        relay_server_process.start()
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print('Terminating ultra96 main')
    finally:
        relay_server_process_instance.close_instance()

