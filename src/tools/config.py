import os
from dataclasses import dataclass

import tomli

PROJECT_PATH = "/".join(os.path.abspath(__file__).split("/")[:-2])
CONFIG_FILE = f"{PROJECT_PATH}/config/credentials.toml"
POT_FILE = f"{PROJECT_PATH}/config/potenciostato.toml"
SIGNAL_FILE = f"{PROJECT_PATH}/config/signal.toml"


with open(CONFIG_FILE, mode="rb") as f_data:
    config = tomli.load(f_data)

with open(POT_FILE, mode="rb") as f_data:
    potenciostato = tomli.load(f_data)

with open(SIGNAL_FILE, mode="rb") as f_data:
    triangular = tomli.load(f_data)["triangular"]
    square = tomli.load(f_data)["square"]


@dataclass
class Credentials:
    channel: int = config["credentials"]["channel"]
    k_write: int = config["credentials"]["key"]["write"]
    k_read: int = config["credentials"]["key"]["read"]


@dataclass
class Potenciostato:
    enable: int = potenciostato["enable"]
    signal: str = potenciostato["signal"]
    period: int = potenciostato["sender_period"]


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
