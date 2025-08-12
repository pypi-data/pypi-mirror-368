# -*- coding: utf-8 -*-

class Unit13Enum(object):

    """Implementation of the 'Unit13' enum.

    Specifies how often to start new runs of a Protection Group. <br>'Days'
    specifies that Protection Group run starts periodically on every day. For
    full backup schedule, currently we only support frequecny of 1 which
    indicates that full backup will be performed daily. <br>'Weeks' specifies
    that new Protection Group runs start weekly on certain days specified
    using 'dayOfWeek' field. <br>'Months' specifies that new Protection Group
    runs start monthly on certain day of specific week. This schedule needs
    'weekOfMonth' and 'dayOfWeek' fields to be set. <br> Example: To run the
    Protection Group on Second Sunday of Every Month, following schedule need
    to be set: <br> unit: 'Month' <br> dayOfWeek: 'Sunday' <br> weekOfMonth:
    'Second'

    Attributes:
        DAYS: TODO: type description here.
        WEEKS: TODO: type description here.
        MONTHS: TODO: type description here.

    """

    DAYS = 'Days'

    WEEKS = 'Weeks'

    MONTHS = 'Months'

