"""Notification Channels."""

from enum import Enum
from typing import TYPE_CHECKING, Any, Optional, Union, cast

from camel_converter import to_camel

from validio_sdk.resource._errors import ManifestConfigurationError
from validio_sdk.resource._resource import (
    ApiSecretChangeNestedResource,
    Resource,
    ResourceGraph,
)
from validio_sdk.resource._resource_graph import RESOURCE_GRAPH
from validio_sdk.resource._serde import (
    _api_create_input_params,
    _api_update_input_params,
    _encode_resource,
    decode_nested_objects,
    get_children_node,
    get_config_node,
    with_resource_graph_info,
)

if TYPE_CHECKING:
    from validio_sdk.resource._diff import DiffContext
    from validio_sdk.resource._diffable import Diffable


class EmailChannelSmtpEncryption(str, Enum):
    """Connection encryption mode for an EmailChannel."""

    TLS = "TLS"
    START_TLS = "START_TLS"
    NONE = "NONE"


class Channel(Resource):
    """A notification channel configuration.

    https://docs.validio.io/docs/channels
    """

    def __init__(
        self,
        name: str,
        display_name: str | None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ) -> None:
        """
        Constructor.

        :param name: Unique resource name assigned to the destination
        :param display_name: Human-readable name for the channel. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        :param __internal__: Should be left ignored. This is for internal usage only.
        """
        # Channels are at the root sub-graphs.
        g: ResourceGraph = __internal__ or RESOURCE_GRAPH
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=g,
        )

        self._resource_graph: ResourceGraph = g
        self._resource_graph._add_root(self)

    def _deprecated_secret_fields(self) -> set[str]:
        """Fields that are not supported when calling the secrets changed endpoint.

        :return: Set of secret fields that are deprecated
        """
        return set({})

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _all_fields(self) -> set[str]:
        return {
            *super()._all_fields(),
            *self._secret_fields(),
        }

    def resource_class_name(self) -> str:
        """Returns the base class name."""
        return "Channel"

    def _encode(self) -> dict[str, object]:
        return _encode_resource(self)

    def _api_delete_arguments(self) -> dict[str, str]:
        return {"input": f"{self.resource_class_name()}DeleteInput!"}

    def _api_delete_input(self) -> Any:
        return {"input": {"id": self._must_id()}}

    def _api_create_input(self, namespace: str, _: "DiffContext") -> Any:
        overrides = {
            "namespaceId": namespace,
            **{
                to_camel(f): obj._api_input()
                for f, obj in self._nested_secret_objects().items()
            },
        }
        return _api_create_input_params(
            resource=self, overrides=overrides, skip_fields=self._api_skip_fields()
        )

    def _api_update_input(self, _namespace: str, _ctx: "DiffContext") -> Any:
        overrides = {
            **{
                to_camel(f): obj._api_input()
                for f, obj in self._nested_secret_objects().items()
            }
        }
        return _api_update_input_params(
            resource=self, overrides=overrides, skip_fields=self._api_skip_fields()
        )

    def _api_skip_fields(self) -> set[str]:
        return {
            to_camel(f)
            for f in self._deprecated_secret_fields()
            if not getattr(self, f, None)
        }

    @staticmethod
    def _decode(
        ctx: "DiffContext",
        cls: type,
        obj: dict[str, dict[str, object]],
        g: ResourceGraph,
    ) -> "Channel":
        from validio_sdk.resource.notification_rules import NotificationRule

        args = get_config_node(obj)

        decode_nested_objects(
            obj=args,
            cls_eval=lambda cls_name: eval(cls_name),
        )

        channel = cls(**with_resource_graph_info(args, g))

        # Decode notification rules
        children_obj = cast(dict[str, dict[str, object]], get_children_node(obj))
        notification_rules_obj = cast(
            dict[str, dict[str, object]],
            children_obj.get(NotificationRule.__name__, {}),
        )

        notification_rules = {}
        for rule_name, value in notification_rules_obj.items():
            rule = NotificationRule._decode(ctx, channel, value)
            notification_rules[rule_name] = rule
            ctx.notification_rules[rule_name] = rule

        if len(notification_rules) > 0:
            channel._children[NotificationRule.__name__] = cast(
                dict[str, Resource], notification_rules
            )

        return channel

    def _api_secret_change_response(
        self,
    ) -> dict[str, None | ApiSecretChangeNestedResource]:
        fields = super()._api_secret_change_response()
        for secret_field in self._deprecated_secret_fields():
            if secret_field in fields:
                del fields[secret_field]
        return fields


