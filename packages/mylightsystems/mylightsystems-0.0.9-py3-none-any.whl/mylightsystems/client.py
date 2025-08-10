"""Client for MyLightSystems API."""

from __future__ import annotations

import asyncio
import logging
import socket
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from aiohttp import ClientError, ClientResponseError, ClientSession
from aiohttp.hdrs import METH_GET
from yarl import URL

from mylightsystems.const import (
    AUTH_URL,
    DEFAULT_BASE_URL,
    DEVICES_URL,
    MEASURES_TOTAL_URL,
    PROFILE_URL,
    STATES_URL,
    SWITCH_URL,
)
from mylightsystems.device_factory import DeviceFactory
from mylightsystems.exceptions import (
    MyLightSystemsConnectionError,
    MyLightSystemsInvalidAuthError,
    MyLightSystemsMeasuresTotalNotSupportedError,
    MyLightSystemsSwitchNotAllowedError,
    MyLightSystemsUnauthorizedError,
    MyLightSystemsUnknownDeviceError,
)
from mylightsystems.models import (
    Auth,
    Device,
    DeviceState,
    Measure,
    Profile,
    SensorMeasure,
    SensorState,
    SwitchState,
)

if TYPE_CHECKING:
    from typing import Self

_LOGGER = logging.getLogger(__name__)


@dataclass
class MyLightSystemsApiClient:
    """Main class for handling communication with MyLightSystems API."""

    base_url: str = DEFAULT_BASE_URL
    session: ClientSession | None = None
    request_timeout: int = 10
    _close_session: bool = False

    async def _request(
        self,
        uri: str,
        *,
        method: str = METH_GET,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Handle a request to the MyLightSystems API."""
        url = URL(self.base_url).with_path(uri)

        headers = {
            "Content-Type": "application/json",
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.request(method, url, headers=headers, params=params)

                _LOGGER.debug("Data retrieved from %s, status: %s", url, response.status)

                response.raise_for_status()

                json_response = await response.json()

                _LOGGER.debug("Response: %s", json_response)

                if json_response["status"] == "error" and json_response["error"] == "not.authorized":
                    raise MyLightSystemsUnauthorizedError

                return json_response

        except TimeoutError as exception:
            msg = "Timeout occurred while connecting to the device"
            raise MyLightSystemsConnectionError(msg) from exception
        except (
            ClientError,
            ClientResponseError,
            socket.gaierror,
        ) as exception:
            msg = "Error occurred while communicating with the device"
            raise MyLightSystemsConnectionError(msg) from exception

    async def auth(self, email: str, password: str) -> Auth:
        """Login to MyLightSystems API."""
        response = await self._request(
            AUTH_URL,
            params={"email": email, "password": password},
        )

        if response["status"] == "error" and response["error"] in (
            "invalid.credentials",
            "undefined.email",
            "undefined.password",
        ):
            raise MyLightSystemsInvalidAuthError

        return Auth(token=response["authToken"])

    async def get_profile(self, auth_token: str) -> Profile:
        """Get user profile."""
        response = await self._request(
            PROFILE_URL,
            params={"authToken": auth_token},
        )

        return Profile(
            id=response["id"],
            grid_type=response["gridType"],
            tenant=response["tenant"],
            city=response["city"],
            country=response["country"],
            postal_code=response["postalCode"],
            address=response["address"],
        )

    async def get_devices(self, auth_token: str) -> list[Device]:
        """Get devices."""
        response = await self._request(
            DEVICES_URL,
            params={"authToken": auth_token},
        )

        device_factory = DeviceFactory()

        return [device_factory.create_device(data=device) for device in response["devices"]]

    async def get_measures_total(self, auth_token: str, device_id: str) -> list[Measure]:
        """Get measures total."""
        response = await self._request(
            MEASURES_TOTAL_URL,
            params={"authToken": auth_token, "deviceId": device_id},
        )

        if response["status"] == "error" and response["error"] == "device.not.supports.total.measures":
            raise MyLightSystemsMeasuresTotalNotSupportedError

        return [
            Measure(type=measure["type"], unit=measure["unit"], value=measure["value"])
            for measure in response.get("measure", {}).get("values", [])
        ]

    async def get_states(self, auth_token: str) -> list[DeviceState]:
        """Get states."""
        response = await self._request(
            STATES_URL,
            params={"authToken": auth_token},
        )

        return [
            DeviceState(
                device_id=device_state["deviceId"],
                report_period=device_state["effectiveReportPeriod"],
                sensor_states=[
                    SensorState(
                        sensor_id=sensor_state["sensorId"],
                        measure=SensorMeasure(
                            value=sensor_state["measure"]["value"],
                            type=sensor_state["measure"].get("type", None),
                            unit=sensor_state["measure"].get("unit", None),
                            date=sensor_state["measure"]["date"],
                        ),
                    )
                    for sensor_state in device_state["sensorStates"]
                ],
                state=device_state["state"].lower() == "on",
            )
            for device_state in response["deviceStates"]
        ]

    async def switch(self, auth_token: str, device_id: str, value: bool) -> SwitchState:  # noqa: FBT001
        """Change switch state."""
        response = await self._request(
            SWITCH_URL,
            params={"authToken": auth_token, "id": device_id, "on": str(value).lower()},
        )

        if response["status"] == "error":
            if response["error"] == "switch.not.allowed":
                raise MyLightSystemsSwitchNotAllowedError
            if response["error"] == "device.not.found":
                raise MyLightSystemsUnknownDeviceError

        return SwitchState(state=response["state"] == "on")

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        """Async enter.

        Returns
        -------
            The AirGradientClient object.

        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.

        """
        await self.close()
