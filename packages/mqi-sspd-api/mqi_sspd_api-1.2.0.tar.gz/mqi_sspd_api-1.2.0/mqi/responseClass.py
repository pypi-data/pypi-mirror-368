from typing import List, Dict, Optional


# -----------------------
# Classes for ChannelValue
# -----------------------

from typing import Union

class ChannelValue:
    def __init__(self, value: Union[int, float]):
        self.value = value

    @classmethod
    def from_int(cls, value: int) -> 'ChannelValue':
        if not isinstance(value, int):
            raise TypeError("Expected int")
        return cls(value)

    @classmethod
    def from_float(cls, value: float) -> 'ChannelValue':
        if not isinstance(value, float):
            raise TypeError("Expected float")
        return cls(value)

    def __repr__(self):
        return f"ChannelValue(value={self.value})"

# ----------------------
# Classes for CURRENT
# ----------------------


class Current:
    def __init__(self, channels: Dict[int, ChannelValue]):
        self.channels = channels

    @staticmethod
    def from_json(data: dict) -> 'Current':
        return Current({
            int(ch): ChannelValue(**val)
            for ch, val in data['channels'].items()
        })

    def __repr__(self):
        return f"Current(channels={self.channels})"


# ----------------------
# Classes for VOLTAGE
# ----------------------

class VoltageChannel:
    def __init__(self, value_get: float, value_set: float):
        self.value_get = value_get
        self.value_set = value_set

    def __repr__(self):
        return f"VoltageChannel(get={self.value_get}, set={self.value_set})"


class Voltage:
    def __init__(self, channels: Dict[int, VoltageChannel]):
        self.channels = channels

    @staticmethod
    def from_json(data: dict) -> 'Voltage':
        return Voltage({
            int(ch): VoltageChannel(**val)
            for ch, val in data['channels'].items()
        })

    def __repr__(self):
        return f"Voltage(channels={self.channels})"
    

# ----------------------
# Classes for active channels
# ----------------------

class ActiveChannels:
    def __init__(self, active_channels: List[int]):
        self.active_channels = active_channels

    @staticmethod
    def from_json(data: dict) -> 'ActiveChannels':
        return ActiveChannels(active_channels=data['active_channels'])

    def __repr__(self):
        return f"ActiveChannels(active_channels={self.active_channels})"
    

# ----------------------
# Classes for TargetVoltage/Current
# ----------------------

    
class TargetVoltage:
    def __init__(self, channels: Dict[int, ChannelValue]):
        self.channels = channels

    @staticmethod
    def from_json(data: dict) -> 'TargetVoltage':
        return TargetVoltage({
            int(ch): ChannelValue(**val)
            for ch, val in data['channels'].items()
        })

    def __repr__(self):
        return f"TargetVoltage(channels={self.channels})"
    
class TargetCurrent:
    def __init__(self, channels: Dict[int, ChannelValue]):
        self.channels = channels

    @staticmethod
    def from_json(data: dict) -> 'TargetCurrent':
        return TargetCurrent({
            int(ch): ChannelValue(**val)
            for ch, val in data['channels'].items()
        })

    def __repr__(self):
        return f"TargetCurrent(channels={self.channels})"
    
# ----------------------
# Classes for LoadResistance
# ----------------------

class LoadResistance:
    def __init__(self, channels: Dict[int, ChannelValue]):
        self.channels = channels

    @staticmethod
    def from_json(data: dict) -> 'LoadResistance':
        return TargetVoltage({
            int(ch): ChannelValue(**val)
            for ch, val in data['channels'].items()
        })

    def __repr__(self):
        return f"LoadResistance(channels={self.channels})"
    
# ----------------------
# Classes for AutoDelatching
# ----------------------

class AutoDeLatching:
    def __init__(
        self,
        active: bool,
        checkLatchingInterval_ms: int,
        fineSteps: int,
        perc_start_fineSweep: float,
        roughSteps: int,
        sweep_delay_ms: int,
        volt_drop_for_detection: float
    ):
        self.active = active
        self.checkLatchingInterval_ms = checkLatchingInterval_ms
        self.fineSteps = fineSteps
        self.perc_start_fineSweep = perc_start_fineSweep
        self.roughSteps = roughSteps
        self.sweep_delay_ms = sweep_delay_ms
        self.volt_drop_for_detection = volt_drop_for_detection

    @staticmethod
    def from_json(data: dict) -> 'AutoDeLatching':
        return AutoDeLatching(**data['autoDeLatching'])

    def __repr__(self):
        return (
            f"AutoDeLatching(active={self.active}, "
            f"checkLatchingInterval_ms={self.checkLatchingInterval_ms}, "
            f"fineSteps={self.fineSteps}, "
            f"perc_start_fineSweep={self.perc_start_fineSweep}, "
            f"roughSteps={self.roughSteps}, "
            f"sweep_delay_ms={self.sweep_delay_ms}, "
            f"volt_drop_for_detection={self.volt_drop_for_detection})"
        )