class SlackChannel(Channel):
    """
    Configuration to send notifications to a Slack channel.

    https://docs.validio.io/docs/slack
    """

    def __init__(
        self,
        *,
        name: str,
        application_link_url: str,
        slack_channel_id: str | None = None,
        token: str | None = None,
        signing_secret: str | None = None,
        app_token: str | None = None,
        interactive_message_enabled: bool | None = None,
        webhook_url: str | None = None,
        display_name: str | None = None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param application_link_url: URL to your Validio application
            instance, used to send notifications.
        :param slack_channel_id: Slack channel ID to send to.
        :param token: Slack API token.
        :param signing_secret: Slack API signing secret. Deprecated.
        :param app_token: App level token used to retrieve user events from Slack.
        :param interactive_message_enabled: If interactive notification messages should
         be used.
        :param webhook_url: Webhook URL provided by Slack to the
            specified Slack channel. (deprecated)
        :param display_name: Human-readable name for the channel. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        """
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=__internal__,
        )
        self.application_link_url = application_link_url
        self.webhook_url = webhook_url
        self.slack_channel_id = slack_channel_id
        self.token = token
        self.signing_secret = signing_secret
        self.app_token = app_token
        self.interactive_message_enabled = interactive_message_enabled

        if self.signing_secret:
            self.add_field_deprecation("signing_secret", "app_token")

        if webhook_url and (
            slack_channel_id
            or token
            or signing_secret
            or interactive_message_enabled
            or app_token
        ):
            raise ManifestConfigurationError(
                f"invalid configuration for Slack channel {self.name}: either"
                " webhook_url or slack_channel_id, token, app_token and"
                " interactive_message_enabled can be used."
            )

        if webhook_url:
            self.add_field_deprecation("webhook_url")

    def _secret_fields(self) -> set[str]:
        # If the webhook URL is set, we return an empty set so that the caller can
        # avoid calling the secrets changed endpoint as it's not supported
        return (
            set({})
            if self.webhook_url
            else {
                "app_token",
                "signing_secret",
                "token",
            }
        )

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{
                "application_link_url",
                "slack_channel_id",
                "interactive_message_enabled",
                *self._deprecated_secret_fields(),
            },
        }

    def _deprecated_secret_fields(self) -> set[str]:
        return {"webhook_url"}


class MsTeamsChannel(Channel):
    """
    Configuration to send notifications to a Microsoft Teams channel.

    https://docs.validio.io/docs/msteams
    """

    def __init__(
        self,
        *,
        name: str,
        application_link_url: str,
        ms_teams_channel_id: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        interactive_message_enabled: bool | None = None,
        webhook_url: str | None = None,
        display_name: str | None = None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param application_link_url: URL to your Validio application
            instance, used to send notifications.
        :param ms_teams_channel_id: Channel ID to send notifications to.
        :param client_id: Client ID for authentication.
        :param client_secret: Client secret for authentication.
        :param interactive_message_enabled: If interactive notification messages should
         be used.
        :param webhook_url: Webhook URL provided by Microsoft Teams to the
            specified channel. (deprecated)
        :param display_name: Human-readable name for the channel. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        """
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=__internal__,
        )
        self.application_link_url = application_link_url
        self.webhook_url = webhook_url
        self.ms_teams_channel_id = ms_teams_channel_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.interactive_message_enabled = interactive_message_enabled

        if webhook_url and (
            ms_teams_channel_id
            or client_id
            or client_secret
            or interactive_message_enabled
        ):
            raise ManifestConfigurationError(
                f"invalid configuration for MS Teams channel {self.name}: either"
                " webhook_url or ms_teams_channel_id, client_id, client_secret,"
                " and interactive_message_enabled can be used."
            )

        if webhook_url:
            self.add_field_deprecation("webhook_url")

    def _secret_fields(self) -> set[str]:
        # If the webhook URL is set, we return an empty set so that the caller can
        # avoid calling the secrets changed endpoint as it's not supported
        return set({}) if self.webhook_url else {"client_id", "client_secret"}

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{
                "application_link_url",
                "ms_teams_channel_id",
                "interactive_message_enabled",
                *self._deprecated_secret_fields(),
            },
        }

    def _deprecated_secret_fields(self) -> set[str]:
        return {"webhook_url"}


