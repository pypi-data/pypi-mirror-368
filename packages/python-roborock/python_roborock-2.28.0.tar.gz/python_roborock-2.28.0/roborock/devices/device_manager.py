"""Module for discovering Roborock devices."""

import asyncio
import logging
from collections.abc import Awaitable, Callable

from roborock.containers import (
    HomeData,
    HomeDataDevice,
    HomeDataProduct,
    UserData,
)
from roborock.devices.device import DeviceVersion, RoborockDevice
from roborock.mqtt.roborock_session import create_mqtt_session
from roborock.mqtt.session import MqttSession
from roborock.protocol import create_mqtt_params
from roborock.web_api import RoborockApiClient

from .v1_channel import create_v1_channel

_LOGGER = logging.getLogger(__name__)

__all__ = [
    "create_device_manager",
    "create_home_data_api",
    "DeviceManager",
    "HomeDataApi",
    "DeviceCreator",
]


HomeDataApi = Callable[[], Awaitable[HomeData]]
DeviceCreator = Callable[[HomeDataDevice, HomeDataProduct], RoborockDevice]


class DeviceManager:
    """Central manager for Roborock device discovery and connections."""

    def __init__(
        self,
        home_data_api: HomeDataApi,
        device_creator: DeviceCreator,
        mqtt_session: MqttSession,
    ) -> None:
        """Initialize the DeviceManager with user data and optional cache storage.

        This takes ownership of the MQTT session and will close it when the manager is closed.
        """
        self._home_data_api = home_data_api
        self._device_creator = device_creator
        self._devices: dict[str, RoborockDevice] = {}
        self._mqtt_session = mqtt_session

    async def discover_devices(self) -> list[RoborockDevice]:
        """Discover all devices for the logged-in user."""
        home_data = await self._home_data_api()
        device_products = home_data.device_products
        _LOGGER.debug("Discovered %d devices %s", len(device_products), home_data)

        # These are connected serially to avoid overwhelming the MQTT broker
        new_devices = {}
        for duid, (device, product) in device_products.items():
            if duid in self._devices:
                continue
            new_device = self._device_creator(device, product)
            await new_device.connect()
            new_devices[duid] = new_device

        self._devices.update(new_devices)
        return list(self._devices.values())

    async def get_device(self, duid: str) -> RoborockDevice | None:
        """Get a specific device by DUID."""
        return self._devices.get(duid)

    async def get_devices(self) -> list[RoborockDevice]:
        """Get all discovered devices."""
        return list(self._devices.values())

    async def close(self) -> None:
        """Close all MQTT connections and clean up resources."""
        tasks = [device.close() for device in self._devices.values()]
        self._devices.clear()
        tasks.append(self._mqtt_session.close())
        await asyncio.gather(*tasks)


def create_home_data_api(email: str, user_data: UserData) -> HomeDataApi:
    """Create a home data API wrapper.

    This function creates a wrapper around the Roborock API client to fetch
    home data for the user.
    """

    # Note: This will auto discover the API base URL. This can be improved
    # by caching this next to `UserData` if needed to avoid unnecessary API calls.
    client = RoborockApiClient(email)

    async def home_data_api() -> HomeData:
        return await client.get_home_data(user_data)

    return home_data_api


async def create_device_manager(user_data: UserData, home_data_api: HomeDataApi) -> DeviceManager:
    """Convenience function to create and initialize a DeviceManager.

    The Home Data is fetched using the provided home_data_api callable which
    is exposed this way to allow for swapping out other implementations to
    include caching or other optimizations.
    """

    mqtt_params = create_mqtt_params(user_data.rriot)
    mqtt_session = await create_mqtt_session(mqtt_params)

    def device_creator(device: HomeDataDevice, product: HomeDataProduct) -> RoborockDevice:
        # Check device version and only support V1 for now
        if device.pv != DeviceVersion.V1.value:
            raise NotImplementedError(
                f"Device {device.name} has version {device.pv}, but only V1 devices "
                f"are supported through the unified interface."
            )
        # Create V1 channel that handles both MQTT and local connections
        v1_channel = create_v1_channel(user_data, mqtt_params, mqtt_session, device)
        return RoborockDevice(user_data, device, product, v1_channel)

    manager = DeviceManager(home_data_api, device_creator, mqtt_session=mqtt_session)
    await manager.discover_devices()
    return manager
