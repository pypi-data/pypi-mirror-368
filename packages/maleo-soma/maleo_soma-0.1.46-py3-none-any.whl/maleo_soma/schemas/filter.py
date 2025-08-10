from maleo_soma.mixins.general import Name
from maleo_soma.mixins.timestamp import OptionalFromTimestamp, OptionalToTimestamp


class DateFilter(
    OptionalToTimestamp,
    OptionalFromTimestamp,
    Name,
):
    pass
