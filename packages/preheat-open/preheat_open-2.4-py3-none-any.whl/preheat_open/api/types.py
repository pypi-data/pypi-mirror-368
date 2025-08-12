from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache
from typing import ClassVar, Type

import yaml

from ..query import Query
from ..unit import Component, Device, Unit
from ..zone import Zone


class ControlSettingDataType(Enum):
    ENUM = "ENUM"
    INT = "INT"
    DECIMAL = "DECIMAL"
    BOOL = "BOOL"


class ControlSettingUiType(Enum):
    SELECT = "SELECT"
    NUMBER = "NUMBER"
    RANGE = "RANGE"
    CHECKBOX = "CHECKBOX"


class __ControlSettingTypeEnum(Enum):
    def __init__(
        self,
        id: int,
        key: str,
        default_value: int | float | bool,
        min: int | float,
        max: int | float,
        step: int | float,
        type: ControlSettingDataType,
        ui_type: ControlSettingUiType,
        unit,
        show_in_ui,
        description,
        ui_order,
        ui_advanced,
    ):
        self.key = key
        self.id = id
        self.default_value = default_value
        self.min = min
        self.max = max
        self.step = step
        self.type = (
            type
            if isinstance(type, ControlSettingDataType)
            else ControlSettingDataType(type)
        )
        self.ui_type = (
            ui_type
            if isinstance(ui_type, ControlSettingUiType)
            else ControlSettingUiType(ui_type)
        )
        self.unit = unit
        self.show_in_ui = show_in_ui
        self.description = description
        self.ui_order = ui_order
        self.ui_advanced = ui_advanced

    @classmethod
    def from_key(self, key: str) -> __ControlSettingTypeEnum:
        lookup = {setting.key: setting for setting in self.__members__.values()}
        return lookup[key] if key in lookup else None

    @classmethod
    def contains(cls, value: __ControlSettingTypeEnum) -> bool:
        try:
            cls.from_key(value)
        except:
            return False
        return True


@lru_cache(maxsize=1)
def control_setting_types() -> dict:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(
        file=dir_path + "/control_setting_type.yaml", mode="r", encoding="utf8"
    ) as file:
        return yaml.safe_load(file)


ControlSettingType = __ControlSettingTypeEnum(
    "ControlSettingType",
    {setting["key"]: tuple(setting.values()) for setting in control_setting_types()},
)


class RelatedUnitType(Enum):
    COOLING_COIL = "coolingCoilIds"
    HEATING_COIL = "heatingCoilIds"
    HEATING_SECONDARY = "heatingSecondaryId"
    COOLING_SECONDARY = "coolingSecondaryId"
    ELECTRICITY = "electricityId"
    HEATING = "heatingId"
    COOLING = "coolingId"
    MAIN = "mainId"
    HOT_WATER = "hotWaterId"
    COLD_WATER = "coldWaterId"

    @property
    def unittype(self) -> UnitType:
        lookup = {
            RelatedUnitType.COOLING_COIL: UnitType.COOLING_COIL,
            RelatedUnitType.HEATING_SECONDARY: UnitType.SECONDARY,
            RelatedUnitType.HEATING_COIL: UnitType.HEATING_COIL,
            RelatedUnitType.COOLING_SECONDARY: UnitType.SECONDARY,
            RelatedUnitType.ELECTRICITY: UnitType.ELECTRICITY,
            RelatedUnitType.HEATING: UnitType.HEATING,
            RelatedUnitType.COOLING: UnitType.COOLING,
            RelatedUnitType.MAIN: UnitType.MAIN,
            RelatedUnitType.HOT_WATER: UnitType.HOT_WATER,
            RelatedUnitType.COLD_WATER: UnitType.COLD_WATER,
        }
        return lookup[self] if self in lookup else []


class UnitDescriptorType(Enum):
    PANEL_ANGLE = "panelAngle"
    COMPASS_HEADING = "compassHeading"
    PANEL_PEAK_POWER = "panelPeakPower"
    MAX_CONVERTER_PEAK_POWER = "maxConverterPeakPower"
    PRODUCES = "produces"
    BRAND = "brand"
    HEAT_CURVE_OFFSET = "heatCurveOffset"
    HEAT_PUMP_CAPACITY = "heatpumpCapacity"
    BUILDINGS_COVERED = "buildingsCovered"
    PLACEMENT = "placement"
    PLACED_BEFORE_HEAT_RECOVERY = "placedBeforeHeatRecovery"
    PLACEMENT_NUMBER = "placementNumber"
    ACTIVE = "active"
    METER_TYPE = "meterType"
    CONFIGURATION = "configuration"

    @property
    def expected_type(self) -> Type:
        lookup = {
            UnitDescriptorType.PANEL_ANGLE: float,
            UnitDescriptorType.COMPASS_HEADING: float,
            UnitDescriptorType.PANEL_PEAK_POWER: float,
            UnitDescriptorType.MAX_CONVERTER_PEAK_POWER: float,
            UnitDescriptorType.PRODUCES: str,
            UnitDescriptorType.BRAND: str,
            UnitDescriptorType.HEAT_CURVE_OFFSET: float,
            UnitDescriptorType.HEAT_PUMP_CAPACITY: float,
            UnitDescriptorType.BUILDINGS_COVERED: int,
            UnitDescriptorType.PLACEMENT: str,
            UnitDescriptorType.PLACED_BEFORE_HEAT_RECOVERY: bool,
            UnitDescriptorType.PLACEMENT_NUMBER: int,
            UnitDescriptorType.ACTIVE: bool,
            UnitDescriptorType.METER_TYPE: str,
            UnitDescriptorType.CONFIGURATION: dict,
        }
        return lookup[self] if self in lookup else str


