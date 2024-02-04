from datetime import date, datetime, timezone,time
from dateutil.parser import isoparse


class Int32(int):
    """
    A restricted int type for only 32bit range integer
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        sql_integer = int(v)
        if not (-0x1 << 31) <= sql_integer <= (0x1 << 31) - 1:
            raise ValueError('Lookup value too large to convert to SQL INTEGER')
        return sql_integer



class ParameterInt(Int32):
    """
    Restricts path/query parameters (string) of the URL to pure digits (0 ~ 9).

    Underscores in Numeric Literals is prohibited.

    It inherits int so the type on the documents (OpenApi) would be integer.
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        v = str(v)
        if not v.isdigit():
            raise ValueError('Unacceptable numeric literals in URL parameters')
        return super().validate(v)


class ParameterDate(date):
    """
        Restrict date format of query parameters to simply accept iso8601 calendar date format only
    (eg.'YYYY-MM-DD' or 'YYYYMMDD'), query parameters like date=20160101 should be recognized as date
    string format instead of timestamp.
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, data):
        if type(data) is not str:
            data = str(data)

        if data.isdigit():
            try:
                date_obj = datetime.strptime(data, '%Y%m%d')
            except ValueError:
                raise ValueError('Unprocessable date format in URL parameters')
        else:
            try:
                date_obj = datetime.strptime(data, '%Y-%m-%d')
            except ValueError:
                raise ValueError('Unprocessable date format in URL parameters')

        return date_obj



class UTCDatetime(datetime):
    """
    Add timezone info of UTC and return an ISO 8601 datetime.
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, data) -> datetime:
        if type(data) is not str:
            data = str(data)
        return isoparse(data).replace(tzinfo=timezone.utc, microsecond=0)

    @classmethod
    def to_isoformat_str(cls, data: datetime) -> str:
        return cls.validate(data).isoformat()


class ParameterTime(str):
    """
        Restrict time format of query parameters to simply accept iso8601 calendar time format only
    (eg.'HH:MM:SS'), query parameters like date=20160101 should be recognized as date
    string format instead of timestamp.
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, data):
        if type(data) is not str:
            raise ValueError('Unprocessable time format in URL parameters')
        else:
            try:
                time_obj=time.fromisoformat(data)
            except ValueError:
                raise ValueError('Unprocessable time format in URL parameters')
        return time_obj