from dataclasses import dataclass

@dataclass
class Measurement:
    value: float
    unit: str

@dataclass
class EnergyMeasurements:
    grid_bought: Measurement
    grid_sold: Measurement
    load_consumption: Measurement
    production: Measurement
    battery_charged: Measurement
    battery_discharged: Measurement

@dataclass
class BatteryMeasurements:
    temperature: Measurement
    voltage: Measurement
    current: Measurement
    power: Measurement
    soc: Measurement


@dataclass
class PhaseMeasurements:
    voltage: Measurement
    current: Measurement
    power: Measurement

    def __init__(self, voltage, power, current=None):
        self.voltage = voltage
        self.current = current
        self.power = power

@dataclass
class ACMeasurements:
    total_power: Measurement
    phases: list[PhaseMeasurements]
    frequency: Measurement

@dataclass
class PVStringMeasurements:
    voltage: Measurement
    current: Measurement
    power: Measurement

@dataclass
class InverterMeasurements:
    total: EnergyMeasurements
    daily: EnergyMeasurements
    grid: ACMeasurements
    load: ACMeasurements
    battery: BatteryMeasurements
    pv_strings: list[PVStringMeasurements]