# ----------------------
# Classes for CounterAutoDelatching
# ----------------------

class CounterAutoDelatching:
    def __init__(self, counters: Dict[str, ChannelValue]):
        self.counters = counters

    @staticmethod
    def from_json(data: dict) -> 'CounterAutoDelatching':
        return CounterAutoDelatching({
            ch: ChannelValue(int(val['counter']))  # parse 'counter' from JSON as 'value'
            for ch, val in data['CounterAutoDelatching'].items()
        })

    def __repr__(self):
        return f"CounterAutoDelatching(counters={self.counters})"

# ----------------------
# Classes form MaxVoltage/Current  
# ----------------------

class MaxVoltCurrentChannel:
    def __init__(self, current: float, volt: float):
        self.current = current
        self.volt = volt

    def __repr__(self):
        return f"MaxVoltCurrentChannel(current={self.current}, volt={self.volt})"


class MaxVoltCurrent:
    def __init__(self, channels: Dict[int, MaxVoltCurrentChannel]):
        self.channels = channels

    @staticmethod
    def from_json(data: dict) -> 'MaxVoltCurrent':
        return MaxVoltCurrent({
            int(ch): MaxVoltCurrentChannel(**val)
            for ch, val in data['channels'].items()
        })

    def __repr__(self):
        return f"MaxVoltCurrent(channels={self.channels})"

class Communication:
    def __init__(self, type: str, port: Optional[str] = None, baudRate: Optional[int] = None, url: Optional[str] = None):
        self.type = type
        self.port = port
        self.baudRate = baudRate
        self.url = url

    def __repr__(self):
        return f"Communication(type={self.type}, port={self.port}, baudRate={self.baudRate}, url={self.url})"
    
    def to_json(self):
        data = {'type': self.type}
        if self.port is not None:
            data['port'] = self.port
        if self.baudRate is not None:
            data['baudRate'] = self.baudRate
        if self.url is not None:
            data['url'] = self.url
        return data


class Compressor:
    def __init__(self, ads_id: str, communication: Communication, createRouting: bool):
        self.ads_id = ads_id
        self.communication = communication
        self.createRouting = createRouting

    def to_json(self):
        return {
            'ads_id': self.ads_id,
            'communication': self.communication.to_json(),
            'createRouting': self.createRouting
        }
    
    def __repr__(self):
        return (
            f"Compressor(ads_id={self.ads_id!r}, "
            f"communication={self.communication!r}, "
            f"createRouting={self.createRouting})"
        )

    @staticmethod
    def from_json(data: dict) -> 'Compressor':
        return Compressor(
            ads_id=data['ads_id'],
            communication=Communication(**data['communication']),
            createRouting=data['createRouting']
        )
    
    


class TemperaturMonitorCompressor:
    def __init__(self, communication: Communication):
        self.communication = communication

    @staticmethod
    def from_json(data: dict) -> 'TemperaturMonitorCompressor':
        return TemperaturMonitorCompressor(
            communication=Communication(**data['communication'])
        )
    
    def to_json(self):
        return {
            'communication': self.communication.to_json()
        }
    



class ChannelConfig:
    def __init__(self, active: bool, resistance: int, voltage: str):
        self.active = active
        self.resistance = resistance
        self.voltage = voltage

    def __repr__(self):
        return f"Channel(active={self.active}, resistance={self.resistance}, voltage={self.voltage})"
    
    def to_json(self):
        return {
            'active': self.active,
            'resistance': self.resistance,
            'voltage': self.voltage
        }


