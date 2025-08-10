"""Handles parsing of json data."""

__all__ = ["BreakerData", "CTData", "PanelData", "ParsedData", "parse_data"]
from typing import TypedDict

from .const import LEG1_POSITIONS, RMS_VOLTAGE_FACTOR


class BreakerData(TypedDict):
    """Parsed data related to breakers."""

    id: str  # ID for the given breaker
    panel_id: str  # Panel where the breaker exists
    rating: int
    position: int
    name: str
    state: bool
    model: str
    poles: int
    serialNumber: str
    hardware: str
    firmware: str
    canRemoteOn: bool
    remoteState: str
    power: float
    voltage: float
    frequency: float
    current: float
    leg: int
    power1: float
    voltage1: float
    current1: float
    frequency1: float
    power2: float
    voltage2: float
    current2: float
    frequency2: float


CTData = TypedDict(
    "CTData",
    {
        "id": str,
        "name": str,
        "panel_id": str,
        "channel": str,
        "power": float,
        "consumption": float,
        "import": float,
        "current": float,
        "current1": float,
        "current2": float,
    },
)


class PanelData(TypedDict):
    """Parsed data related to Panels."""

    id: str
    name: str
    model: str
    firmware: str
    serialNumber: str
    voltage: float
    voltage1: float
    frequency1: float
    frequency2: float


class ParsedData(TypedDict):
    """Parsed API data.

    This data includes a <panel_id>_totalPower key for each panel.
    """

    breakers: dict[str, BreakerData]
    cts: dict[str, CTData]
    panels: list[PanelData]


def none_to_zero(data, key) -> float:
    """Convert a value to a float and replace None with 0.0."""
    try:
        result = float(data.get(key, None))
    except (TypeError, ValueError):
        result = 0.0
    return result


def parse_data(api_data: list[dict], three_phase: bool = False) -> ParsedData:
    """Parse the API data into a well-formatted object."""
    breakers: dict[str, BreakerData] = {}
    cts: dict[str, CTData] = {}
    panels: list[PanelData] = []
    panel_power: dict[str, float] = {}
    for panel in api_data:
        panel_data = PanelData()
        panel_data["firmware"] = panel["updateVersion"]
        panel_data["model"] = panel["model"]
        panel_data["id"] = panel["id"]
        panel_data["name"] = panel["name"]
        panel_data["serialNumber"] = panel["id"]
        if not three_phase:
            panel_data["voltage"] = (
                float(panel["rmsVoltage"]) + float(panel["rmsVoltage2"])
            ) / 2.0
        else:
            panel_data["voltage"] = (
                float(panel["rmsVoltage"]) * RMS_VOLTAGE_FACTOR
            ) + (float(panel["rmsVoltage2"]) * RMS_VOLTAGE_FACTOR)
        panel_data["voltage1"] = float(panel["rmsVoltage"])
        panel_data["voltage2"] = float(panel["rmsVoltage2"])
        panel_data["frequency1"] = float(none_to_zero(panel, "frequencyA"))
        panel_data["frequency2"] = float(none_to_zero(panel, "frequencyB"))
        if panel_data["frequency1"] == 0:
            panel_data["frequency1"] = 0
            panel_data["frequency2"] = 0
            for breaker in panel["residentialBreakers"]:
                if breaker["position"] in LEG1_POSITIONS:
                    if float(none_to_zero(breaker, "lineFrequency")) > 0:
                        panel_data["frequency1"] = float(
                            none_to_zero(breaker, "lineFrequency")
                        )
                    if float(none_to_zero(breaker, "lineFrequency2")) > 0:
                        panel_data["frequency2"] = float(
                            none_to_zero(breaker, "lineFrequency2")
                        )
                else:
                    if float(none_to_zero(breaker, "lineFrequency")) > 0:
                        panel_data["frequency2"] = float(
                            none_to_zero(breaker, "lineFrequency")
                        )
                    if float(none_to_zero(breaker, "lineFrequency2")) > 0:
                        panel_data["frequency1"] = float(
                            none_to_zero(breaker, "lineFrequency2")
                        )
                if panel_data["frequency1"] != 0 and panel_data["frequency2"] != 0:
                    break
        if panel_data["frequency2"] == 0:
            panel_data["frequency2"] = panel_data["frequency1"]
        panel_data["frequency"] = (
            float(panel_data["frequency1"]) + float(panel_data["frequency2"])
        ) / 2
        panels.append(panel_data)
        if "CTs" in panel:
            cts.update(parse_cts(panel["CTs"], panel["id"]))
        parsed_breaker_data = parse_breakers(
            panel["residentialBreakers"], panel["id"], three_phase=three_phase
        )
        panel_power[panel["id"] + "totalPower"] = sum(
            breaker["power"]
            for breaker in parsed_breaker_data
            if isinstance(breaker["power"], float)
        )
        breakers.update(parsed_breaker_data)
    full_data = ParsedData(breakers=breakers, cts=cts, panels=panels)
    full_data.update(panel_power)
    return full_data