class ComponentType(Enum):
    FLOW = "flow"
    SUPPLY_TEMPERATURE = "supplyT"
    RETURN_TEMPERATURE = "returnT"
    VOLUME = "volume"
    VOLUME_CONSUMPTION = "volumeConsumption"
    CONSUMPTION = "consumption"
    ENERGY = "energy"
    FLOW_ACCUMULATED_SUPPLY_TEMPERATURE = "flowAccumulatedSupplyT"
    FLOW_ACCUMULATED_RETURN_TEMPERATURE = "flowAccumulatedReturnT"
    POWER = "power"
    PRIMARY_FLOW = "primaryFlow"
    PRIMARY_RETURN_TEMPERATURE = "primaryReturnT"
    PRIMARY_SUPPLY_TEMPERATURE = "primarySupplyT"
    SENSOR_1 = "sensor1"
    SENSOR_2 = "sensor2"
    SENSOR_3 = "sensor3"
    SENSOR_4 = "sensor4"
    SENSOR_5 = "sensor5"
    SENSOR_6 = "sensor6"
    SENSOR_7 = "sensor7"
    SENSOR_8 = "sensor8"
    SENSOR_9 = "sensor9"
    SENSOR_10 = "sensor10"
    SENSOR_11 = "sensor11"
    SENSOR_12 = "sensor12"
    SENSOR_13 = "sensor13"
    SENSOR_14 = "sensor14"
    SENSOR_15 = "sensor15"
    SENSOR_16 = "sensor16"
    SENSOR_17 = "sensor17"
    SENSOR_18 = "sensor18"
    SENSOR_19 = "sensor19"
    SENSOR_20 = "sensor20"
    BACKUP_ON = "backupOn"
    DEFROST_ON = "defrostOn"
    HOT_GAS = "hotGas"
    HP_ON = "hpOn"
    START_COUNTER = "startCounter"
    TANK_TEMPERATURE = "tankTemperature"
    CONTROL_INPUT = "controlInput"
    CONTROL_SWITCH = "controlSwitch"
    CONTROLLED_SIGNAL = "controlledSignal"
    HEARTBEAT = "heartbeat"
    MOTOR_POSITION = "motorPosition"
    MOTOR_RANGE = "motorRange"
    THERMOSTAT_MOTOR_POSITION_PERCENT = "thermostatMotorPositionPercent"
    ORIGINAL_SETPOINT = "originalSetPoint"
    PERCENTAGE_CONTROLLER = "percentageController"
    PUMP_ON_OFF = "pumpOnOff"
    RELAY_OFF = "relayOff"
    RELAY_ON = "relayOn"
    SECONDARY_CONTROLLED_SIGNAL = "secondaryControlledSignal"
    SETPOINT = "setPoint"
    SETPOINT_OFFSET = "setPointOffset"
    VOLTAGE_CONTROLLER = "voltageController"
    DIFFERENTIAL_PRESSURE = "differentialPressure"
    PRESSURE = "pressure"
    PUMP = "pump"
    RETURN_PRESSURE = "returnPressure"
    SUPPLY_PRESSURE = "supplyPressure"
    VALVE_CURRENT = "valveCurrent"
    VALVE_OPENING = "valveOpening"
    AIR_TEMPERATURE_AFTER = "airTemperatureAfter"
    AIRTEMPERATURE_BEFORE = "airTemperatureBefore"
    CIRCULATION_PUMP = "circulationPump"
    TANK_BOTTOM_TEMPERATURE = "tankBottomT"
    TANK_TOP_TEMPERATURE = "tankTopT"
    CHARGE_TEMPERATURE = "chargeT"
    BATTERY_VOLTAGE = "batteryVoltage"
    CO2 = "co2"
    FLOOR_TEMPERATURE = "floorTemperature"
    FLOOR_TEMPERATURE_MAX = "floorTemperatureMax"
    FLOOR_TEMPERATURE_MIN = "floorTemperatureMin"
    HUMIDITY = "humidity"
    NOISE_LEVEL_AVG = "noiseLevelAvg"
    NOISE_LEVEL_PEAK = "noiseLevelPeak"
    RADON_LONG_TERM = "radonLongTerm"
    RADON_SHORT_TERM = "radonShortTerm"
    SETPOINT_TEMPERATURE = "setPointTemperature"
    SETPOINT_TEMPERATURE_MAX = "setPointTemperatureMax"
    SETPOINT_TEMPERATURE_MIN = "setPointTemperatureMin"
    TEMPERATURE = "temperature"
    THERMOSTAT_MOTOR_POSITION = "thermostatMotorPosition"
    THERMOSTAT_MOTOR_RANGE = "thermostatMotorRange"
    VOC = "voc"
    WINDOW_OPENING = "windowOpening"
    AMBIENT_TEMPERATURE = "ambientTemperature"
    WIND_DIRECTION = "windDirection"
    WIND_SPEED = "windSpeed"
    EXHAUST_AIR_FLOW = "exhaustAirFlow"
    EXHAUST_AIR_PRESSURE = "exhaustAirPressure"
    EXHAUST_AIR_SPEED = "exhaustAirSpeed"
    EXHAUST_AIR_TEMPERATURE = "exhaustAirTemperature"
    EXTRACT_AIR_FLOW = "extractAirFlow"
    EXTRACT_AIR_HUMIDITY = "extractAirHumidity"
    EXTRACT_AIR_PRESSURE = "extractAirPressure"
    EXTRACT_AIR_SPEED = "extractAirSpeed"
    EXTRACT_AIR_TEMPERATURE = "extractAirTemperature"
    EXTRACT_CO2 = "extractCO2"
    EXTRACT_FILTER_DIFFERENTIAL_PRESSURE = "extractFilterDifferentialPressure"
    HEAT_RECOVERY_EXCHANGER_LOADING = "heatRecoveryExchangerLoading"
    HEAT_RECOVERY_RECOVERED_TEMPERATURE = "heatRecoveryRecoveredTemperature"
    INLET_DAMPER_POSITION = "inletDamperPosition"
    INLET_FAN_SPEED = "inletFanSpeed"
    INTAKE_AIR_FLOW = "intakeAirFlow"
    INTAKE_AIR_PRESSURE = "intakeAirPressure"
    INTAKE_AIR_SPEED = "intakeAirSpeed"
    INTAKE_AIR_TEMPERATURE = "intakeAirTemperature"
    INTAKE_FILTER_DIFFERENTIAL_PRESSURE = "intakeFilterDifferentialPressure"
    OUTLET_DAMPER_POSITION = "outletDamperPosition"
    OUTLET_FAN_SPEED = "outletFanSpeed"
    SETPOINT_AIR_FLOW = "setPointAirFlow"
    SETPOINT_CO2 = "setPointCO2"
    SETPOINT_EXTRACT_TEMPERATURE = "setPointExtractTemperature"
    SETPOINT_HEAT_RECOVERY_SUPPLY_TEMPERATURE = "setPointHeatRecoverySupplyTemperature"
    SETPOINT_HUMIDITY = "setPointHumidity"
    SETPOINT_SUPPLY_TEMPERATURE = "setPointSupplyTemperature"
    SUPPLY_AIR_FLOW = "supplyAirFlow"
    SUPPLY_AIR_PRESSURE = "supplyAirPressure"
    SUPPLY_AIR_SPEED = "supplyAirSpeed"
    SUPPLY_AIR_TEMPERATURE = "supplyAirTemperature"
    VENTILATION_ON = "ventilationOn"
    CURRENT_WINDOW_POSITION = "currentWindowPosition"
    ERROR_WINDOW_POSITION = "errorWindowPosition"
    DAMPER_POSITION = "damperPosition"
    LOADING = "loading"
    RECOVERED_TEMPERATURE = "recoveredTemperature"
    EMITTER_TEMPERATURE = "emitterT"
    BATTERY_PERCENTAGE = "batteryPercentage"
    HCA = "hca"
    RADIATOR_TEMPERATURE = "radiatorTempeture"
    TEMPERATURE_ = "Temperature"
    HUMIDITY_ = "Humidity"
    WIND_DIRECTION_ = "WindDirection"
    WIND_SPEED_ = "WindSpeed"
    PRESSURE_ = "Pressure"
    LOW_CLOUDS_ = "LowClouds"
    MEDIUM_CLOUDS_ = "MediumClouds"
    HIGH_CLOUDS_ = "HighClouds"
    FOG_ = "Fog"
    WIND_GUST_ = "WindGust"
    DEW_POINT_TEMPERATURE_ = "DewPointTemperature"
    CLOUDINESS_ = "Cloudiness"
    PRECIPITATION_ = "Precipitation"
    DIRECT_SUN_POWER_ = "DirectSunPower"
    DIFFUSE_SUN_POWER_ = "DiffuseSunPower"
    SUN_ALTITUDE_ = "SunAltitude"
    SUN_AZIMUTH_ = "SunAzimuth"
    DIRECT_SUN_POWER_VERTICAL_ = "DirectSunPowerVertical"
    CHARGING = "charging"
    HOME = "home"
    PLUGGED_IN = "plugged_in"
    RANGE = "range"
    STATE_OF_CHARGE = "stateOfCharge"
    ACTIVE_EXPORT_COUNTER = "active_export_counter"
    ACTIVE_EXPORT_CONSUMPTION = "active_export_consumption"
    REACTIVE_IMPORT = "reactive_import"
    REACTIVE_EXPORT = "reactive_export"
    APPARENT_ENERGY = "apparent_energy"
    APPARENT_POWER = "apparent_power"
    REACTIVE_POWER = "reactive_power"
    FREQUENCY = "frequency"
    CURRENT = "current"
    DMI_TEMPERATURE = "dmiTemperature"
    SG_RELAY_1 = "sgRelay1"
    SG_RELAY_2 = "sgRelay2"

    def __repr__(self) -> str:
        return self.name


