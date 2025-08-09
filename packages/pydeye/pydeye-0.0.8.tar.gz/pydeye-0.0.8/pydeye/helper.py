from enum import Enum
import struct

class InverterType(Enum):
    UNDEFINED = (0, "Undefined")
    SINGLE_PHASE_HYBRID_INVERTER = (3, "Single phase hybrid inverter")
    MICRO_INVERTER = (4, "Micro inverter")
    LOW_VOLTAGE_THREE_PHASE_HYBRID_INVERTER = (5, "Low voltage three phase hybrid inverter")
    HIGH_VOLTAGE_THREE_PHASE_HYBRID_INVERTER = (6, "High voltage three phase hybrid inverter")
    HIGH_VOLTAGE_THREE_PHASE_INVERTER_6_12KW = (7, "High voltage three phase inverter 6-12kW")
    HIGH_VOLTAGE_THREE_PHASE_INVERTER_20_50WK = (262, "High voltage three phase inverter 20-50kW")
    THREE_PHASE_POWER_CONVERSION_SYSTEM = (8, "Three phase power conversion system")
    BALCONY_ENERGY_STORAGE_SYSTEM = (9, "Balcony energy storage system")

class BasicInfo:
    def __init__(self, type: InverterType, serial_number, main_version, hmi_version, protocol_version, rated_power) -> None:
        self.type = type
        self.serial_number = serial_number
        self.main_version = main_version
        self.hmi_version = hmi_version
        self.protocol_version = protocol_version
        self.rated_power = rated_power


class ModbusMapper:
    def __init__(self, register_values, start_address):
        self.register_values = register_values
        self.start_address = start_address

    def get_value(self, desired_address):
        if desired_address < self.start_address or desired_address >= self.start_address + len(self.register_values):
            return None  # Desired address is out of range

        index = desired_address - self.start_address
        return self.register_values[index]
    
    def get_uint16(self, desired_address):
        value = self.get_value(desired_address)
        return value

    def get_int16(self, desired_address):
        value = self.get_value(desired_address)
        if value is None:
            return None
        if value > 32767:
            value -= 65536
        return value        
    
    def get_uint32(self, desired_address, word_swap=True):
        high_word = self.get_value(desired_address)
        low_word = self.get_value(desired_address + 1)
        if word_swap:
            return (low_word << 16) + high_word
        return (high_word << 16) + low_word
    
    def get_string(self, desired_address):
        value = self.get_value(desired_address)
        high_byte = (value >> 8) & 0xFF
        low_byte = value & 0xFF
        return "".join([chr(high_byte), chr(low_byte)])
    
    def dump(self):
        for i, value in enumerate(self.register_values):
            print(f"Address {self.start_address + i}: {value} 0x{value:04X}")