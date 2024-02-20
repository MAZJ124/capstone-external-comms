from multiprocessing import Process
import time
import certifi
import paho.mqtt.client as paho
from paho import mqtt

class MQTTClient:

    def __init__(self):
        self.client = None
        self.gamestate_topic = 'gamestate'
        self.hostname = None
        self.port = None 
        self.username = None 
        self.password = None 


    # setting callbacks for different events to see if it works, print the message etc.
    def on_connect(self, client, userdata, flags, rc, properties=None):
        print("CONNACK received with code %s." % rc)

    # with this callback you can see if your publish was successful
    def on_publish(self, client, userdata, mid, properties=None):
        print("mid: " + str(mid))

    # print which topic was subscribed to
    def on_subscribe(csefl, lient, userdata, mid, granted_qos, properties=None):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    # print message, useful for checking if it was successful
    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    def start_client(self):
        # self.client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5, callback_api_version=paho.CallbackAPIVersion.VERSION2)
        self.client = paho.Client()
        # self.client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message

        # move to credentials file later on 
        username, password = 'capstone-visualizer', 'capstoneVisualizer'
        hostname = '3d839f6faa9b4f6c93480ac499f5544a.s1.eu.hivemq.cloud'
        port = 8883

        self.username = username
        self.password = password
        self.port = port
        self.hostname = hostname

        # self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        self.client.tls_set(certifi.where())
        self.client.username_pw_set(username, password)
        self.client.connect(host=hostname, port=port)

    def subscribe_to_topic(self, topic):
        self.client.subscribe(topic, qos=0)
        self.client.loop_forever()

    def publish_to_topic(self, topic, msg):
        self.client.publish(topic, msg, qos=0)

    def close_client(self):
        self.client.loop_stop()
        self.client.disconnect()
        self.is_subscribed = False

    def publish_gamestate_to_viz_task(self, engine_to_viz):
        try:
            self.publish_client.publish_to_topic(self.gamestate_topic, 'testing')
            print('Test MQTT publish to visualizer')
        except Exception as e:
            print(e)
            print('MQTT test failed')
        
        while True:
            try:
                msg = engine_to_viz.get()
                self.publish_to_topic(self.gamestate_topic, msg)
            except Exception as e:
                print(e)
                print('Attempt MQTT re-publish')
                try:
                    self.close_client()
                except:
                    print('Failed to close. Starting new without closing.')
                # self.publish_client = MQTTClient()
                # self.publish_client.start_client()
                time.sleep(5)
            except:
                break

        self.close_client()
        print('MQTT client closed')

    def Mqtt_client_process_main(self, engine_to_viz):
        self.start_client()
        processes = []
        # try:
        publish_gamestate_process = Process(target=self.publish_gamestate_to_viz_task, args=(engine_to_viz,), daemon=True)
        publish_gamestate_process.start()
        # except Exception as e:
        #     print('HELLO')
        #     print(e)
        
        try:
            processes.append(publish_gamestate_process)
            for p in processes:
                p.join()
        except KeyboardInterrupt:
            print('MQTT client process terminated')

        return True