def parse_breakers(
    api_breakers: list, panel_id: str, three_phase: bool
) -> dict[str, BreakerData]:
    breakers: dict[str, BreakerData] = {}
    for breaker in api_breakers:
        if breaker["model"] in [None, "NONE-1", "NONE-2"]:
            continue
        breaker_data = BreakerData()
        breaker_data["panel_id"] = panel_id
        breaker_data["rating"] = breaker["currentRating"]
        breaker_data["position"] = breaker["position"]
        breaker_data["name"] = breaker["name"]
        breaker_data["state"] = breaker["currentState"]
        breaker_data["id"] = breaker["id"]
        breaker_data["model"] = breaker["model"]
        breaker_data["poles"] = breaker["poles"]
        breaker_data["serialNumber"] = breaker["serialNumber"]
        breaker_data["hardware"] = breaker["hwVersion"]
        breaker_data["firmware"] = breaker["firmwareVersionMeter"]
        breaker_data["canRemoteOn"] = bool(breaker["canRemoteOn"])
        breaker_data["remoteState"] = (
            "RemoteON"
            if breaker["remoteState"] in ["", "RemoteOn"]
            else breaker["remoteState"]
        )
        breaker_data["power"] = none_to_zero(breaker, "power") + none_to_zero(
            breaker, "power2"
        )
        if not three_phase or (breaker["poles"] == 1):
            breaker_data["voltage"] = none_to_zero(
                breaker, "rmsVoltage"
            ) + none_to_zero(breaker, "rmsVoltage2")
        else:
            breaker_data["voltage"] = (
                none_to_zero(breaker, "rmsVoltage") * RMS_VOLTAGE_FACTOR
            ) + (none_to_zero(breaker, "rmsVoltage2") * RMS_VOLTAGE_FACTOR)

        if breaker["poles"] == 2:
            breaker_data["frequency"] = (
                none_to_zero(breaker, "lineFrequency")
                + none_to_zero(breaker, "lineFrequency2")
            ) / 2.0
            breaker_data["current"] = (
                none_to_zero(breaker, "rmsCurrent")
                + none_to_zero(breaker, "rmsCurrent2")
            ) / 2
        else:
            breaker_data["frequency"] = none_to_zero(breaker, "lineFrequency")
            breaker_data["current"] = none_to_zero(
                breaker, "rmsCurrent"
            ) + none_to_zero(breaker, "rmsCurrent2")
        if breaker["position"] in LEG1_POSITIONS:
            breaker_data["leg"] = 1
            breaker_data["power1"] = none_to_zero(breaker, "power")
            breaker_data["power2"] = none_to_zero(breaker, "power2")
            breaker_data["voltage1"] = none_to_zero(breaker, "rmsVoltage")
            breaker_data["voltage2"] = none_to_zero(breaker, "rmsVoltage2")
            breaker_data["current1"] = none_to_zero(breaker, "rmsCurrent")
            breaker_data["current2"] = none_to_zero(breaker, "rmsCurrent2")
            breaker_data["frequency1"] = none_to_zero(breaker, "lineFrequency")
            breaker_data["frequency2"] = none_to_zero(breaker, "lineFrequency2")
        else:
            breaker_data["leg"] = 2
            breaker_data["power1"] = none_to_zero(breaker, "power2")
            breaker_data["power2"] = none_to_zero(breaker, "power")
            breaker_data["voltage1"] = none_to_zero(breaker, "rmsVoltage2")
            breaker_data["voltage2"] = none_to_zero(breaker, "rmsVoltage")
            breaker_data["current1"] = none_to_zero(breaker, "rmsCurrent2")
            breaker_data["current2"] = none_to_zero(breaker, "rmsCurrent")
            breaker_data["frequency1"] = none_to_zero(breaker, "lineFrequency2")
            breaker_data["frequency2"] = none_to_zero(breaker, "lineFrequency")
        breakers[breaker["id"]] = breaker_data
    return breakers


def parse_cts(cts_data: list[dict], panel_id: str) -> dict[str, CTData]:
    parsed_data: dict[str, CTData] = {}
    for ct in cts_data:
        if ct["usageType"] == "NOT_USED":
            continue
        ct_data = CTData()
        ct_data["name"] = ct["usageType"]
        ct_data["id"] = str(ct["id"])
        ct_data["panel_id"] = panel_id
        ct_data["channel"] = str(ct["channel"])
        ct_data["power"] = none_to_zero(ct, "activePower") + none_to_zero(
            ct, "activePower2"
        )
        ct_data["consumption"] = none_to_zero(ct, "energyConsumption") + none_to_zero(
            ct, "energyConsumption2"
        )
        ct_data["import"] = none_to_zero(ct, "energyImport") + none_to_zero(
            ct, "energyImport2"
        )
        ct_data["current"] = (
            none_to_zero(ct, "rmsCurrent") + none_to_zero(ct, "rmsCurrent2")
        ) / 2
        ct_data["current1"] = none_to_zero(ct, "rmsCurrent")
        ct_data["current2"] = none_to_zero(ct, "rmsCurrent2")
        # Add the CT to the list.
        parsed_data[ct_data["id"]] = ct_data
    return parsed_data
