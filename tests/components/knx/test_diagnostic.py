"""Tests for the diagnostics data provided by the KNX integration."""
from unittest.mock import patch

from xknx.io import DEFAULT_MCAST_GRP, DEFAULT_MCAST_PORT

from homeassistant.components.knx.const import (
    CONF_KNX_AUTOMATIC,
    CONF_KNX_CONNECTION_TYPE,
    CONF_KNX_DEFAULT_RATE_LIMIT,
    CONF_KNX_DEFAULT_STATE_UPDATER,
    CONF_KNX_INDIVIDUAL_ADDRESS,
    CONF_KNX_KNXKEY_PASSWORD,
    CONF_KNX_MCAST_GRP,
    CONF_KNX_MCAST_PORT,
    CONF_KNX_RATE_LIMIT,
    CONF_KNX_ROUTING_BACKBONE_KEY,
    CONF_KNX_SECURE_DEVICE_AUTHENTICATION,
    CONF_KNX_SECURE_USER_PASSWORD,
    CONF_KNX_STATE_UPDATER,
    DEFAULT_ROUTING_IA,
    DOMAIN as KNX_DOMAIN,
)
from homeassistant.core import HomeAssistant

from .conftest import KNXTestKit

from tests.common import MockConfigEntry
from tests.components.diagnostics import get_diagnostics_for_config_entry
from tests.typing import ClientSessionGenerator


async def test_diagnostics(
    hass: HomeAssistant,
    hass_client: ClientSessionGenerator,
    mock_config_entry: MockConfigEntry,
    knx: KNXTestKit,
):
    """Test diagnostics."""
    await knx.setup_integration({})

    with patch("homeassistant.config.async_hass_config_yaml", return_value={}):
        # Overwrite the version for this test since we don't want to change this with every library bump
        knx.xknx.version = "1.0.0"
        assert await get_diagnostics_for_config_entry(
            hass, hass_client, mock_config_entry
        ) == {
            "config_entry_data": {
                "connection_type": "automatic",
                "individual_address": "0.0.240",
                "multicast_group": "224.0.23.12",
                "multicast_port": 3671,
                "rate_limit": 0,
                "state_updater": True,
            },
            "configuration_error": None,
            "configuration_yaml": None,
            "xknx": {"current_address": "0.0.0", "version": "1.0.0"},
        }


async def test_diagnostic_config_error(
    hass: HomeAssistant,
    hass_client: ClientSessionGenerator,
    mock_config_entry: MockConfigEntry,
    knx: KNXTestKit,
):
    """Test diagnostics."""
    await knx.setup_integration({})

    with patch(
        "homeassistant.config.async_hass_config_yaml",
        return_value={"knx": {"wrong_key": {}}},
    ):
        # Overwrite the version for this test since we don't want to change this with every library bump
        knx.xknx.version = "1.0.0"
        assert await get_diagnostics_for_config_entry(
            hass, hass_client, mock_config_entry
        ) == {
            "config_entry_data": {
                "connection_type": "automatic",
                "individual_address": "0.0.240",
                "multicast_group": "224.0.23.12",
                "multicast_port": 3671,
                "rate_limit": 0,
                "state_updater": True,
            },
            "configuration_error": "extra keys not allowed @ data['knx']['wrong_key']",
            "configuration_yaml": {"wrong_key": {}},
            "xknx": {"current_address": "0.0.0", "version": "1.0.0"},
        }


async def test_diagnostic_redact(
    hass: HomeAssistant,
    hass_client: ClientSessionGenerator,
):
    """Test diagnostics redacting data."""
    mock_config_entry: MockConfigEntry = MockConfigEntry(
        title="KNX",
        domain=KNX_DOMAIN,
        data={
            CONF_KNX_CONNECTION_TYPE: CONF_KNX_AUTOMATIC,
            CONF_KNX_RATE_LIMIT: CONF_KNX_DEFAULT_RATE_LIMIT,
            CONF_KNX_STATE_UPDATER: CONF_KNX_DEFAULT_STATE_UPDATER,
            CONF_KNX_MCAST_PORT: DEFAULT_MCAST_PORT,
            CONF_KNX_MCAST_GRP: DEFAULT_MCAST_GRP,
            CONF_KNX_INDIVIDUAL_ADDRESS: DEFAULT_ROUTING_IA,
            CONF_KNX_KNXKEY_PASSWORD: "password",
            CONF_KNX_SECURE_USER_PASSWORD: "user_password",
            CONF_KNX_SECURE_DEVICE_AUTHENTICATION: "device_authentication",
            CONF_KNX_ROUTING_BACKBONE_KEY: "bbaacc44bbaacc44bbaacc44bbaacc44",
        },
    )
    knx: KNXTestKit = KNXTestKit(hass, mock_config_entry)
    await knx.setup_integration({})

    with patch("homeassistant.config.async_hass_config_yaml", return_value={}):
        # Overwrite the version for this test since we don't want to change this with every library bump
        knx.xknx.version = "1.0.0"
        assert await get_diagnostics_for_config_entry(
            hass, hass_client, mock_config_entry
        ) == {
            "config_entry_data": {
                "connection_type": "automatic",
                "individual_address": "0.0.240",
                "multicast_group": "224.0.23.12",
                "multicast_port": 3671,
                "rate_limit": 0,
                "state_updater": True,
                "knxkeys_password": "**REDACTED**",
                "user_password": "**REDACTED**",
                "device_authentication": "**REDACTED**",
                "backbone_key": "**REDACTED**",
            },
            "configuration_error": None,
            "configuration_yaml": None,
            "xknx": {"current_address": "0.0.0", "version": "1.0.0"},
        }
