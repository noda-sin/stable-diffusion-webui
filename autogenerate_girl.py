import subprocess
import time
import requests
import sys

from drawer import Drawer


def is_launched():
    try:
        r = requests.get('http://127.0.0.1:7860/robots.txt')
        return r.status_code == 200
    except:
        return False


def wait_for_launch():
    while not is_launched():
        time.sleep(1)


if __name__ == "__main__":
    proc = subprocess.Popen(" ".join(["./webui.sh",  "--api"] + ([f"'{arg}'" for arg in sys.argv[1:]])), shell=True)
    try:
        wait_for_launch()
        drawer = Drawer()
        drawer.start()
    finally:
        proc.kill()
