import paho.mqtt.client as mqtt
import ssl
import time
import RPi.GPIO as GPIO
import json

# AWS IoT Core endpoint
iot_endpoint = "a3cax1pao8cxta-ats.iot.ap-southeast-2.amazonaws.com"  # Replace with your AWS IoT endpoint

# Path to the certificate, private key, and root CA certificate
cert_path = "/home/pi/Desktop/IoT/AWSIoT_Certs/raspberrypizero-certs/certificate.pem.crt"
private_key_path = "/home/pi/Desktop/IoT/AWSIoT_Certs/raspberrypizero-certs/private.pem.key"
root_ca_path = "/home/pi/Desktop/IoT/AWSIoT_Certs/raspberrypizero-certs/rootCA.pem"

# Device name
device_name = "AutomateDry"

# Set up the MQTT client
client = mqtt.Client(client_id=device_name)

# Configure TLS/SSL context
client.tls_set(certfile=cert_path, keyfile=private_key_path, ca_certs=root_ca_path, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)

# GPIO pin numbers for relays
RELAY_PIN_2 = 2
RELAY_PIN_3 = 3

# Set up GPIO mode and initialize the relays
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN_2, GPIO.OUT, initial=GPIO.HIGH)  # Relay OFF initially (active low)
GPIO.setup(RELAY_PIN_3, GPIO.OUT, initial=GPIO.HIGH)

# Callback function when the connection to the broker is established
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker.")
        # Subscribe to the topic when the connection is established
        client.subscribe("automate-dry/processing/")  # Subscribe to the topic
        print("Subscribed to topic: automate-dry/processing/")
    else:
        print(f"Connection failed with result code {rc}")

# Callback function when a message is received
def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    payload = json.loads(payload)
    print("Received message: {}".format(payload))

    if payload["message"] == "start":
        turn_on_relay_2()
        time.sleep(2)  # Wait for 2 seconds with relay 2 ON and relay 3 OFF
        turn_on_relay_3()
        time.sleep(2)  # Wait for 2 seconds with relay 3 ON and relay 2 OFF

    elif payload["message"] == "stop":
        turn_off_relay_2_and_3()

def turn_on_relay_2():
    GPIO.output(RELAY_PIN_2, GPIO.LOW)  # Relay ON (active low)
    print("Relay 2 turned ON.")

def turn_on_relay_3():
    GPIO.output(RELAY_PIN_3, GPIO.LOW)  # Relay ON (active low)
    print("Relay 3 turned ON.")

def turn_off_relay_2_and_3():
    GPIO.output(RELAY_PIN_2, GPIO.HIGH)  # Relay OFF (active low)
    GPIO.output(RELAY_PIN_3, GPIO.HIGH)  # Relay OFF (active low)
    print("Relay 2 and Relay 3 turned OFF.")

# Assign the callback functions to the client
client.on_connect = on_connect
client.on_message = on_message

# Connect to the AWS IoT Core endpoint
client.connect(iot_endpoint, port=8883)

# Loop to maintain the connection and handle MQTT messages
client.loop_forever()