# -*- coding: utf-8 -*-

class WeekOfMonthEnum(object):

    """Implementation of the 'WeekOfMonth' enum.

    Specifies the week of the month (such as 'Third') in a Monthly Schedule
    specified by unit field as 'Months'. <br>This field is used in combination
    with 'dayOfWeek' to define the day in the month to start the Protection
    Group Run. <br> Example: if 'weekOfMonth' is set to 'Third' and day is set
    to 'Monday', a backup is performed on the third Monday of every month.

    Attributes:
        FIRST: TODO: type description here.
        SECOND: TODO: type description here.
        THIRD: TODO: type description here.
        FOURTH: TODO: type description here.
        LAST: TODO: type description here.

    """

    FIRST = 'First'

    SECOND = 'Second'

    THIRD = 'Third'

    FOURTH = 'Fourth'

    LAST = 'Last'

