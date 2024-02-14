
import asyncio
import threading
from eval_client import Eval_client

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

    eval_client = Eval_client(EVAL_IP, EVAL_PORT, SECRET_KEY, DEFAULT_GAME_STATE)
    eval_client.main()