class WebhookChannel(Channel):
    """
    Configuration to send notifications to a webhook.

    https://docs.validio.io/docs/webhooks
    """

    def __init__(
        self,
        *,
        name: str,
        application_link_url: str,
        webhook_url: str,
        auth_header: str | None = None,
        display_name: str | None = None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param application_link_url: URL to your Validio application
            instance, used to send notifications.
        :param webhook_url: Webhook URL to the specified HTTP endpoint.
        :param auth_header: Signature to include in the authorization
            header sent to the HTTP endpoint.
        :param display_name: Human-readable name for the channel. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        """
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=__internal__,
        )
        self.application_link_url = application_link_url
        self.webhook_url = webhook_url
        self.auth_header = auth_header

    def _secret_fields(self) -> set[str]:
        return {"auth_header", "webhook_url"}

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{"application_link_url"},
        }


class EmailChannelAuthSmtpUserPassword(ApiSecretChangeNestedResource):
    """
    Credential configuration for an Email channel resource.

    Contains configuration based on SMTP user-password authentication.
    """

    def __init__(
        self,
        *,
        address: str,
        port: int,
        encryption: EmailChannelSmtpEncryption,
        username: str | None,
        password: str | None,
    ):
        """
        Constructor.

        :param address: The hostname or IP address of the SMTP server.
        :param port: Port number where the SMTP server is hosted.
        :param encryption: Connection encryption mode towards the SMTP server.
        :param username: Username to log in with the email provider.
        :param password: Password associated with the provided login username.
        """
        self.address = address
        self.port = port
        self.encryption = encryption
        self.username = username
        self.password = password

    def _api_variant_name(self) -> str:
        return "smtpUserPassword"

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {"address", "port", "encryption", "username"}

    def _secret_fields(self) -> set[str]:
        return {"password"}

    def _nested_objects(
        self,
    ) -> dict[str, Optional["Diffable | list[Diffable]"] | None]:
        return {}


EmailChannelAuth = Union[EmailChannelAuthSmtpUserPassword]


class EmailChannel(Channel):
    """Configuration to send notifications via email."""

    def __init__(
        self,
        *,
        name: str,
        application_link_url: str,
        sender_address: str,
        recipient_addresses: list[str],
        auth: EmailChannelAuth,
        interactive_message_enabled: bool = True,
        display_name: str | None = None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param application_link_url: URL to your Validio application
            instance, used to send notifications.
        :param sender_address: The address to use to send
            emails. e.g. `validio@acme.com`
        :param recipient_addresses: One or more recipient addresses to
            receive email messages. e.g. `incidents@acme.com`
        :param auth: Credentials to use for authentication.
        :param interactive_message_enabled:
        :param display_name: Human-readable name for the channel. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        """
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=__internal__,
        )
        self.application_link_url = application_link_url
        self.sender_address = sender_address
        self.recipient_addresses = recipient_addresses
        self.auth = auth
        self.interactive_message_enabled = interactive_message_enabled

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{
                "application_link_url",
                "sender_address",
                "recipient_addresses",
                "interactive_message_enabled",
            },
        }

    def _secret_fields(self) -> set[str]:
        return set()

    def _nested_objects(
        self,
    ) -> dict[str, Optional["Diffable | list[Diffable]"] | None]:
        return {"auth": self.auth}