class UnitType(Enum):
    CAR_CHARGER = "carChargers"
    COLD_WATER = "coldWater"
    COOLING = "cooling"
    CUSTOM = "custom"
    ELECTRICITY = "electricity"
    HEAT_PUMP = "heatPumps"
    HEATING = "heating"
    HOT_WATER = "hotWater"
    INDOOR_CLIMATE = "indoorClimate"
    LOCAL_WEATHER_STATION = "localWeatherStations"
    MAIN = "main"
    PV = "pvs"
    VENTILATION = "ventilation"
    WINDOW = "window"
    SUB_METER = "subMeters"
    SECONDARY = "secondaries"
    COOLING_COIL = "coolingCoils"
    CONTROL = "controls"
    FLOOR_HEATING_LOOP = "floorHeatingLoops"
    HEATING_COIL = "heatingCoils"
    SUB_HEATING = "subHeating"
    SECONDARY_HEAT_EXCHANGER = "secondaryHeatExchanger"
    SECONDARY_HEAT_EXCHANGER_WITH_TANK = "secondaryHeatExchangerWithTank"
    SECONDARY_TANK = "secondaryTank"
    HEAT_EXCHANGER = "heatExchangers"
    HEAT_RECOVERY = "heatRecovery"
    RADIATOR = "radiators"
    HCA = "hca"
    WEATHER_FORECAST = "weatherForecast"
    THERMOSTAT = "thermostat"
    CAR = "cars"
    SUB_VENTILATION = "subVentilations"

    def __repr__(self) -> str:
        return self.name

    @property
    def components(self) -> list[ComponentType]:
        lookup = {
            UnitType.WEATHER_FORECAST: [
                ComponentType.TEMPERATURE_,
                ComponentType.HUMIDITY_,
                ComponentType.WIND_DIRECTION_,
                ComponentType.WIND_SPEED_,
                ComponentType.PRESSURE_,
                ComponentType.LOW_CLOUDS_,
                ComponentType.MEDIUM_CLOUDS_,
                ComponentType.HIGH_CLOUDS_,
                ComponentType.FOG_,
                ComponentType.WIND_GUST_,
                ComponentType.DEW_POINT_TEMPERATURE_,
                ComponentType.CLOUDINESS_,
                ComponentType.PRECIPITATION_,
                ComponentType.DIRECT_SUN_POWER_,
                ComponentType.DIFFUSE_SUN_POWER_,
                ComponentType.SUN_ALTITUDE_,
                ComponentType.SUN_AZIMUTH_,
                ComponentType.DIRECT_SUN_POWER_VERTICAL_,
            ],
            UnitType.COLD_WATER: [
                ComponentType.FLOW,
                ComponentType.SUPPLY_TEMPERATURE,
                ComponentType.VOLUME,
                ComponentType.VOLUME_CONSUMPTION,
            ],
            UnitType.COOLING: [
                ComponentType.CONSUMPTION,
                ComponentType.ENERGY,
                ComponentType.FLOW_ACCUMULATED_RETURN_TEMPERATURE,
                ComponentType.FLOW_ACCUMULATED_SUPPLY_TEMPERATURE,
                ComponentType.POWER,
                ComponentType.PRIMARY_FLOW,
                ComponentType.PRIMARY_RETURN_TEMPERATURE,
                ComponentType.PRIMARY_SUPPLY_TEMPERATURE,
                ComponentType.VOLUME,
                ComponentType.VOLUME_CONSUMPTION,
            ],
            UnitType.CUSTOM: [
                ComponentType.SENSOR_1,
                ComponentType.SENSOR_2,
                ComponentType.SENSOR_3,
                ComponentType.SENSOR_4,
                ComponentType.SENSOR_5,
                ComponentType.SENSOR_6,
                ComponentType.SENSOR_7,
                ComponentType.SENSOR_8,
                ComponentType.SENSOR_9,
                ComponentType.SENSOR_10,
                ComponentType.SENSOR_11,
                ComponentType.SENSOR_12,
                ComponentType.SENSOR_13,
                ComponentType.SENSOR_14,
                ComponentType.SENSOR_15,
                ComponentType.SENSOR_16,
                ComponentType.SENSOR_17,
                ComponentType.SENSOR_18,
                ComponentType.SENSOR_19,
                ComponentType.SENSOR_20,
            ],
            UnitType.ELECTRICITY: [
                ComponentType.CONSUMPTION,
                ComponentType.ENERGY,
                ComponentType.POWER,
                ComponentType.ACTIVE_EXPORT_CONSUMPTION,
                ComponentType.ACTIVE_EXPORT_COUNTER,
                ComponentType.REACTIVE_IMPORT,
                ComponentType.REACTIVE_EXPORT,
                ComponentType.APPARENT_ENERGY,
                ComponentType.APPARENT_POWER,
                ComponentType.REACTIVE_POWER,
                ComponentType.FREQUENCY,
                ComponentType.CURRENT,
            ],
            UnitType.HEAT_PUMP: [
                ComponentType.BACKUP_ON,
                ComponentType.DEFROST_ON,
                ComponentType.HOT_GAS,
                ComponentType.HP_ON,
                ComponentType.START_COUNTER,
                ComponentType.TANK_TEMPERATURE,
            ],
            UnitType.HEATING: [
                ComponentType.CONSUMPTION,
                ComponentType.ENERGY,
                ComponentType.FLOW_ACCUMULATED_RETURN_TEMPERATURE,
                ComponentType.FLOW_ACCUMULATED_SUPPLY_TEMPERATURE,
                ComponentType.POWER,
                ComponentType.PRIMARY_FLOW,
                ComponentType.PRIMARY_RETURN_TEMPERATURE,
                ComponentType.PRIMARY_SUPPLY_TEMPERATURE,
                ComponentType.VOLUME,
                ComponentType.VOLUME_CONSUMPTION,
            ],
            UnitType.SUB_HEATING: [
                ComponentType.CONSUMPTION,
                ComponentType.ENERGY,
                ComponentType.FLOW_ACCUMULATED_RETURN_TEMPERATURE,
                ComponentType.FLOW_ACCUMULATED_SUPPLY_TEMPERATURE,
                ComponentType.POWER,
                ComponentType.PRIMARY_FLOW,
                ComponentType.PRIMARY_RETURN_TEMPERATURE,
                ComponentType.PRIMARY_SUPPLY_TEMPERATURE,
                ComponentType.VOLUME,
                ComponentType.VOLUME_CONSUMPTION,
            ],
            UnitType.HOT_WATER: [
                ComponentType.CONSUMPTION,
                ComponentType.ENERGY,
                ComponentType.FLOW_ACCUMULATED_RETURN_TEMPERATURE,
                ComponentType.FLOW_ACCUMULATED_SUPPLY_TEMPERATURE,
                ComponentType.POWER,
                ComponentType.PRIMARY_FLOW,
                ComponentType.PRIMARY_RETURN_TEMPERATURE,
                ComponentType.PRIMARY_SUPPLY_TEMPERATURE,
                ComponentType.VOLUME,
                ComponentType.VOLUME_CONSUMPTION,
            ],
            UnitType.INDOOR_CLIMATE: [
                ComponentType.BATTERY_VOLTAGE,
                ComponentType.CO2,
                ComponentType.FLOOR_TEMPERATURE,
                ComponentType.FLOOR_TEMPERATURE_MAX,
                ComponentType.FLOOR_TEMPERATURE_MIN,
                ComponentType.HUMIDITY,
                ComponentType.NOISE_LEVEL_AVG,
                ComponentType.NOISE_LEVEL_PEAK,
                ComponentType.RADON_LONG_TERM,
                ComponentType.RADON_SHORT_TERM,
                ComponentType.SETPOINT_TEMPERATURE,
                ComponentType.SETPOINT_TEMPERATURE_MAX,
                ComponentType.SETPOINT_TEMPERATURE_MIN,
                ComponentType.TEMPERATURE,
                ComponentType.THERMOSTAT_MOTOR_POSITION,
                ComponentType.THERMOSTAT_MOTOR_RANGE,
                ComponentType.VOC,
                ComponentType.WINDOW_OPENING,
            ],
            UnitType.LOCAL_WEATHER_STATION: [
                ComponentType.AMBIENT_TEMPERATURE,
                ComponentType.WIND_DIRECTION,
                ComponentType.WIND_SPEED,
            ],
            UnitType.MAIN: [
                ComponentType.CONSUMPTION,
                ComponentType.ENERGY,
                ComponentType.FLOW,
                ComponentType.FLOW_ACCUMULATED_RETURN_TEMPERATURE,
                ComponentType.FLOW_ACCUMULATED_SUPPLY_TEMPERATURE,
                ComponentType.POWER,
                ComponentType.RETURN_TEMPERATURE,
                ComponentType.SUPPLY_TEMPERATURE,
                ComponentType.VOLUME,
                ComponentType.VOLUME_CONSUMPTION,
            ],
            UnitType.HEAT_RECOVERY: [
                ComponentType.DAMPER_POSITION,
                ComponentType.LOADING,
                ComponentType.RECOVERED_TEMPERATURE,
            ],
            UnitType.VENTILATION: [
                ComponentType.EXHAUST_AIR_FLOW,
                ComponentType.EXHAUST_AIR_PRESSURE,
                ComponentType.EXHAUST_AIR_SPEED,
                ComponentType.EXHAUST_AIR_TEMPERATURE,
                ComponentType.EXTRACT_AIR_FLOW,
                ComponentType.EXTRACT_AIR_HUMIDITY,
                ComponentType.EXTRACT_AIR_PRESSURE,
                ComponentType.EXTRACT_AIR_SPEED,
                ComponentType.EXTRACT_AIR_TEMPERATURE,
                ComponentType.EXTRACT_CO2,
                ComponentType.EXTRACT_FILTER_DIFFERENTIAL_PRESSURE,
                ComponentType.HEAT_RECOVERY_EXCHANGER_LOADING,
                ComponentType.HEAT_RECOVERY_RECOVERED_TEMPERATURE,
                ComponentType.INLET_DAMPER_POSITION,
                ComponentType.INLET_FAN_SPEED,
                ComponentType.INTAKE_AIR_FLOW,
                ComponentType.INTAKE_AIR_PRESSURE,
                ComponentType.INTAKE_AIR_SPEED,
                ComponentType.INTAKE_AIR_TEMPERATURE,
                ComponentType.INTAKE_FILTER_DIFFERENTIAL_PRESSURE,
                ComponentType.OUTLET_DAMPER_POSITION,
                ComponentType.OUTLET_FAN_SPEED,
                ComponentType.SETPOINT_AIR_FLOW,
                ComponentType.SETPOINT_CO2,
                ComponentType.SETPOINT_EXTRACT_TEMPERATURE,
                ComponentType.SETPOINT_HEAT_RECOVERY_SUPPLY_TEMPERATURE,
                ComponentType.SETPOINT_HUMIDITY,
                ComponentType.SETPOINT_SUPPLY_TEMPERATURE,
                ComponentType.SUPPLY_AIR_FLOW,
                ComponentType.SUPPLY_AIR_PRESSURE,
                ComponentType.SUPPLY_AIR_SPEED,
                ComponentType.SUPPLY_AIR_TEMPERATURE,
                ComponentType.VENTILATION_ON,
            ],
            UnitType.SUB_VENTILATION: [
                ComponentType.EXHAUST_AIR_FLOW,
                ComponentType.EXHAUST_AIR_PRESSURE,
                ComponentType.EXHAUST_AIR_SPEED,
                ComponentType.EXHAUST_AIR_TEMPERATURE,
                ComponentType.EXTRACT_AIR_FLOW,
                ComponentType.EXTRACT_AIR_HUMIDITY,
                ComponentType.EXTRACT_AIR_PRESSURE,
                ComponentType.EXTRACT_AIR_SPEED,
                ComponentType.EXTRACT_AIR_TEMPERATURE,
                ComponentType.EXTRACT_CO2,
                ComponentType.EXTRACT_FILTER_DIFFERENTIAL_PRESSURE,
                ComponentType.HEAT_RECOVERY_EXCHANGER_LOADING,
                ComponentType.HEAT_RECOVERY_RECOVERED_TEMPERATURE,
                ComponentType.INLET_DAMPER_POSITION,
                ComponentType.INLET_FAN_SPEED,
                ComponentType.INTAKE_AIR_FLOW,
                ComponentType.INTAKE_AIR_PRESSURE,
                ComponentType.INTAKE_AIR_SPEED,
                ComponentType.INTAKE_AIR_TEMPERATURE,
                ComponentType.INTAKE_FILTER_DIFFERENTIAL_PRESSURE,
                ComponentType.OUTLET_DAMPER_POSITION,
                ComponentType.OUTLET_FAN_SPEED,
                ComponentType.SETPOINT_AIR_FLOW,
                ComponentType.SETPOINT_CO2,
                ComponentType.SETPOINT_EXTRACT_TEMPERATURE,
                ComponentType.SETPOINT_HEAT_RECOVERY_SUPPLY_TEMPERATURE,
                ComponentType.SETPOINT_HUMIDITY,
                ComponentType.SETPOINT_SUPPLY_TEMPERATURE,
                ComponentType.SUPPLY_AIR_FLOW,
                ComponentType.SUPPLY_AIR_PRESSURE,
                ComponentType.SUPPLY_AIR_SPEED,
                ComponentType.SUPPLY_AIR_TEMPERATURE,
                ComponentType.VENTILATION_ON,
            ],
            UnitType.WINDOW: [
                ComponentType.CURRENT_WINDOW_POSITION,
                ComponentType.ERROR_WINDOW_POSITION,
            ],
            UnitType.CONTROL: [
                ComponentType.CONTROL_INPUT,
                ComponentType.CONTROL_SWITCH,
                ComponentType.CONTROLLED_SIGNAL,
                ComponentType.HEARTBEAT,
                ComponentType.MOTOR_POSITION,
                ComponentType.ORIGINAL_SETPOINT,
                ComponentType.PERCENTAGE_CONTROLLER,
                ComponentType.PUMP_ON_OFF,
                ComponentType.RELAY_OFF,
                ComponentType.RELAY_ON,
                ComponentType.SECONDARY_CONTROLLED_SIGNAL,
                ComponentType.SETPOINT,
                ComponentType.SETPOINT_OFFSET,
                ComponentType.VOLTAGE_CONTROLLER,
                ComponentType.SG_RELAY_1,
                ComponentType.SG_RELAY_2,
            ],
            UnitType.COOLING_COIL: [
                ComponentType.AIR_TEMPERATURE_AFTER,
                ComponentType.AIRTEMPERATURE_BEFORE,
                ComponentType.CIRCULATION_PUMP,
                ComponentType.RETURN_TEMPERATURE,
                ComponentType.SUPPLY_TEMPERATURE,
                ComponentType.VALVE_OPENING,
            ],
            UnitType.FLOOR_HEATING_LOOP: [
                ComponentType.CIRCULATION_PUMP,
                ComponentType.RETURN_TEMPERATURE,
                ComponentType.SUPPLY_TEMPERATURE,
                ComponentType.VALVE_CURRENT,
                ComponentType.VALVE_OPENING,
            ],
            UnitType.HEATING_COIL: [
                ComponentType.AIR_TEMPERATURE_AFTER,
                ComponentType.AIRTEMPERATURE_BEFORE,
                ComponentType.CIRCULATION_PUMP,
                ComponentType.RETURN_TEMPERATURE,
                ComponentType.SUPPLY_TEMPERATURE,
                ComponentType.VALVE_OPENING,
            ],
            UnitType.SECONDARY_HEAT_EXCHANGER: [
                ComponentType.RETURN_TEMPERATURE,
                ComponentType.SUPPLY_TEMPERATURE,
            ],
            UnitType.SUB_METER: [
                ComponentType.CONSUMPTION,
                ComponentType.ENERGY,
                ComponentType.FLOW,
                ComponentType.FLOW_ACCUMULATED_RETURN_TEMPERATURE,
                ComponentType.FLOW_ACCUMULATED_SUPPLY_TEMPERATURE,
                ComponentType.POWER,
                ComponentType.RETURN_TEMPERATURE,
                ComponentType.SUPPLY_TEMPERATURE,
                ComponentType.VOLUME,
                ComponentType.VOLUME_CONSUMPTION,
                ComponentType.ACTIVE_EXPORT_CONSUMPTION,
                ComponentType.ACTIVE_EXPORT_COUNTER,
                ComponentType.REACTIVE_IMPORT,
                ComponentType.REACTIVE_EXPORT,
                ComponentType.APPARENT_ENERGY,
                ComponentType.APPARENT_POWER,
                ComponentType.REACTIVE_POWER,
                ComponentType.FREQUENCY,
                ComponentType.CURRENT,
            ],
            UnitType.SECONDARY_HEAT_EXCHANGER_WITH_TANK: [
                ComponentType.CHARGE_TEMPERATURE,
                ComponentType.RETURN_TEMPERATURE,
                ComponentType.SUPPLY_TEMPERATURE,
                ComponentType.TANK_BOTTOM_TEMPERATURE,
                ComponentType.TANK_TOP_TEMPERATURE,
            ],
            UnitType.SECONDARY_TANK: [
                ComponentType.CHARGE_TEMPERATURE,
                ComponentType.RETURN_TEMPERATURE,
                ComponentType.SUPPLY_TEMPERATURE,
                ComponentType.TANK_BOTTOM_TEMPERATURE,
                ComponentType.TANK_TOP_TEMPERATURE,
            ],
            UnitType.HEAT_EXCHANGER: [
                ComponentType.CONSUMPTION,
                ComponentType.ENERGY,
                ComponentType.FLOW,
                ComponentType.FLOW_ACCUMULATED_RETURN_TEMPERATURE,
                ComponentType.FLOW_ACCUMULATED_SUPPLY_TEMPERATURE,
                ComponentType.POWER,
                ComponentType.RETURN_TEMPERATURE,
                ComponentType.SUPPLY_TEMPERATURE,
                ComponentType.VOLUME,
                ComponentType.VOLUME_CONSUMPTION,
            ],
            UnitType.RADIATOR: [
                ComponentType.EMITTER_TEMPERATURE,
                ComponentType.RETURN_TEMPERATURE,
                ComponentType.SUPPLY_TEMPERATURE,
            ],
            UnitType.HCA: [
                ComponentType.AMBIENT_TEMPERATURE,
                ComponentType.BATTERY_PERCENTAGE,
                ComponentType.HCA,
                ComponentType.RADIATOR_TEMPERATURE,
            ],
            UnitType.SECONDARY: [
                ComponentType.CONSUMPTION,
                ComponentType.DIFFERENTIAL_PRESSURE,
                ComponentType.ENERGY,
                ComponentType.FLOW,
                ComponentType.FLOW_ACCUMULATED_RETURN_TEMPERATURE,
                ComponentType.FLOW_ACCUMULATED_SUPPLY_TEMPERATURE,
                ComponentType.POWER,
                ComponentType.PRESSURE,
                ComponentType.PUMP,
                ComponentType.RETURN_PRESSURE,
                ComponentType.RETURN_TEMPERATURE,
                ComponentType.SUPPLY_PRESSURE,
                ComponentType.SUPPLY_TEMPERATURE,
                ComponentType.VOLUME,
                ComponentType.VOLUME_CONSUMPTION,
            ],
            UnitType.THERMOSTAT: [
                ComponentType.TEMPERATURE,
                ComponentType.MOTOR_POSITION,
                ComponentType.MOTOR_RANGE,
                ComponentType.THERMOSTAT_MOTOR_POSITION_PERCENT,
                ComponentType.SETPOINT,
                ComponentType.BATTERY_VOLTAGE,
            ],
            UnitType.CAR: [
                ComponentType.CHARGING,
                ComponentType.HOME,
                ComponentType.PLUGGED_IN,
                ComponentType.RANGE,
                ComponentType.STATE_OF_CHARGE,
                ComponentType.POWER,
            ],
        }
        return lookup[self] if self in lookup else []

    @property
    def children(self) -> list[UnitType]:
        lookup = {
            UnitType.COLD_WATER: [UnitType.SUB_METER],
            UnitType.COOLING: [UnitType.COOLING_COIL, UnitType.SECONDARY],
            UnitType.CUSTOM: [UnitType.CONTROL],
            UnitType.ELECTRICITY: [UnitType.SUB_METER],
            UnitType.SUB_METER: [UnitType.SUB_METER],
            UnitType.HEAT_PUMP: [UnitType.CONTROL],
            UnitType.HEATING: [
                UnitType.FLOOR_HEATING_LOOP,
                UnitType.HEATING_COIL,
                UnitType.SECONDARY,
                UnitType.SUB_HEATING,
            ],
            UnitType.SUB_HEATING: [
                UnitType.FLOOR_HEATING_LOOP,
                UnitType.SECONDARY,
                UnitType.HEATING_COIL,
                UnitType.SUB_HEATING,
            ],
            UnitType.HOT_WATER: [
                UnitType.SECONDARY_HEAT_EXCHANGER,
                UnitType.SECONDARY_HEAT_EXCHANGER_WITH_TANK,
                UnitType.SECONDARY_TANK,
            ],
            UnitType.LOCAL_WEATHER_STATION: [UnitType.CONTROL],
            UnitType.MAIN: [UnitType.HEAT_EXCHANGER],
            UnitType.VENTILATION: [
                UnitType.CONTROL,
                UnitType.HEAT_RECOVERY,
                UnitType.SUB_VENTILATION,
            ],
            UnitType.SUB_VENTILATION: [UnitType.CONTROL, UnitType.HEAT_RECOVERY],
            UnitType.HEAT_RECOVERY: [UnitType.CONTROL],
            UnitType.SECONDARY: [
                UnitType.CONTROL,
                UnitType.FLOOR_HEATING_LOOP,
                UnitType.HEATING_COIL,
                UnitType.RADIATOR,
                UnitType.SECONDARY,
                UnitType.SUB_METER,
                UnitType.COOLING_COIL,
            ],
            UnitType.COOLING_COIL: [UnitType.CONTROL],
            UnitType.FLOOR_HEATING_LOOP: [UnitType.CONTROL],
            UnitType.HEATING_COIL: [UnitType.CONTROL],
            UnitType.SECONDARY_HEAT_EXCHANGER: [UnitType.CONTROL, UnitType.SUB_METER],
            UnitType.SECONDARY_HEAT_EXCHANGER_WITH_TANK: [
                UnitType.CONTROL,
                UnitType.SUB_METER,
            ],
            UnitType.SECONDARY_TANK: [UnitType.CONTROL, UnitType.SUB_METER],
            UnitType.RADIATOR: [UnitType.CONTROL, UnitType.HCA, UnitType.THERMOSTAT],
            UnitType.THERMOSTAT: [UnitType.CONTROL],
        }
        return lookup[self] if self in lookup else []

    @property
    def descriptors(self) -> list[UnitDescriptorType]:
        lookup = {
            UnitType.COLD_WATER: [
                UnitDescriptorType.BUILDINGS_COVERED,
                UnitDescriptorType.PLACEMENT,
            ],
            UnitType.COOLING: [UnitDescriptorType.BUILDINGS_COVERED],
            UnitType.COOLING_COIL: [
                UnitDescriptorType.PLACED_BEFORE_HEAT_RECOVERY,
                UnitDescriptorType.PLACEMENT_NUMBER,
            ],
            UnitType.CONTROL: [UnitDescriptorType.ACTIVE],
            UnitType.ELECTRICITY: [
                UnitDescriptorType.BUILDINGS_COVERED,
                UnitDescriptorType.METER_TYPE,
                UnitDescriptorType.CONFIGURATION,
            ],
            UnitType.SUB_METER: [
                UnitDescriptorType.METER_TYPE,
                UnitDescriptorType.CONFIGURATION,
                UnitDescriptorType.PLACEMENT,
            ],
            UnitType.HEAT_PUMP: [
                UnitDescriptorType.BRAND,
                UnitDescriptorType.HEAT_CURVE_OFFSET,
                UnitDescriptorType.HEAT_PUMP_CAPACITY,
                UnitDescriptorType.PRODUCES,
            ],
            UnitType.HEATING: [UnitDescriptorType.BUILDINGS_COVERED],
            UnitType.SUB_HEATING: [
                UnitDescriptorType.BUILDINGS_COVERED,
            ],
            UnitType.HEATING_COIL: [
                UnitDescriptorType.PLACED_BEFORE_HEAT_RECOVERY,
                UnitDescriptorType.PLACEMENT_NUMBER,
            ],
            UnitType.HOT_WATER: [UnitDescriptorType.BUILDINGS_COVERED],
            UnitType.MAIN: [UnitDescriptorType.BUILDINGS_COVERED],
            UnitType.PV: [
                UnitDescriptorType.COMPASS_HEADING,
                UnitDescriptorType.MAX_CONVERTER_PEAK_POWER,
                UnitDescriptorType.PANEL_ANGLE,
                UnitDescriptorType.PANEL_PEAK_POWER,
            ],
        }
        return lookup[self] if self in lookup else []

    @property
    def related_units(self) -> list[RelatedUnitType]:
        lookup = {
            UnitType.HEAT_PUMP: [
                RelatedUnitType.ELECTRICITY,
                RelatedUnitType.HEATING,
                RelatedUnitType.COOLING,
                RelatedUnitType.HOT_WATER,
                RelatedUnitType.MAIN,
            ],
            UnitType.CAR_CHARGER: [RelatedUnitType.ELECTRICITY],
            UnitType.SECONDARY_HEAT_EXCHANGER: [RelatedUnitType.COLD_WATER],
            UnitType.SECONDARY_HEAT_EXCHANGER_WITH_TANK: [RelatedUnitType.COLD_WATER],
            UnitType.SECONDARY_TANK: [RelatedUnitType.COLD_WATER],
            UnitType.PV: [RelatedUnitType.ELECTRICITY],
            UnitType.VENTILATION: [
                RelatedUnitType.COOLING_COIL,
                RelatedUnitType.ELECTRICITY,
                RelatedUnitType.HEATING_COIL,
                RelatedUnitType.HEATING_SECONDARY,
                RelatedUnitType.COOLING_SECONDARY,
            ],
            UnitType.SUB_VENTILATION: [
                RelatedUnitType.COOLING_COIL,
                RelatedUnitType.ELECTRICITY,
                RelatedUnitType.HEATING_COIL,
                RelatedUnitType.HEATING_SECONDARY,
                RelatedUnitType.COOLING_SECONDARY,
            ],
        }
        return lookup[self] if self in lookup else []

    @property
    def is_top_level(self) -> bool:
        return self in [
            UnitType.CAR,
            UnitType.CAR_CHARGER,
            UnitType.COLD_WATER,
            UnitType.COOLING,
            UnitType.CUSTOM,
            UnitType.ELECTRICITY,
            UnitType.HEAT_PUMP,
            UnitType.HEATING,
            UnitType.HOT_WATER,
            UnitType.INDOOR_CLIMATE,
            UnitType.LOCAL_WEATHER_STATION,
            UnitType.MAIN,
            UnitType.PV,
            UnitType.VENTILATION,
            UnitType.WINDOW,
        ]


