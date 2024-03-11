import paho.mqtt.client as mqtt
import sys
import json

jsonToSend = {
    "player_id":1,
    "action":"hulk",
    "game_state":{
        "p1":{
            "hp":95,
            "bullets":2,
            "bombs":1,
            "shield_hp":15,
            "deaths":4,
            "shields":2
            },
        "p2":{
            "hp":85,
            "bullets":6,
            "bombs":1,
            "shield_hp":25,
            "deaths":11,
            "shields":2
        }
    }
}


def on_message(client, userdata, message):
    # Convert the received message payload from bytes to string
    payload_str = message.payload.decode("utf-8")

    # Decode the JSON payload into a Python dictionary
    data = json.loads(payload_str)

    # Append the received data to a local file
    with open("mqtt_data.txt", "w") as file:
        file.write(json.dumps(data) + "\n")




# def onMessage(client, usrData, msg):
#     print(msg.topic + ": " + msg.payload.decode())

client = mqtt.Client(1, "pythontest1")

if client.connect("172.25.99.243", 1883, 60) != 0:
    print("FAILED TO CONNECT!")
    sys.exit(-1)
print("sending now...")
dataOut = json.dumps(jsonToSend)
# data_to_send = json.loads(dataOut)

client.publish("Overlay", dataOut, 0)
client.subscribe("PlayerAction")
client.on_message = on_message
client.loop_forever()
# client.disconnect()
