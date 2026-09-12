"""Support for Joulo sensors."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Joulo sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name="Joulo",
        manufacturer="Joulo",
        model="Smart Energy & ERE Monitor",
    )

    entities = [
        # Chargers
        JouloSensor(coordinator, device_info, "Charger Status", "chargers", lambda d: d["chargers"]["chargers"][0]["status"], icon="mdi:ev-station"),
        JouloSensor(coordinator, device_info, "Is Charging", "chargers", lambda d: d["chargers"]["chargers"][0]["is_charging"], icon="mdi:battery-charging"),
        JouloSensor(coordinator, device_info, "Active Session kWh", "chargers", lambda d: d["chargers"]["chargers"][0]["current_session"]["kwh_so_far"], unit="kWh", device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING),

        # Energy & ERE
        JouloSensor(coordinator, device_info, "Total MID kWh", "energy", lambda d: d["energy"]["total_kwh"], unit="kWh", device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING),
        JouloSensor(coordinator, device_info, "Total ERE Credits", "energy", lambda d: d["energy"]["total_ere_credits"], icon="mdi:certificate", state_class=SensorStateClass.TOTAL_INCREASING),
        JouloSensor(coordinator, device_info, "Total All kWh", "energy", lambda d: d["energy"]["total_kwh_all"], unit="kWh", device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING),

        # Financial ERE-Position
        JouloSensor(coordinator, device_info, "Verwachte Jaaropbrengst", "ere", lambda d: d["ere"]["total_expected_eur"], unit="€", device_class=SensorDeviceClass.MONETARY),
        JouloSensor(coordinator, device_info, "Al Uitbetaald", "ere", lambda d: d["ere"]["paid"]["net_eur"], unit="€", device_class=SensorDeviceClass.MONETARY),
        JouloSensor(coordinator, device_info, "Nog Uit Te Betalen", "ere", lambda d: round(float(d["ere"]["payable"]["net_eur"]) + float(d["ere"]["reserved"]["net_eur"]), 2), unit="€", device_class=SensorDeviceClass.MONETARY),
        JouloSensor(coordinator, device_info, "Onverkochte ERE", "ere", lambda d: d["ere"]["unsold"]["ere"], icon="mdi:certificate-outline"),
        JouloSensor(coordinator, device_info, "Onverkochte Verwachte Opbrengst", "ere", lambda d: d["ere"]["unsold"]["forecast_net_eur"], unit="€", device_class=SensorDeviceClass.MONETARY),
        JouloSensor(coordinator, device_info, "Actuele ERE Marktprijs", "ere", lambda d: d["ere"]["indicative_price_per_ere"], unit="€/ERE", device_class=SensorDeviceClass.MONETARY),
    ]

    async_add_entities(entities)

class JouloSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Joulo Sensor."""

    def __init__(
        self,
        coordinator,
        device_info: DeviceInfo,
        name: str,
        category: str,
        value_fn,
        unit: str | None = None,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
        icon: str | None = None,
    ) -> None:

        super().__init__(coordinator)
        self._attr_name = f"Joulo {name}"
        self._attr_unique_id = f"joulo_{category}_{name.lower().replace(' ', '_')}"
        self._attr_device_info = device_info
        self._value_fn = value_fn
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_icon = icon

    @property
    def native_value(self):
        """Return the state of the sensor."""
        try:
            return self._value_fn(self.coordinator.data)
        except (KeyError, IndexError, TypeError):
            return None