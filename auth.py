import hmac
import hashlib
import time

with open("password.txt", "r") as f:
    PASSWORD = f.read().rstrip("\n")

def make_hmac(data):
    datastr = ""
    keys = sorted(data.keys())
    for key in keys:
        datastr += key + "=" + value + ","

    t = int(time.time())
    datastr += "hmac-timestamp=" + str(t)
    return "hmac-sha256=" + hmac.new(PASSWORD, datastr, digestmod=hashlib.sha256).hexdigest()

