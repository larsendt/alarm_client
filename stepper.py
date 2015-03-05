import subprocess

def run():
    s = subprocess.call(["./stepper_control", "180", "0", "30"])
