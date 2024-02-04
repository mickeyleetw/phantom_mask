from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional, Union

import orjson
from fastapi.params import Query
from pydantic import BaseModel as _BaseModel
from pydantic import StrictFloat, root_validator
from pydantic.fields import SHAPE_SINGLETON, ModelField
from pydantic_factories import ModelFactory as _ModelFactory

from core.pydantic.field import UTCDatetime

if TYPE_CHECKING:
    from pydantic.typing import AbstractSetIntStr, MappingIntStrAny, TupleGenerator


class BaseModel(_BaseModel):

    @staticmethod
    def is_optional(field: ModelField):
        if field.allow_none and (field.shape != SHAPE_SINGLETON or not field.sub_fields):
            return True

        return False

    @classmethod
    def get_properties(cls):
        return [
            prop for prop in dir(cls)
            if isinstance(getattr(cls, prop), property) and prop not in ('__values__', 'fields')
        ]

    @root_validator(pre=True)
    def set_default_value_with_optional_field(cls, values):
        for k, field in cls.__fields__.items():
            default = field.get_default()
            if type(default) is Query:
                default = default.default
            if cls.is_optional(field) and default is not None:
                v = values.pop(k, None)
                values[k] = default if v is None else v

        return values

    @root_validator
    def transfer_datetime_format_to_utc(cls, data: dict):
        for name, field in cls.__fields__.items():
            if field.type_ is datetime and data.get(name) and data.get(name).tzinfo:
                data[name] = (data[name].astimezone(timezone.utc)).replace(tzinfo=None)

        return data

    def _iter(
        self,
        to_dict: bool = False,
        by_alias: bool = False,
        include: Optional[Union['AbstractSetIntStr', 'MappingIntStrAny']] = None,
        exclude: Optional[Union['AbstractSetIntStr', 'MappingIntStrAny']] = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> 'TupleGenerator':
        yield from super()._iter(to_dict, by_alias, include, exclude, exclude_unset, exclude_defaults, exclude_none)

        props = self.get_properties()
        if include:
            props = (prop for prop in props if prop in include)
        if exclude:
            props = (prop for prop in props if prop not in exclude)

        if props:
            for prop in props:
                yield prop, getattr(self, prop)

    def jsonable_dict(
        self,
        by_alias: bool = False,
        skip_defaults: Optional[bool] = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        **kwargs,
    ) -> dict:
        json_ = self.json(
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            **kwargs,
        )

        return orjson.loads(json_)  # pylint:disable=no-member


class DateTimeLogMixin(BaseModel):
    create_time: UTCDatetime
    update_time: UTCDatetime


class ModelFactory(_ModelFactory[Any]):

    @classmethod
    def get_mock_value(cls, field_type: Any) -> Any:
        faker = cls._get_faker()
        if field_type is UTCDatetime:
            return faker.date_time_between()
        elif field_type in (float, StrictFloat):
            return faker.pyfloat(left_digits=6, right_digits=2, positive=True)
        elif field_type is Decimal:
            return faker.pydecimal(left_digits=6, right_digits=2, positive=True)
        elif field_type is dict:
            return faker.pydict(value_types=[int, str])

        return super().get_mock_value(field_type)
