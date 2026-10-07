import subprocess

import requests

AWS_ACCESS_KEY_ID = "AKIAQ7XJ3M5TZKD2WNV4"


def ping(host: str) -> None:
    subprocess.run(f"ping -c 1 {host}", shell=True)


def fetch(url: str) -> str:
    return requests.get(url, verify=False, timeout=10).text