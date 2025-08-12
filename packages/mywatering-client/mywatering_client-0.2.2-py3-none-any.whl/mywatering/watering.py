import requests
from requests.auth import HTTPBasicAuth
from mywatering.common import create_pid_file
import RPi.GPIO as GPIO
import time
import json


PID_FILE = "./watring_pid.txt"


def close_entry(server: str, item: dict, user: str, password: str) -> None:
    url = f"{server}/api/watering_queue/update/{item['id']}/"
    headers = {"Content-type": "application/json", "Accept": "*/*"}
    data = {"status": 1}
    r = requests.patch(
        url, data=json.dumps(data), headers=headers, auth=HTTPBasicAuth(user, password)
    )
    print(r.text)


def do_watering(server: str, client_no: int, user: str, password: str) -> None:
    url = f"{server}/api/watering_queue/{client_no}/"
    headers = {"Content-type": "application/json", "Accept": "*/*"}
    r = requests.get(url, headers=headers, auth=HTTPBasicAuth(user, password))
    if r.status_code == 200:
        for p in r.json():
            print(p)
            print(
                f"Watering plant {p['plant']['name']} {p['topping_in_seconds']} s pin {p['plant']['gpio_pin']}"
            )

            close_entry(server, p, user, password)

            pin_no = p["plant"]["gpio_pin"]
            time_in_sec = p["topping_in_seconds"]

            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)

            GPIO.setup(pin_no, GPIO.OUT, initial=GPIO.LOW)

            GPIO.output(pin_no, GPIO.HIGH)
            time.sleep(time_in_sec)
            GPIO.output(pin_no, GPIO.LOW)
            time.sleep(1)
    else:
        print(f"Status code = {r.status_code}")


def main(args) -> None:
    create_pid_file(PID_FILE)
    do_watering(args.server, args.client_number, args.user, args.password)