class Biasbox:
    def __init__(self,
                 name: str,
                 unique_id: str,
                 powersupply: str,
                 communication: Communication,
                 isUsed: bool,
                 uploadSketchWhileRestart: bool,
                 channels: Dict[int, ChannelConfig],
                 _readonly: List[str]):
        self.name = name
        self.unique_id = unique_id
        self.powersupply = powersupply
        self.communication = communication
        self.isUsed = isUsed
        self.uploadSketchWhileRestart = uploadSketchWhileRestart
        self.channels = channels
        self._readonly = _readonly

    @staticmethod
    def from_json(data: dict) -> 'Biasbox':
        channels = {
            int(k): ChannelConfig(**v) for k, v in data['channels'].items()
        }
        return Biasbox(
            name=data['name'],
            unique_id=data['unique_id'],
            powersupply=data['powersupply'],
            communication=Communication(**data['communication']),
            isUsed=data['isUsed'],
            uploadSketchWhileRestart=data['uploadSketchWhileRestart'],
            channels=channels,
            _readonly=data.get('_readonly', [])
        )
    
    def to_json(self):
        return {
            'name': self.name,
            'unique_id': self.unique_id,
            'powersupply': self.powersupply,
            'communication': self.communication.to_json(),
            'isUsed': self.isUsed,
            'uploadSketchWhileRestart': self.uploadSketchWhileRestart,
            'channels': {str(k): v.to_json() for k, v in self.channels.items()},
            '_readonly': self._readonly
        }
    
    def __repr__(self):
        return (
            f"Biasbox(name={self.name!r},"
            f"unique_id={self.unique_id!r},\n "
            f"powersupply={self.powersupply!r}, "
            f"communication={self.communication!r},\n"
            f"isUsed={self.isUsed},"
            f"uploadSketchWhileRestart={self.uploadSketchWhileRestart},\n"
            f"channels={{\n    " + ",\n    ".join(f"{k}: {v!r}" for k, v in self.channels.items()) + "\n  }},"
            f"_readonly={self._readonly})"
        )


class RpiCommunication:
    def __init__(self, type: str, port: str, url: str):
        self.type = type
        self.port = port
        self.url = url

    def to_json(self):
        return {
            'type': self.type,
            'port': self.port,
            'url': self.url
        }


class Config:
    def __init__(self,
                 compressor: Compressor,
                 temperatur_monitor_compressor: TemperaturMonitorCompressor,
                 biasboxes: List[Biasbox],
                 rpi_communication: RpiCommunication,
                 _readonly: List[str]):
        self.compressor = compressor
        self.temperatur_monitor_compressor = temperatur_monitor_compressor
        self.biasboxes = biasboxes
        self.rpi_communication = rpi_communication
        self._readonly = _readonly

    @staticmethod
    def from_json(data: dict) -> 'Config':
        config = data['config']
        return Config(
            compressor=Compressor.from_json(config['Compressor']),
            temperatur_monitor_compressor=TemperaturMonitorCompressor.from_json(config['TemperaturMonitorCompressor']),
            biasboxes=[Biasbox.from_json(b) for b in config['biasboxes']],
            rpi_communication=RpiCommunication(**config['rpi_communication']),
            _readonly=config.get('_readonly', [])
        )

    def __repr__(self):
        return f"Config(compressor={self.compressor}, biasboxes={self.biasboxes})"
    
    def to_json(self):
        return {
            'config': {
                'Compressor': self.compressor.to_json(),
                'TemperaturMonitorCompressor': self.temperatur_monitor_compressor.to_json(),
                'biasboxes': [b.to_json() for b in self.biasboxes],
                'rpi_communication': self.rpi_communication.to_json(),
                '_readonly': self._readonly
            }
        }
    

    
class User:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    def __repr__(self):
        return f"User(name={self.name}, role={self.role})"
    
    @staticmethod
    def from_json(data: dict) -> 'User':
        return User(
            name=data['user']['username'],
            role=data['user']['auth']
        )



class Users:
    def __init__(self, users: List[User]):
        self.users = users

    @staticmethod
    def from_json(data: dict) -> 'Users':
        return Users([
            User(name, role) for name, role in data['users']
        ])

    def __repr__(self):
        return f"Users(users={self.users})"
    
