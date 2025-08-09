from ..interfaces import ModbusTCP
from ..measurements import InverterMeasurements, EnergyMeasurements, BatteryMeasurements, PhaseMeasurements, ACMeasurements, PVStringMeasurements, Measurement
from ..helper import ModbusMapper
from ..inverters.base_inverter import BaseInverter


class DeyeSUN12KEU(BaseInverter):

    measurements: InverterMeasurements

    def __init__(self, adapter):
        self.adapter = adapter
        self.external_ct = False


    async def update_status(self):
        self.measurements = await self.get_measurements()


    async def get_measurements(self):
        print("Getting measurements")
        data = await self.adapter.read_registers(514, 125)
        data2 = await self.adapter.read_registers(514+125, 125)

        mapper = ModbusMapper(data+data2, 514)
        mapper.dump()

        # 514 daily battery charge uint16 0.1 scale 
        daily_battery_charge_value = round(mapper.get_uint16(514) * 0.1, 1)
        daily_battery_charge = Measurement(value=daily_battery_charge_value, unit="kWh")


        # 515 daily battery discharge uint16 0.1 scale
        daily_battery_discharge_value = round(mapper.get_uint16(515) * 0.1, 1)
        daily_battery_discharge = Measurement(value=daily_battery_discharge_value, unit="kWh")

        # 516-517 total battery charge uint32 word swap 0.1 scale
        total_battery_charge_value = round(mapper.get_uint32(516) * 0.1, 1)
        total_battery_charge = Measurement(value=total_battery_charge_value, unit="kWh")

        # 518-519 total battery discharge uint32 word swap 0.1 scale
        total_battery_discharge_value = round(mapper.get_uint32(518) * 0.1, 1)
        total_battery_discharge = Measurement(value=total_battery_discharge_value, unit="kWh")

        # 520 daily grid bought uint16 0.1 scale
        daily_grid_bought_value = round(mapper.get_uint16(520) * 0.1, 1)
        daily_grid_bought = Measurement(value=daily_grid_bought_value, unit="kWh")

        # 521 daily grid sold uint16 0.1 scale
        daily_grid_sold_value = round(mapper.get_uint16(521) * 0.1, 1)
        daily_grid_sold = Measurement(value=daily_grid_sold_value, unit="kWh")

        # 522-523 total grid bought uint32 word swap 0.1 scale
        total_grid_bought_value =  round(mapper.get_uint32(522) * 0.1, 1)
        total_grid_bought = Measurement(value=total_grid_bought_value, unit="kWh")

        # 524-525 total grid sold uint32 word swap 0.1 scale
        total_grid_sold_value = round(mapper.get_uint32(524) * 0.1, 1)
        total_grid_sold = Measurement(value=total_grid_sold_value, unit="kWh")

        # 526 daily consumption uint16 0.1 scale
        daily_consumption_value = round(mapper.get_uint16(526) * 0.1, 1)
        daily_consumption = Measurement(value=daily_consumption_value, unit="kWh")

        # 527-528 total consumption uint32 word swap 0.1 scale
        total_consumption_value = round(mapper.get_uint32(527) * 0.1, 1)
        total_consumption = Measurement(value=total_consumption_value, unit="kWh")

        # 529 daily production uint16 0.1 scale
        daily_production_value = round(mapper.get_uint16(529) * 0.1, 1)
        daily_production = Measurement(value=daily_production_value, unit="kWh")

        # 534-535 total production uint32 word swap 0.1 scale
        total_production_value = round(mapper.get_uint32(534) * 0.1, 1)
        total_production = Measurement(value=total_production_value, unit="kWh")

        # 540 dc temperature uint16 0.1 scale -100 offset
        dc_temperature_value = round(mapper.get_int16(540) * 0.1 - 100, 1)
        dc_temperature = Measurement(value=dc_temperature_value, unit="°C")

        # 541 heatsink temperature uint16 0.1 scale -100 offset
        heatsink_temperature_value = round(mapper.get_int16(541) * 0.1 - 100, 1)
        heatsink_temperature = Measurement(value=heatsink_temperature_value, unit="°C")

        # 586 battery temperature uint16 0.1 scale -100 offset
        battery_temperature_value = round(mapper.get_int16(586) * 0.1 - 100, 1)
        battery_temperature = Measurement(value=battery_temperature_value, unit="°C")

        # 587 battery voltage uint16 0.01 scale
        battery_voltage_value = round(mapper.get_uint16(587) * 0.01, 2)
        battery_voltage = Measurement(value=battery_voltage_value, unit="V")

        # 588 battery soc uint16
        battery_soc_value = mapper.get_uint16(588)
        battery_soc = Measurement(value=battery_soc_value, unit="%")

        # 590 battery power uint16 
        battery_power_value = mapper.get_int16(590)
        battery_power = Measurement(value=battery_power_value, unit="W")

        # 591 battery current uint16 0.01 scale
        battery_current_value = round(mapper.get_int16(591) * 0.01, 2)
        battery_current = Measurement(value=battery_current_value, unit="A")

        # 592 battery corrected ah uint16
        battery_corrected_ah_value = mapper.get_uint16(592)
        battery_corrected_ah = Measurement(value=battery_corrected_ah_value, unit="AH")

        # 598 grid L1 voltage uint16 0.1 scale
        grid_L1_voltage_value = round(mapper.get_uint16(598) * 0.1, 1)
        grid_L1_voltage = Measurement(value=grid_L1_voltage_value, unit="V")

        # 599 grid L2 voltage uint16 0.1 scale
        grid_L2_voltage_value = round(mapper.get_uint16(599) * 0.1, 1)
        grid_L2_voltage = Measurement(value=grid_L2_voltage_value, unit="V")

        # 600 grid L3 voltage uint16 0.1 scale
        grid_L3_voltage_value = round(mapper.get_uint16(600) * 0.1, 1)
        grid_L3_voltage = Measurement(value=grid_L3_voltage_value, unit="V")

        
        # 604 grid L1 power internal uint16
        grid_L1_internal_power_value =  mapper.get_int16(604)
        grid_L1_internal_power = Measurement(value=grid_L1_internal_power_value, unit="W")
        
        # 605 grid L2 power internal uint16
        grid_L2_internal_power_value =  mapper.get_int16(605)
        grid_L2_internal_power = Measurement(value=grid_L2_internal_power_value, unit="W")

        # 606 grid L3 power internal uint16
        grid_L3_internal_power_value =  mapper.get_int16(606)
        grid_L3_internal_power = Measurement(value=grid_L3_internal_power_value, unit="W")

        # 609 grid frequency uint16 0.01 scale
        grid_frequency_value = round(mapper.get_uint16(609) * 0.01, 2)
        grid_frequency = Measurement(value=grid_frequency_value, unit="Hz")
       
        # 616 grid L1 power external uint16
        grid_L1_external_power_value =  mapper.get_int16(616)
        grid_L1_external_power = Measurement(value=grid_L1_external_power_value, unit="W")

        # 617 grid L2 power external uint16
        grid_L2_external_power_value =  mapper.get_int16(617)
        grid_L2_external_power = Measurement(value=grid_L2_external_power_value, unit="W")

        # 618 grid L3 power external uint16
        grid_L3_external_power_value =  mapper.get_int16(618)
        grid_L3_external_power = Measurement(value=grid_L3_external_power_value, unit="W")

        # 625 grid total power uint16
        grid_total_power_value = mapper.get_int16(625)
        grid_total_power = Measurement(value=grid_total_power_value, unit="W")

        # 630 grid L1 current uint16 0.01 scale
        grid_L1_current_value = round(mapper.get_int16(610) * 0.01, 2)
        grid_L1_current = Measurement(value=grid_L1_current_value, unit="A")

        # 631 grid L2 current uint16 0.01 scale
        grid_L2_current_value = round(mapper.get_int16(611) * 0.01, 2)
        grid_L2_current = Measurement(value=grid_L2_current_value, unit="A")

        # 632 grid L3 current uint16 0.01 scale
        grid_L3_current_value = round(mapper.get_int16(612) * 0.01, 2)
        grid_L3_current = Measurement(value=grid_L3_current_value, unit="A")

        # 633 inverter L1 power uint16
        inverter_L1_power_value = mapper.get_int16(633)
        inverter_L1_power = Measurement(value=inverter_L1_power_value, unit="W")

        # 634 inverter L2 power uint16
        inverter_L2_power_value = mapper.get_int16(634)
        inverter_L2_power = Measurement(value=inverter_L2_power_value, unit="W")

        # 635 inverter L3 power uint16
        inverter_L3_power_value = mapper.get_int16(635)
        inverter_L3_power = Measurement(value=inverter_L3_power_value, unit="W")

        # 644 load L1 voltage uint16 0.1 scale
        load_L1_voltage_value = round(mapper.get_uint16(644) * 0.1, 1)
        load_L1_voltage = Measurement(value=load_L1_voltage_value, unit="V")

        # 645 load L2 voltage uint16 0.1 scale
        load_L2_voltage_value = round(mapper.get_uint16(645) * 0.1, 1)
        load_L2_voltage = Measurement(value=load_L2_voltage_value, unit="V")

        # 646 load L3 voltage uint16 0.1 scale
        load_L3_voltage_value = round(mapper.get_uint16(646) * 0.1, 1)
        load_L3_voltage = Measurement(value=load_L3_voltage_value, unit="V")

        # 650 load L1 power uint16
        load_L1_power_value = mapper.get_uint16(650)
        load_L1_power = Measurement(value=load_L1_power_value, unit="W")
       
        # 651 load L2 power uint16
        load_L2_power_value = mapper.get_uint16(651)
        load_L2_power = Measurement(value=load_L2_power_value, unit="W")

        # 652 load L3 power uint16
        load_L3_power_value = mapper.get_uint16(652)
        load_L3_power = Measurement(value=load_L3_power_value, unit="W")

        # 653 load total power uint16
        load_total_power_value = mapper.get_uint16(653)
        load_total_power = Measurement(value=load_total_power_value, unit="W")

        # 655 load frequency uint16 0.01 scale
        load_frequency_value = round(mapper.get_uint16(655) * 0.01, 2)
        load_frequency = Measurement(value=load_frequency_value, unit="Hz")

        # 672 pv1 power uint16
        pv1_power_value = mapper.get_uint16(672)
        pv1_power = Measurement(value=pv1_power_value, unit="W")

        # 673 pv2 power uint16
        pv2_power_value = mapper.get_uint16(673)
        pv2_power = Measurement(value=pv2_power_value, unit="W")

        # 676 pv1 voltage uint16 0.1 scale
        pv1_voltage_value = round(mapper.get_uint16(676) * 0.1, 1)
        pv1_voltage = Measurement(value=pv1_voltage_value, unit="V")

        # 677 pv1 current uint16 0.1 scale
        pv1_current_value = round(mapper.get_uint16(677) * 0.1, 1)
        pv1_current = Measurement(value=pv1_current_value, unit="A")

        # 678 pv2 voltage uint16 0.1 scale
        pv2_voltage_value = round(mapper.get_uint16(678) * 0.1, 1)
        pv2_voltage = Measurement(value=pv2_voltage_value, unit="V")

        # 679 pv2 current uint16 0.1 scale
        pv2_current_value = round(mapper.get_uint16(679) * 0.1, 1)
        pv2_current = Measurement(value=pv2_current_value, unit="A")


        battery_measurements = BatteryMeasurements(
            temperature=battery_temperature,
            voltage=battery_voltage,
            current=battery_current,
            power=battery_power,
            soc=battery_soc
        )

        grid_measurements = ACMeasurements(
            total_power=grid_total_power,
            phases=[
                PhaseMeasurements(
                    voltage=grid_L1_voltage,
                    current=grid_L1_current,
                    power=grid_L1_external_power if self.external_ct else grid_L1_internal_power
                ),
                PhaseMeasurements(
                    voltage=grid_L2_voltage,
                    current=grid_L2_current,
                    power=grid_L2_external_power if self.external_ct else grid_L2_internal_power
                ),
                PhaseMeasurements(
                    voltage=grid_L3_voltage,
                    current=grid_L3_current,
                    power=grid_L3_external_power if self.external_ct else grid_L3_internal_power
                )
            ],
            frequency=grid_frequency
        )

        load_measurements = ACMeasurements(
            total_power=load_total_power,
            phases=[
                PhaseMeasurements(
                    voltage=load_L1_voltage,
                    power=load_L1_power
                ),
                PhaseMeasurements(
                    voltage=load_L2_voltage,
                    power=load_L2_power
                ),
                PhaseMeasurements(
                    voltage=load_L3_voltage,
                    power=load_L3_power
                )
            ],
            frequency=load_frequency
        )

        total_measurements = EnergyMeasurements(
            grid_bought=total_grid_bought,
            grid_sold=total_grid_sold,
            load_consumption=total_consumption,
            production=total_production,
            battery_charged=total_battery_charge,
            battery_discharged=total_battery_discharge
        )

        daily_measurements = EnergyMeasurements(
            grid_bought=daily_grid_bought,
            grid_sold=daily_grid_sold,
            load_consumption=daily_consumption,
            production=daily_production,
            battery_charged=daily_battery_charge,
            battery_discharged=daily_battery_discharge
        )

        pv_measurements = [
            PVStringMeasurements(
                voltage=pv1_voltage,
                current=pv1_current,
                power=pv1_power
            ),
            PVStringMeasurements(
                voltage=pv2_voltage,
                current=pv2_current,
                power=pv2_power
            )
        ]

        print("\ntotal")
        print(total_measurements)
        print("\ndaily")
        print(daily_measurements)
        print("\ngrid")
        print(grid_measurements)

        print(f" l1 power {grid_measurements.phases[0].power} l2 power {grid_measurements.phases[1].power} l3 power {grid_measurements.phases[2].power}")
        
        print("\nload")
        print(load_measurements)
        print("\nbattery")
        print(battery_measurements)
        print("\npv")
        print(pv_measurements)

        return InverterMeasurements(
            total=total_measurements,
            daily=daily_measurements,
            grid=grid_measurements,
            load=load_measurements,
            battery=battery_measurements,
            pv_strings=pv_measurements
        )