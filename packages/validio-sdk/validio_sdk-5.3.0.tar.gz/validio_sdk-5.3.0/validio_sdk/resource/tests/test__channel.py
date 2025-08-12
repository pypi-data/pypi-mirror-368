import pytest

from validio_sdk.resource._errors import ManifestConfigurationError

# We need validio_sdk in scope due to eval.
# ruff: noqa: F401
from validio_sdk.resource.channels import MsTeamsChannel, SlackChannel


@pytest.mark.parametrize(
    ("channel_type", "config"),
    [
        # Slack channel - Using webhook URL and Slack channel ID, token, signing
        # secret, and interactive message enabled
        (
            "SlackChannel",
            {
                "name": "ch1",
                "application_link_url": "app",
                "slack_channel_id": "sid",
                "webhook_url": "webhook",
                "display_name": "name",
                "token": "token",
                "signing_secret": "secret",
                "interactive_message_enabled": True,
            },
        ),
        # Slack channel - Using webhook URL and Slack channel ID
        (
            "SlackChannel",
            {
                "name": "ch2",
                "application_link_url": "app",
                "slack_channel_id": "sid",
                "webhook_url": "webhook",
                "display_name": "name",
            },
        ),
        # Slack channel - Using webhook URL and token
        (
            "SlackChannel",
            {
                "name": "ch3",
                "application_link_url": "app",
                "webhook_url": "webhook",
                "display_name": "name",
                "token": "token",
            },
        ),
        # Slack channel - Using webhook URL and signing secret
        (
            "SlackChannel",
            {
                "name": "ch4",
                "application_link_url": "app",
                "webhook_url": "webhook",
                "display_name": "name",
                "signing_secret": "secret",
            },
        ),
        # Slack channel - Using webhook URL and interactive message enabled
        (
            "SlackChannel",
            {
                "name": "ch5",
                "application_link_url": "app",
                "webhook_url": "webhook",
                "display_name": "name",
                "interactive_message_enabled": True,
            },
        ),
        # MS Teams Channel - Using webhook URL with MS teams channel ID, client ID,
        # client secret, and interactive message enabled
        (
            "MsTeamsChannel",
            {
                "name": "ch6",
                "application_link_url": "app",
                "ms_teams_channel_id": "cid",
                "webhook_url": "webhook",
                "display_name": "name",
                "client_id": "id",
                "client_secret": "secret",
                "interactive_message_enabled": True,
            },
        ),
        # MS Teams Channel - Using webhook URL and MS teams channel ID
        (
            "MsTeamsChannel",
            {
                "name": "ch7",
                "application_link_url": "app",
                "ms_teams_channel_id": "cid",
                "webhook_url": "webhook",
                "display_name": "name",
            },
        ),
        # MS Teams Channel - Using webhook URL and client ID
        (
            "MsTeamsChannel",
            {
                "name": "ch8",
                "application_link_url": "app",
                "webhook_url": "webhook",
                "display_name": "name",
                "client_id": "id",
            },
        ),
        # MS Teams Channel - Using webhook URL and client secret
        (
            "MsTeamsChannel",
            {
                "name": "ch9",
                "application_link_url": "app",
                "webhook_url": "webhook",
                "display_name": "name",
                "client_secret": "secret",
            },
        ),
        # MS Teams Channel - Using webhook URL and interactive message enabled
        (
            "MsTeamsChannel",
            {
                "name": "ch10",
                "application_link_url": "app",
                "webhook_url": "webhook",
                "display_name": "name",
                "interactive_message_enabled": True,
            },
        ),
    ],
)
def test_should_raise_error_when_channel_with_invalid_config(
    channel_type: str, config: dict[str, str]
) -> None:
    with pytest.raises(ManifestConfigurationError):
        eval(channel_type)(**config)