class CompressorStatus:
    def __init__(
        self,
        AmbientTemp: float,
        CV1Temp: float,
        CV2Temp: float,
        CompErrLastEntryIdx: int,
        CompErrString: str,
        CompStatus: int,
        CryoBoardTemperatur: float,
        CryostatVacuum: float,
        CurSpeed: float,
        Cycles: int,
        DifferentialPressure: float,
        ExceededCycleCounter: int,
        FirstStageTemperature: float,
        HasCompErr: bool,
        Hours: float,
        IsColdHeadRunning: bool,
        IsCompReady: bool,
        IsCompRunning: bool,
        MaxCycleTorque: float,
        MotorTemp: float,
        ReturnPressure: float,
        SecondStageTemperatur: float,
        SetColdHeadSpeed: float,
        SetSpeed: float,
        SupplyPressure: float
    ):
        self.AmbientTemp = AmbientTemp
        self.CV1Temp = CV1Temp
        self.CV2Temp = CV2Temp
        self.CompErrLastEntryIdx = CompErrLastEntryIdx
        self.CompErrString = CompErrString
        self.CompStatus = CompStatus
        self.CryoBoardTemperatur = CryoBoardTemperatur
        self.CryostatVacuum = CryostatVacuum
        self.CurSpeed = CurSpeed
        self.Cycles = Cycles
        self.DifferentialPressure = DifferentialPressure
        self.ExceededCycleCounter = ExceededCycleCounter
        self.FirstStageTemperature = FirstStageTemperature
        self.HasCompErr = HasCompErr
        self.Hours = Hours
        self.IsColdHeadRunning = IsColdHeadRunning
        self.IsCompReady = IsCompReady
        self.IsCompRunning = IsCompRunning
        self.MaxCycleTorque = MaxCycleTorque
        self.MotorTemp = MotorTemp
        self.ReturnPressure = ReturnPressure
        self.SecondStageTemperatur = SecondStageTemperatur
        self.SetColdHeadSpeed = SetColdHeadSpeed
        self.SetSpeed = SetSpeed
        self.SupplyPressure = SupplyPressure

    @staticmethod
    def from_json(data: dict) -> 'CompressorStatus':
        return CompressorStatus(**data)

    def __repr__(self):
        return f"CompressorStatus({self.__dict__})"
    
class CompressorSecondStageTemperature:
    def __init__(self, Temp1: float, Temp3: float):
        self.Temp1 = Temp1
        self.Temp3 = Temp3

    @staticmethod
    def from_json(data: dict) -> 'CompressorSecondStageTemperature':
        return CompressorSecondStageTemperature(
            Temp1=data['Temp1'],
            Temp3=data['Temp3']
        )

    def __repr__(self):
        return f"CompressorSecondStageTemperature(Temp1={self.Temp1}, Temp3={self.Temp3})"
    
#-----------------------
# Classes for ConnectedBiasBoxesResponse
#-----------------------
    
class ConnectedBiasBox:
    def __init__(self, deviceNote: str, port: str):
        self.deviceNote = deviceNote
        self.port = port

    def __repr__(self):
        return f"ConnectedBiasBox(deviceNote={self.deviceNote}, port={self.port})"


class ConnectedBiasBoxes:
    def __init__(self, ConnectedBiasBoxes: List[ConnectedBiasBox]):
        self.ConnectedBiasBoxes = ConnectedBiasBoxes

    @staticmethod
    def from_json(data: dict) -> 'ConnectedBiasBoxes':
        boxes = [
            ConnectedBiasBox(**box)
            for box in data.get("ConnectedBiasBoxes", [])
        ]
        return ConnectedBiasBoxes(boxes)

    def __repr__(self):
        return f"ConnectedBiasBoxes(ConnectedBiasBoxes={self.ConnectedBiasBoxes})"

# ----------------------
# Classes for ControlUnitVoltages
# ----------------------
class ControlUnitVoltages:
    def __init__(self, _3V3: float, _5V: float, FAN_VOLTAGE: float, V_IN: float):
        self._3V3 = _3V3
        self._5V = _5V
        self.FAN_VOLTAGE = FAN_VOLTAGE
        self.V_IN = V_IN

    @staticmethod
    def from_json(data: dict) -> 'ControlUnitVoltages':
        return ControlUnitVoltages(
            _3V3=data['3V3'],
            _5V=data['5V'],
            FAN_VOLTAGE=data['FAN_VOLTAGE'],
            V_IN=data['V_IN']
        )

    def __repr__(self):
        return (f"ControlUnitVoltages(_3V3={self._3V3}, _5V={self._5V}, "
                f"FAN_VOLTAGE={self.FAN_VOLTAGE}, V_IN={self.V_IN})")
    
class ControlUnitTemperatures:
    def __init__(self, Temperature1: float, Temperature2: float, Temperature3: float, Temperature4: float):
        self.Temperature1 = Temperature1
        self.Temperature2 = Temperature2
        self.Temperature3 = Temperature3
        self.Temperature4 = Temperature4

    @staticmethod
    def from_json(data: dict) -> 'ControlUnitTemperatures':
        return ControlUnitTemperatures(
            Temperature1=data['Temperature1'],
            Temperature2=data['Temperature2'],
            Temperature3=data['Temperature3'],
            Temperature4=data['Temperature4'],
        )

    def __repr__(self):
        return (f"ControlUnitTemperatures(Temperature1={self.Temperature1}, Temperature2={self.Temperature2}, "
                f"Temperature3={self.Temperature3}, Temperature4={self.Temperature4})")