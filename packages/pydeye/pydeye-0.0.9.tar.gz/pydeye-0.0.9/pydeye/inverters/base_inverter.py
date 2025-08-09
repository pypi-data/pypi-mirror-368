import re
from ..interfaces import ModbusTCP
from ..measurements import InverterMeasurements, EnergyMeasurements, BatteryMeasurements, PhaseMeasurements, ACMeasurements, PVStringMeasurements, Measurement
from ..helper import ModbusMapper
from ..exceptions import DeviceNotSupported


class BaseInverter:

    type: str
    serial_number: str
    main_version: str
    hmi_version: str
    protocol_version: str
    rated_power: int
    firmware: str
    adapter: ModbusTCP
    measurements: InverterMeasurements
    DEVICE_PARAMETERS = {}

    @staticmethod
    async def create_device(adapter):


        from .deye_SUN12KEU import DeyeSUN12KEU        
        return DeyeSUN12KEU(adapter)

        raise DeviceNotSupported(f"Unsupported device model: {type}")

    def __init__(self, adapter: ModbusTCP):
        self.adapter = adapter

    async def init(self):
        basic_info = await self.adapter.get_basic_info()
        self.type = basic_info.type
        self.serial_number = basic_info.serial_number
        self.main_version = basic_info.main_version
        self.hmi_version = basic_info.hmi_version
        self.protocol_version = basic_info.protocol_version
        self.rated_power = basic_info.rated_power

        print(f"Inverter {self.type} {self.rated_power}W {self.serial_number} initialized")


    async def update_status(self):
        """
        Updates the status of the device.

        This method needs to be re-defined in all sub-classes.
        """
        raise NotImplementedError