# this file is not run with tox but inside .gitlab-ci.yml itself
# See the job named : test-instance-creation-with-cubicweb_web

import os
import requests

from time import sleep


def run_test_instance():
    url = os.getenv("CW_BASE_URL", "http://localhost:8080")

    print(f"Trying to request {url} to see if the instance is running...")
    for _ in range(3):
        try:
            resp = requests.get(url, timeout=30)

            if resp.ok:
                break
        except requests.exceptions.ConnectionError as e:
            print(f"Warning: except {e} why trying to connect to url")
            sleep(1)
            resp = None
            continue

        sleep(1)

    if resp is None:
        print("Impossible to connect to the instance")
        print("\033[91mHere is the server log:\033[0m")
        with open("/tmp/cubicweb.log") as f:
            print(f.read())

        print("\033[91mAbort\033[0m")

        exit(1)

    if resp.status_code != 200:
        print(
            f"\033[93mDoing a GET on {url} result in a {resp.status_code} HTTP answer"
        )
        print("With the following content:\033[0m")
        print(resp.content.decode())
        print()
        print("\033[91mHere is the server log:\033[0m")
        with open("/tmp/cubicweb.log") as f:
            print(f.read())
        print("\033[91mAbort\033[0m")
        exit(1)
    print("Success")


if __name__ == "__main__":
    run_test_instance()
