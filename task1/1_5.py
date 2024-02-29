import argparse
import platform
import psutil
import os

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--distro", action="store_true")
parser.add_argument("-m", "--memory", action="store_true")
parser.add_argument("-c", "--cpu", action="store_true")
parser.add_argument("-u", "--user", action="store_true")
parser.add_argument("-l", "--load", action="store_true")
parser.add_argument("-i", "--ip", action="store_true")
args = parser.parse_args()

if args.distro:
    print(platform.platform())
if args.memory:
    memory = psutil.virtual_memory()
    print(f"Total: {memory.total}, Used: {memory.used}, Free: {memory.free}")
if args.cpu:
    cpu_info = platform.processor()
    print(f"CPU Model: {cpu_info}, Cores: {psutil.cpu_count(logical=False)}, Speed: {psutil.cpu_freq().current} MHz")
if args.user:
    print(platform.node())
if args.load:
    print(psutil.getloadavg())
if args.ip:
    print(os.system('ipconfig getifaddr en0'))
