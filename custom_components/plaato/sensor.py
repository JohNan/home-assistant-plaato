"""Support for Plaato Airlock sensors."""

import logging

from homeassistant.const import CONF_TOKEN, UNIT_PERCENTAGE
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)

from . import (
    ATTR_ABV,
    ATTR_BATCH_VOLUME,
    ATTR_BPM,
    ATTR_CO2_VOLUME,
    ATTR_TEMP,
    ATTR_TEMP_UNIT,
    ATTR_VOLUME_UNIT,
    PLAATO_DEVICE_ATTRS,
    PLAATO_DEVICE_SENSORS,
    SENSOR_DATA_KEY,
    SENSOR_UPDATE,
)
from .const import CONF_DEVICE_NAME, CONF_USE_WEBHOOK, DOMAIN
from .entity import PlaatoEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Plaato sensor."""


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Set up Plaato from a config entry."""
    devices = {}

    def get_device(device_id):
        """Get a device."""
        return hass.data[DOMAIN].get(device_id, False)

    def get_device_sensors(device_id):
        """Get device sensors."""
        return hass.data[DOMAIN].get(device_id).get(PLAATO_DEVICE_SENSORS)

    async def _update_sensor(device_id):
        """Update/Create the sensors."""
        if device_id not in devices and get_device(device_id):
            entities = []
            sensors = get_device_sensors(device_id)

            for sensor_type in sensors:
                entities.append(PlaatoSensor(device_id, sensor_type, device_id))

            devices[device_id] = entities

            async_add_devices(entities, True)
        else:
            for entity in devices[device_id]:
                async_dispatcher_send(hass, f"{DOMAIN}_{entity.unique_id}")

    if config_entry.data.get(CONF_USE_WEBHOOK, False):
        hass.data[SENSOR_DATA_KEY] = async_dispatcher_connect(
            hass, SENSOR_UPDATE, _update_sensor
        )
    else:
        coordinator = hass.data[DOMAIN][config_entry.entry_id]
        if coordinator.data is not None:
            async_add_devices(
                PlaatoSensor(
                    config_entry.data[CONF_TOKEN],
                    sensor_type,
                    config_entry.data[CONF_DEVICE_NAME],
                    coordinator,
                )
                for sensor_type in coordinator.data.sensors.keys()
            )

    return True


class PlaatoSensor(PlaatoEntity):
    """Representation of a Plaato Sensor."""

    def get_sensors(self):
        """Get device sensors. (Only webhook)."""
        return (
            self.hass.data[DOMAIN]
            .get(self._device_id, False)
            .get(PLAATO_DEVICE_SENSORS, False)
        )

    def get_sensors_unit_of_measurement(self, sensor_type):
        """Get unit of measurement for sensor of type. (Only webhook)."""
        return (
            self.hass.data[DOMAIN]
            .get(self._device_id)
            .get(PLAATO_DEVICE_ATTRS, [])
            .get(sensor_type, "")
        )

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._coordinator is not None:
            return self._coordinator.data.sensors.get(self._sensor_type)

        sensors = self.get_sensors()
        if sensors is False:
            _LOGGER.debug("Device with %s has no sensors.", self.name)
            return 0

        if self._sensor_type == ATTR_ABV:
            return round(sensors.get(self._sensor_type), 2)
        if self._sensor_type == ATTR_TEMP:
            return round(sensors.get(self._sensor_type), 1)
        if self._sensor_type == ATTR_CO2_VOLUME:
            return round(sensors.get(self._sensor_type), 2)
        return sensors.get(self._sensor_type)

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        if self._coordinator is not None:
            return self._coordinator.data.get_unit_of_measurement(self._sensor_type)

        if self._sensor_type == ATTR_TEMP:
            return self.get_sensors_unit_of_measurement(ATTR_TEMP_UNIT)
        if (
            self._sensor_type == ATTR_BATCH_VOLUME
            or self._sensor_type == ATTR_CO2_VOLUME
        ):
            return self.get_sensors_unit_of_measurement(ATTR_VOLUME_UNIT)
        if self._sensor_type == ATTR_BPM:
            return "bpm"
        if self._sensor_type == ATTR_ABV:
            return UNIT_PERCENTAGE

        return ""