class UnitSubType(Enum):
    DIRECT = "DIRECT"
    HOT_WATER_TANK = "HOT_WATER_TANK"
    COUNTER_FLOW_HEAT_EXCHANGER = "COUNTER_FLOW_HEAT_EXCHANGER"
    HEAT_EXCHANGER_WITH_TANK = "HEAT_EXCHANGER_WITH_TANK"
    ROTARY_WHEEL_HEAT_EXCHANGER = "ROTARY_WHEEL_HEAT_EXCHANGER"
    HEAT_EXCHANGER = "HEAT_EXCHANGER"
    MIXING_LOOP = "MIXING_LOOP"
    CONTROL_HEAT = "CONTROL_HEAT"
    CONTROL_WATER_CIRCULATION = "CONTROL_WATER_CIRCULATION"
    CONTROL_WATER_TANK = "CONTROL_WATER_TANK"
    CONTROL_OTHER_EXTERNAL = "CONTROL_OTHER_EXTERNAL"
    CONTROL_COOLING = "CONTROL_COOLING"
    CONTROL_HEAT_PUMP_ON_OFF = "CONTROL_HEAT_PUMP_ON_OFF"
    CONTROL_TANK_TEMPERATURE_MIN = "CONTROL_TANK_TEMPERATURE_MIN"
    CONTROL_TANK_TEMPERATURE_MAX = "CONTROL_TANK_TEMPERATURE_MAX"
    CONTROL_OUTDOOR_TEMPERATURE = "CONTROL_OUTDOOR_TEMPERATURE"
    CONTROL_HEAT_PUMP_HEAT_CURVE_OFFSET = "CONTROL_HEAT_PUMP_HEAT_CURVE_OFFSET"
    CONTROL_HEAT_PUMP_BLOCKING = "CONTROL_HEAT_PUMP_BLOCKING"
    CONTROL_HEAT_PUMP_BLOCKING_WITH_MAPPING = "CONTROL_HEAT_PUMP_BLOCKING_WITH_MAPPING"
    CONTROL_HEAT_PUMP_BLOCKING_WITH_SLIDER_MAPPING = (
        "CONTROL_HEAT_PUMP_BLOCKING_WITH_SLIDER_MAPPING"
    )
    CONTROL_ZONE = "CONTROL_ZONE"
    CONTROL_SG_READY = "CONTROL_SG_READY"
    CONTROL_HEAT_PUMP_BLOCKING_OFFSET = "CONTROL_HEAT_PUMP_BLOCKING_OFFSET"
    CONSUMPTION = "CONSUMPTION"
    PRODUCTION = "PRODUCTION"
    BOTH = "BOTH"


