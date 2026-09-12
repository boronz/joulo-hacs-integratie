"""Support for Joulo sensors."""
from __future__ import annotations

import logging
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

_LOGGER = logging.getLogger(__name__)

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
        JouloSensor(coordinator, device_info, "Charger Status", "chargers_status", lambda d: d.get("chargers", {}).get("chargers", [{}])[0].get("status"), icon="mdi:ev-station"),
        JouloSensor(coordinator, device_info, "Is Charging", "chargers_is_charging", lambda d: d.get("chargers", {}).get("chargers", [{}])[0].get("is_charging"), icon="mdi:battery-charging"),
        JouloSensor(coordinator, device_info, "Active Session kWh", "chargers_session_kwh", lambda d: float(d.get("chargers", {}).get("chargers", [{}])[0].get("current_session", {}).get("kwh_so_far", 0)), unit="kWh", device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING),

        # Energy & ERE
        JouloSensor(coordinator, device_info, "Total MID kWh", "energy_total_mid_kwh", lambda d: float(d.get("energy", {}).get("total_kwh", 0)), unit="kWh", device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING),
        JouloSensor(coordinator, device_info, "Total ERE Credits", "energy_total_ere", lambda d: float(d.get("energy", {}).get("total_ere_credits", 0)), icon="mdi:certificate", state_class=SensorStateClass.TOTAL_INCREASING),
        JouloSensor(coordinator, device_info, "Total All kWh", "energy_total_all_kwh", lambda d: float(d.get("energy", {}).get("total_kwh_all", 0)), unit="kWh", device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING),

        # Financial ERE-Position
        JouloSensor(coordinator, device_info, "Verwachte Jaaropbrengst", "ere_expected_eur", lambda d: float(d.get("ere", {}).get("total_expected_eur", 0)), unit="€", device_class=SensorDeviceClass.MONETARY),
        JouloSensor(coordinator, device_info, "Al Uitbetaald", "ere_paid_eur", lambda d: float(d.get("ere", {}).get("paid", {}).get("net_eur", 0)), unit="€", device_class=SensorDeviceClass.MONETARY),
        JouloSensor(coordinator, device_info, "Nog Uit Te Betalen", "ere_payable_eur", lambda d: round(float(d.get("ere", {}).get("payable", {}).get("net_eur", 0)) + float(d.get("ere", {}).get("reserved", {}).get("net_eur", 0)), 2), unit="€", device_class=SensorDeviceClass.MONETARY),
        JouloSensor(coordinator, device_info, "Onverkochte ERE", "ere_unsold_credits", lambda d: float(d.get("ere", {}).get("unsold", {}).get("ere", 0)), icon="mdi:certificate-outline"),
        JouloSensor(coordinator, device_info, "Onverkochte Verwachte Opbrengst", "ere_unsold_forecast_eur", lambda d: float(d.get("ere", {}).get("unsold", {}).get("forecast_net_eur", 0)), unit="€", device_class=SensorDeviceClass.MONETARY),
        JouloSensor(coordinator, device_info, "Actuele ERE Marktprijs", "ere_indicative_price", lambda d: float(d.get("ere", {}).get("indicative_price_per_ere", 0)), unit="€/ERE", device_class=SensorDeviceClass.MONETARY),
    ]

    async_add_entities(entities)

class JouloSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Joulo Sensor."""

    def __init__(
        self,
        coordinator,
        device_info: DeviceInfo,
        name: str,
        unique_suffix: str,
        value_fn,
        unit: str | None = None,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
        icon: str | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = f"Joulo {name}"
        self._attr_unique_id = f"joulo_{unique_suffix}"
        self._attr_device_info = device_info
        self._value_fn = value_fn
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_icon = icon

    @property
    def native_value(self):
        """Return the state of the sensor safely."""
        if not self.coordinator.data:
            return None
        try:
            return self._value_fn(self.coordinator.data)
        except (KeyError, IndexError, TypeError, ValueError) as err:
            _LOGGER.debug("Could not extract value for %s: %s", self._attr_name, err)
            return None