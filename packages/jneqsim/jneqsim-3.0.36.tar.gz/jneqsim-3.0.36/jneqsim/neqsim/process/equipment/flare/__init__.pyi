
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import java.lang
import java.util
import jneqsim.neqsim.process.equipment
import jneqsim.neqsim.process.equipment.stream
import typing



class Flare(jneqsim.neqsim.process.equipment.TwoPortEquipment):
    @typing.overload
    def __init__(self, string: typing.Union[java.lang.String, str]): ...
    @typing.overload
    def __init__(self, string: typing.Union[java.lang.String, str], streamInterface: jneqsim.neqsim.process.equipment.stream.StreamInterface): ...
    @typing.overload
    def getCO2Emission(self) -> float: ...
    @typing.overload
    def getCO2Emission(self, string: typing.Union[java.lang.String, str]) -> float: ...
    @typing.overload
    def getHeatDuty(self) -> float: ...
    @typing.overload
    def getHeatDuty(self, string: typing.Union[java.lang.String, str]) -> float: ...
    @typing.overload
    def run(self) -> None: ...
    @typing.overload
    def run(self, uUID: java.util.UUID) -> None: ...
    def setInletStream(self, streamInterface: jneqsim.neqsim.process.equipment.stream.StreamInterface) -> None: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.process.equipment.flare")``.

    Flare: typing.Type[Flare]
