from multiprocessing import Process
import time
from MQTTClient import MQTTClient


class MqttClientProcess:

    def __init__(self):
        # self.publish_client = None
        # self.subscribe_client = None
        self.gamestate_topic = 'gamestate'
        self.processes = []

    def publish_gamestate_to_viz_task(self, engine_to_viz):
        publish_client = MQTTClient()
        publish_client.start_client()
        try:
            publish_client.publish_to_topic(self.gamestate_topic, 'testing')
            print('Test MQTT publish to visualizer')
        except Exception as e:
            print(e)
            print('MQTT test failed')
        
        while True:
            try:
                msg = engine_to_viz.get()
                publish_client.publish_to_topic(self.gamestate_topic, msg)
                print('Published to MQTT broker:', msg)
            except Exception as e:
                print(e)
                print('Attempt MQTT re-publish')
                try:
                    publish_client.close_client()
                except:
                    print('Failed to close. Starting new without closing.')
                publish_client = MQTTClient()
                publish_client.start_client()
                time.sleep(5)
            except:
                break

        publish_client.close_client()
        print('MQTT client closed')

    def Mqtt_client_process_main(self, engine_to_viz):
        # self.publish_client.start_client()
        try:
            publish_gamestate_process = Process(target=self.publish_gamestate_to_viz_task, args=(engine_to_viz,), daemon=True)
            publish_gamestate_process.start()
        except Exception as e:
            print('HELLO')
            print(e)
        
        try:
            self.processes.append(publish_gamestate_process)
            for p in self.processes:
                p.join()
        except KeyboardInterrupt:
            print('MQTT client process terminated')

        return True