@dataclass(eq=False)
class UnitQuery(Query):
    id: list[int] = field(default_factory=list)
    name: list[str] = field(default_factory=list)
    shared: list[bool] = field(default_factory=lambda: [False, None])
    type: list[UnitType] = field(default_factory=list)
    _type_type: ClassVar[type] = UnitType
    subtype: list[UnitSubType] = field(default_factory=list)
    _subtype_type: ClassVar[type] = UnitSubType
    parent: list[UnitQuery] = field(default_factory=list)
    _type_parent: ClassVar[type] = "self"
    exclude: list[UnitQuery] = field(default_factory=list)
    _type_exclude: ClassVar[type] = "self"
    _class: ClassVar[type] = Unit


@dataclass(eq=False)
class ComponentQuery(Query):
    cid: list[int] = field(default_factory=list)
    id: list[int] = field(default_factory=list)
    name: list[str] = field(default_factory=list)
    unit: list[str] = field(default_factory=list)
    type: list[ComponentType] = field(default_factory=list)
    _type_type: ClassVar[type] = ComponentType
    parent: list[UnitQuery] = field(default_factory=list)
    _type_parent: ClassVar[type] = UnitQuery
    exclude: list[ComponentQuery] = field(default_factory=list)
    _type_exclude: ClassVar[type] = "self"
    _class: ClassVar[type] = Component


@dataclass(eq=False)
class DeviceQuery(Query):
    id: list[int] = field(default_factory=list)
    name: list[str] = field(default_factory=list)
    type: list[str] = field(default_factory=list)
    _class: ClassVar[type] = Device


@dataclass(eq=False)
class ZoneQuery(Query):
    id: list[int] = field(default_factory=list)
    name: list[str] = field(default_factory=list)
    type: list[str] = field(default_factory=list)
    external_identifier: list[str] = field(default_factory=list)
    _class: ClassVar[type] = Zone


class BuildingType(Enum):
    """
    Enum class for building types, effectively decoupling from database values
    """

    # For each of these elements, the value must be one of the ones found by querying:
    #       SELECT DISTINCT(building_type) FROM building_characteristics
    SINGLE_FAMILY_HOUSE = "SINGLE_FAMILY_HOME"
    MULTI_FAMILY_HOUSE = "TERRACED_HOUSE"
    APARTMENT_BUILDING = "APARTMENT_BUILDING"
    OFFICE_BUILDING = "OFFICE_BUILDING"
    SHOPPING_CENTER = "SHOPPING_CENTER"
    SCHOOL = "SCHOOL"
    OTHER = "OTHER"
    TEST = "TEST"
