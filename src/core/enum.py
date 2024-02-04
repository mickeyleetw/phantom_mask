from enum import Enum, unique


class _StrEnum(str, Enum):
    pass


# url parameter
@unique
class OrderByTypeEnum(_StrEnum):
    ASC = 'asc'
    DESC = 'desc'

@unique
class DayOfTheWeekEnum(_StrEnum):
    MONDAY='Monday'
    TUESDAY='Tuesday'
    WEDNESDAY='Wednesday'
    THURSDAY='Thursday'
    FRIDAY='Friday'
    SATURDAY='Saturday'
    SUNDAY='Sunday'

@unique
class PharmacyMaskOrderByEnum(_StrEnum):
    NAME = 'name'
    PRICE = 'price'

@unique
class PharmacyOrderByEnum(_StrEnum):
    NAME = 'name'

@unique
class MaskOrderByEnum(_StrEnum):
    NAME = 'name'