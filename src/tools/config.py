import os
from dataclasses import dataclass

import tomli

PROJECT_PATH = "/".join(os.path.abspath(__file__).split("/")[:-2])
API_FILE = f"{PROJECT_PATH}/config/api.toml"
DEVICE_FILE = f"{PROJECT_PATH}/config/device.toml"
SIGNAL_FILE = f"{PROJECT_PATH}/config/signal.toml"


with open(API_FILE, mode="rb") as f_data:
    api = tomli.load(f_data)

with open(DEVICE_FILE, mode="rb") as f_data:
    device = tomli.load(f_data)

with open(SIGNAL_FILE, mode="rb") as f_data:
    triangular = tomli.load(f_data)["triangular"]
    square = tomli.load(f_data)["square"]


@dataclass
class Api:
    delay: int = api["settings"]["delay"]
    channel: int = api["credentials"]["channel"]
    k_write: int = api["credentials"]["write_key"]
    k_read: int = api["credentials"]["read_key"]


@dataclass
class Potenciostato:
    enable: int = device["potenciostato"]["enable"]
    signal: str = device["potenciostato"]["signal"]


@dataclass
class Triangular:
    steps: int = triangular["steps"]
    scan_rate: int = triangular["scan_rate"]
    loops: int = triangular["loops"]
    init: int = triangular["init"]
    max: int = triangular["max"]
    min: int = triangular["min"]


@dataclass
class Square:
    freq_sample: int = square["freq_sample"]
    freq_signal: int = square["freq_signal"]
    amp_signal: int = square["amp_signal"]
    offset: int = square["offset"]
    duty_cycle: int = square["duty_cycle"]
    initial: int = square["initial_value"]
    final: int = square["final_value"]
