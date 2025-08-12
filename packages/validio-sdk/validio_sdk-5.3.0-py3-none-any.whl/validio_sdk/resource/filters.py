"""Filters configuration."""

from abc import abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

from validio_sdk.exception import ValidioBugError
from validio_sdk.resource._diffable import Diffable
from validio_sdk.resource._errors import ManifestConfigurationError
from validio_sdk.resource._resource import Resource, ResourceGraph
from validio_sdk.resource._serde import (
    CONFIG_FIELD_NAME,
    NODE_TYPE_FIELD_NAME,
    _api_create_input_params,
    _encode_resource,
    get_config_node,
)

if TYPE_CHECKING:
    from validio_sdk.resource._diff import DiffContext
    from validio_sdk.resource.sources import Source


# used to detect when we're in resource vs filter expression mode.
DUMMY_NAME_PLACEHOLDER = "_validio_dummy_filter"


class Filter(Resource):
    """
    Base class for a filter configuration.

    https://docs.validio.io/docs/filters
    """

    def __init__(
        self,
        name: str | None = None,
        source: Optional["Source"] = None,
        display_name: str | None = None,
        ignore_changes: bool = False,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the filter
        :param source: The source to attach the filter to
        :param display_name: Human-readable name for the filter. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored
        """
        # For backwards compatibility while we transition from
        # JSONFilterExpression to Filter resources, the Filter class
        # is able to optionally act as a resource.
        if (source is None) and (name is not None and name != DUMMY_NAME_PLACEHOLDER):
            raise ManifestConfigurationError(
                f"invalid {self.__class__.__name__}: "
                "name and source arguments must be provided together."
            )

        # If in JSONFilterExpression mode, we initialize the base
        # resource with an empty resource graph and a random name.
        # Both values are simply placeholders and are ignored in this
        # mode.
        resource_graph = (
            source._resource_graph if source is not None else ResourceGraph()
        )

        super().__init__(
            name=name or DUMMY_NAME_PLACEHOLDER,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=resource_graph,
        )

        # If in Resource mode, then we add it as usual to the graph
        # as a child of the source.
        if source is not None:
            self.source_name: str = source.name
            source.add(self.name, self)

    def _in_resource_mode(self) -> bool:
        """Returns true if the filter is in resource mode."""
        return self.name != DUMMY_NAME_PLACEHOLDER

    def _immutable_fields(self) -> set[str]:
        if self._in_resource_mode():
            return {"source_name"}

        return set({})

    def _mutable_fields(self) -> set[str]:
        if self._in_resource_mode():
            return super()._mutable_fields()

        return set({})

    def _nested_objects(self) -> dict[str, Diffable | list[Diffable] | None]:
        return {}

    def resource_class_name(self) -> str:
        """Returns the base class name."""
        return "Filter"

    @abstractmethod
    def _scalar(self) -> dict[str, object]:
        """
        Returns the JsonFilterExpression representation of this filter.
        For backwards compatibility while we transition to filter resources.
        """

    def _encode(self) -> dict[str, object]:
        if self._in_resource_mode():
            # Drop fields here that are not part of the constructor for when
            # we deserialize back. They will be reinitialized by the constructor.
            return _encode_resource(self, skip_fields={"source_name"})

        data = self._scalar()
        data[NODE_TYPE_FIELD_NAME] = self.__class__.__name__
        data["name"] = self.name

        return data

    @staticmethod
    def _decode(
        obj: dict[str, Any],
        source: Optional["Source"] = None,
    ) -> "Filter":
        cls = eval(obj[NODE_TYPE_FIELD_NAME])

        in_resource_mode = CONFIG_FIELD_NAME in obj

        if in_resource_mode:
            if source is None:
                raise ValidioBugError(
                    "Missing source when decoding filter in resource mode"
                )
            args = get_config_node(obj)
            return cls(**{**args, "source": source})

        return cls(**{k: v for k, v in obj.items() if k != NODE_TYPE_FIELD_NAME})

    def _api_create_input(self, _namespace: str, ctx: "DiffContext") -> dict[str, Any]:
        return _api_create_input_params(
            self,
            overrides={"sourceId": ctx.sources[self.source_name]._must_id()},
        )

    def _api_json_filter_expression_create_input(self) -> dict[str, Any]:
        return {"__typename": f"{self.__class__.__name__}Expression", **self._scalar()}


class BooleanFilterOperator(str, Enum):
    """
    Configures the behavior of a Boolean filter.

    IS_TRUE: Allow values equal to TRUE
    IS_FALSE: Allow values equal to FALSE
    """

    IS_TRUE = "IS_TRUE"
    IS_FALSE = "IS_FALSE"


class BooleanFilter(Filter):
    """A Boolean filter configuration.

    https://docs.validio.io/docs/filters#boolean-filter
    """

    def __init__(
        self,
        *,
        field: str,
        operator: BooleanFilterOperator,
        name: str | None = None,
        source: Optional["Source"] = None,
        display_name: str | None = None,
        ignore_changes: bool = False,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the filter
        :param source: The source to attach the filter to
        :param display_name: Human-readable name for the filter. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored
        :param field: Field to be filtered on.
        :param operator: Operator to allow TRUE or FALSE values.
        """
        super().__init__(
            name=name,
            source=source,
            display_name=display_name,
            ignore_changes=ignore_changes,
        )

        self.field = field
        self.operator = (
            BooleanFilterOperator(operator)
            if not isinstance(operator, BooleanFilterOperator)
            else operator
        )

    def _mutable_fields(self) -> set[str]:
        return {"field", "operator", *super()._mutable_fields()}

    def _scalar(self) -> dict[str, object]:
        return {"field": self.field, "operator": self.operator.value}


class NullFilterOperator(str, Enum):
    """
    Configures the behavior of a Null filter.

    IS: Filter in NULL values
    IS_NOT: Filter in Non-NULL values
    """

    IS = "IS"
    IS_NOT = "IS_NOT"


class NullFilter(Filter):
    """A Null filter configuration.

    https://docs.validio.io/docs/filters#null
    """

    def __init__(
        self,
        *,
        field: str,
        operator: NullFilterOperator = NullFilterOperator.IS,
        name: str | None = None,
        source: Optional["Source"] = None,
        display_name: str | None = None,
        ignore_changes: bool = False,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the filter
        :param source: The source to attach the filter to
        :param display_name: Human-readable name for the filter. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored
        :param field: Field to be filtered on.
        :param operator: Operator to allow NULL or non-NULL values.
        """
        super().__init__(
            name=name,
            source=source,
            display_name=display_name,
            ignore_changes=ignore_changes,
        )

        self.field = field
        self.operator = (
            NullFilterOperator(operator)
            if not isinstance(operator, NullFilterOperator)
            else operator
        )

    def _mutable_fields(self) -> set[str]:
        return {"field", "operator", *super()._mutable_fields()}

    def _scalar(self) -> dict[str, object]:
        return {"field": self.field, "operator": self.operator.value}


class EnumFilterOperator(str, Enum):
    """
    Configures the behavior of an Enum filter.

    ALLOW: Allow values in the enum
    DENY: Deny values in the enum
    """

    ALLOW = "ALLOW"
    DENY = "DENY"


class EnumFilter(Filter):
    """An Enum filter configuration.

    https://docs.validio.io/docs/filters#enum
    """

    def __init__(
        self,
        *,
        field: str,
        values: list[str],
        operator: EnumFilterOperator = EnumFilterOperator.ALLOW,
        name: str | None = None,
        source: Optional["Source"] = None,
        display_name: str | None = None,
        ignore_changes: bool = False,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the filter
        :param source: The source to attach the filter to
        :param display_name: Human-readable name for the filter. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored
        :param field: Field to be filtered on.
        :param values: An explicit list of value to filter with.
        :param operator: Operator to allow or reject values
            found in the specified list.
        """
        super().__init__(
            name=name,
            source=source,
            display_name=display_name,
            ignore_changes=ignore_changes,
        )

        # Ensure we use deterministic ordering when diffing the values list.
        values.sort()
        self.values = values

        self.field = field
        self.operator = (
            EnumFilterOperator(operator)
            if not isinstance(operator, EnumFilterOperator)
            else operator
        )

    def _mutable_fields(self) -> set[str]:
        return {"field", "operator", "values", *super()._mutable_fields()}

    def _scalar(self) -> dict[str, object]:
        return {
            "field": self.field,
            "values": self.values,
            "operator": self.operator.value,
        }


class StringFilterOperator(str, Enum):
    """
    Configures the behavior of a String filter.

    IS_EMPTY: The string is empty
    IS_NOT_EMPTY: The string is not empty
    CONTAINS: The string contains
    DOES_NOT_CONTAIN: The string does not contain
    STARTS_WITH: The string is prefixed with
    ENDS_WITH: The string is suffixed with
    IS_EXACTLY: Exact match of full string
    REGEX: Regular expressions
    """

    IS_EMPTY = "IS_EMPTY"
    IS_NOT_EMPTY = "IS_NOT_EMPTY"
    CONTAINS = "CONTAINS"
    DOES_NOT_CONTAIN = "DOES_NOT_CONTAIN"
    STARTS_WITH = "STARTS_WITH"
    ENDS_WITH = "ENDS_WITH"
    IS_EXACTLY = "IS_EXACTLY"
    REGEX = "REGEX"


class StringFilter(Filter):
    """A String filter configuration.

    https://docs.validio.io/docs/filters#string
    """

    def __init__(
        self,
        *,
        field: str,
        operator: StringFilterOperator,
        value: str | None = None,
        name: str | None = None,
        source: Optional["Source"] = None,
        display_name: str | None = None,
        ignore_changes: bool = False,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the filter
        :param source: The source to attach the filter to
        :param display_name: Human-readable name for the filter. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored
        :param field: Field to be filtered on.
        :param operator: The string matching operation to perform.
            Only records matching this operation will be processed.
        :param value: Depending on the selected operator, this specifies
            an optional value as input to the selected operator.
        """
        super().__init__(
            name=name,
            source=source,
            display_name=display_name,
            ignore_changes=ignore_changes,
        )

        self.field = field
        self.operator = (
            StringFilterOperator(operator)
            if not isinstance(operator, StringFilterOperator)
            else operator
        )
        self.value = value

    def _mutable_fields(self) -> set[str]:
        return {"field", "operator", "value", *super()._mutable_fields()}

    def _scalar(self) -> dict[str, object]:
        return {
            "field": self.field,
            "value": self.value,
            "operator": self.operator.value,
        }


class ThresholdFilterOperator(str, Enum):
    """
    Configures the behavior of a String filter.

    EQUAL: The value equals (==)
    NOT_EQUAL: The value does not equal (!=)
    LESS_THAN: The value is less than (<)
    LESS_THAN_OR_EQUAL: The value is less than or equal (<=)
    GREATER_THAN: The value is greater than (>)
    GREATER_THAN_OR_EQUAL: The value is greater than or equal (>=)
    """

    EQUAL = "EQUAL"
    NOT_EQUAL = "NOT_EQUAL"
    LESS_THAN = "LESS"
    LESS_THAN_OR_EQUAL = "LESS_EQUAL"
    GREATER_THAN = "GREATER"
    GREATER_THAN_OR_EQUAL = "GREATER_EQUAL"


class ThresholdFilter(Filter):
    """A Threshold filter configuration.

    https://docs.validio.io/docs/filters#threshold-filter
    """

    def __init__(
        self,
        *,
        field: str,
        value: float,
        operator: ThresholdFilterOperator,
        name: str | None = None,
        source: Optional["Source"] = None,
        display_name: str | None = None,
        ignore_changes: bool = False,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the filter
        :param source: The source to attach the filter to
        :param display_name: Human-readable name for the filter. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored
        :param field: Field to be filtered on.
        :param operator: The comparison operation to perform.
            Only records matching this operation will be processed.
        :param value: The comparison value for the selected operator.
        """
        super().__init__(
            name=name,
            source=source,
            display_name=display_name,
            ignore_changes=ignore_changes,
        )

        self.field = field
        self.operator = (
            ThresholdFilterOperator(operator)
            if not isinstance(operator, ThresholdFilterOperator)
            else operator
        )
        self.value = value

    def _mutable_fields(self) -> set[str]:
        return {"field", "operator", "value", *super()._mutable_fields()}

    def _scalar(self) -> dict[str, object]:
        return {
            "field": self.field,
            "value": self.value,
            "operator": self.operator.value,
        }


class SqlFilter(Filter):
    """A SQL filter configuration.

    https://docs.validio.io/docs/filters#sql-filter
    """

    def __init__(
        self,
        *,
        query: str,
        name: str | None = None,
        source: Optional["Source"] = None,
        display_name: str | None = None,
        ignore_changes: bool = False,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the filter
        :param source: The source to attach the filter to
        :param display_name: Human-readable name for the filter. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored
        :param query: The SQL `WHERE` clause to filter records against.
            NOTE: this query should not actually contain the `WHERE` keyword.
            Example: `Age > 95 AND City = 'LDN'`
        """
        super().__init__(
            name=name,
            source=source,
            display_name=display_name,
            ignore_changes=ignore_changes,
        )

        self.query = query

    def _mutable_fields(self) -> set[str]:
        return {"query", *super()._mutable_fields()}

    def _scalar(self) -> dict[str, object]:
        return {"query": self.query}
