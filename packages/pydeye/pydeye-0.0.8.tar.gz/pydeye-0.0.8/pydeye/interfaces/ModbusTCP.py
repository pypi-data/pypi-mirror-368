from pymodbus.client import AsyncModbusTcpClient
from pydeye.helper import ModbusMapper, BasicInfo, InverterType

class ModbusTCP():
    def __init__(self, host, port=502, unit=1):
        self.client = AsyncModbusTcpClient(host=host, port=port, timeout=1)
        self.unit = unit

    async def connect(self):
        await self.client.connect()

    async def close(self):
        self.client.close()

    def connected(self):
        return self.client.connected

    async def read_registers(self, register_address, count):
        if not self.connected():
            await self.connect()

        print(self.connected())

        print(f"Reading {count} registers at address {register_address}")
        result = await self.client.read_holding_registers(register_address, count=count, slave=self.unit)
        return result.registers

    async def write_registers(self, register_address, values):
        if not self.connected():
            await self.connect()

        result = await self.client.write_registers(register_address, values=values, slave=self.unit)
        return result
    
    async def get_basic_info(self) -> BasicInfo:
        data = await self.read_registers(0, 24)
        mapper = ModbusMapper(data, 0)
        mapper.dump()

        protocol_version = f"{mapper.get_value(2):04X}"
        serial_number = "".join([mapper.get_string(register) for register in range(3, 8)])
        type = InverterType.UNDEFINED
        for inverter_type in InverterType:
            if inverter_type.value[0] == mapper.get_value(0):
                type = inverter_type
                break

        rated_power = mapper.get_uint32(20)/10
        main_version = f"{mapper.get_value(14):04X}-{mapper.get_value(15):04X}-{mapper.get_value(11):04X}"
        hmi_version= f"{mapper.get_value(17):04X}-{mapper.get_value(18):04X}"

        #data = await self.read_registers(10056, 1)
        #mapper = ModbusMapper(data, 10056)
        # mapper.dump()

        return BasicInfo(type, serial_number, main_version, hmi_version, protocol_version, rated_power)
        
        
    

    


    