from multiprocessing import Process


class MockGameEngineProcess:

    def __init__(self):
        self.name = 'mock'
        self.processes = []

    # send ai action to eval client
    def send_to_eval_task(self, identified_action, engine_to_eval):
        while True:
            try:
                action = identified_action.get()
                print('Action at engine: ', action)
                engine_to_eval.put(action)
            except Exception as e:
                print(e)

    # receive actual gamestate from eval client
    def receive_from_eval_task(self, eval_to_engine_gamestate, engine_to_viz_gamestate, relay_server_to_node_gamestate):
        while True:
            try:
                gamestate = eval_to_engine_gamestate.get()
                engine_to_viz_gamestate.put(gamestate)
                relay_server_to_node_gamestate.put(gamestate)
                print('Gamestate eval server - eval cleint - game engine:', gamestate)
            except Exception as e:
                print(e)

    def mock_game_engine_process_main(self, identified_action, engine_to_eval, eval_to_engine_gamestate, engine_to_viz_gamestate, relay_server_to_node_gamestate):
        try:
            send_to_eval_process = Process(target=self.send_to_eval_task, args=(identified_action, engine_to_eval), daemon=False)
            send_to_eval_process.start()

            receive_from_eval_process = Process(target=self.receive_from_eval_task, args=(eval_to_engine_gamestate, engine_to_viz_gamestate, relay_server_to_node_gamestate), daemon=False)
            receive_from_eval_process.start()
        except Exception as e:
            print('Exception raised here is', e)
        try:
            self.processes.append(send_to_eval_process)
            self.processes.append(receive_from_eval_process)
            for p in self.processes:
                p.join()
        # except Exception as e:
        #     print(e)
        except KeyboardInterrupt:
            print('Mock game engine terminated')
        
        

    