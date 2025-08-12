import adafruit_dht
import board
import requests
from requests.auth import HTTPBasicAuth
import json
from retry import retry


@retry(tries=3, delay=2)
def upload_data(server: str, client_no: int, user: str, password: str) -> None:
    dht_device = adafruit_dht.DHT22(board.D17, use_pulseio=False)
    temperature = dht_device.temperature
    humidity = dht_device.humidity
    print(f"Temperature: {temperature}, Humidity:{humidity}")

    url = f"{server}/api/temperature/create/"
    data = {
        "client_station": client_no,
        "temperature": temperature,
        "humidity": humidity,
    }
    headers = {"Content-type": "application/json", "Accept": "*/*"}
    r = requests.post(
        url, data=json.dumps(data), headers=headers, auth=HTTPBasicAuth(user, password)
    )
    print(r.status_code)


def main(args):
    upload_data(args.server, args.client_number, args.user, args.password)
