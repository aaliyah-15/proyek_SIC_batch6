import network
import time
from machine import Pin, Timer
import dht
import ujson
from umqtt.simple import MQTTClient

# MQTT Server Parameters
MQTT_CLIENT_ID = "emqttx_1dehgjhdgc,uzkgsbawi.lhsawil>sh4d4f8"
MQTT_BROKER = "broker.emqx.io"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_TOPIC = "/UNI427/AALIYAH_BARAKATULLAH_ASURA/data_sensor"
MQTT_TOPIC_LED = "/UNI427/AALIYAH_BARAKATULLAH_ASURA/aktuasi_led"

# Initialize DHT sensors
sensor1 = dht.DHT22(Pin(15))
sensor2 = dht.DHT22(Pin(2))

# LED setup
led = Pin(32, Pin.OUT)  # Ganti GPIO sesuai dengan koneksi LED Anda

# Connect to WiFi
print("Connecting to WiFi", end="")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Wokwi-GUEST', '')
while not sta_if.isconnected():
    print(".", end="")
    time.sleep(0.1)
print(" Connected!")

# Connect to MQTT server
print("Connecting to MQTT server... ", end="")
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)
client.connect()
print("Connected!")


# Callback function for topic subscription
def sub_cb(topic, msg):
    print(f"Received message on topic {topic.decode()}: {msg.decode()}")
    if topic.decode() == MQTT_TOPIC_LED:
        if msg.decode().lower() == "on":
            led.value(1)  # Turn LED on
            print("LED turned ON")
        elif msg.decode().lower() == "off":
            led.value(0)  # Turn LED off
            print("LED turned OFF")
        else:
            print("Invalid command received!")

client.set_callback(sub_cb)
client.subscribe(MQTT_TOPIC_LED)
print(f"Subscribed to topic {MQTT_TOPIC_LED}")

# Publish sensor data
def publish_sensor_data():
    try:
        print("Reading sensor data...")
        sensor1.measure()
        sensor2.measure()
        message = ujson.dumps({
            "temp1": sensor1.temperature(),
            "humidity1": sensor1.humidity(),
            "temp2": sensor2.temperature(),
            "humidity2": sensor2.humidity(),
        })
        print(f"Publishing data to {MQTT_TOPIC}: {message}")
        client.publish(MQTT_TOPIC, message)
    except OSError as e:
        print(f"Error reading sensor: {e}")

# Timer for periodic sensor data publishing
tim = Timer(-1)
tim.init(period=5000, mode=Timer.PERIODIC, callback=lambda t: publish_sensor_data())

# Main loop
try:
    while True:
        client.check_msg()  # Check for incoming messages
        time.sleep(0.1)    # Short delay to avoid high CPU usage
except KeyboardInterrupt:
    print("Program stopped")
    tim.deinit()
    client.disconnect()
