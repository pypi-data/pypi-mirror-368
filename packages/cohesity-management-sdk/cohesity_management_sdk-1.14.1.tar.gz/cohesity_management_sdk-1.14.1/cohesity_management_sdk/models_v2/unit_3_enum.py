# -*- coding: utf-8 -*-

class Unit3Enum(object):

    """Implementation of the 'Unit3' enum.

    Specifies how often to start new runs of a Protection Group. <br>'Minutes'
    specifies that Protection Group run starts periodically after certain
    number of minutes specified in 'frequency' field. <br>'Hours' specifies
    that Protection Group run starts periodically after certain number of
    hours specified in 'frequency' field. <br>'Days' specifies that Protection
    Group run starts periodically after certain number of days specified in
    'frequency' field. <br>'Week' specifies that new Protection Group runs
    start weekly on certain days specified using 'dayOfWeek' field.
    <br>'Month' specifies that new Protection Group runs start monthly on
    certain day of specific week. This schedule needs 'weekOfMonth' and
    'dayOfWeek' fields to be set. <br> Example: To run the Protection Group on
    Second Sunday of Every Month, following schedule need to be set: <br>
    unit: 'Month' <br> dayOfWeek: 'Sunday' <br> weekOfMonth: 'Second'

    Attributes:
        MINUTES: TODO: type description here.
        HOURS: TODO: type description here.
        DAYS: TODO: type description here.
        WEEKS: TODO: type description here.
        MONTHS: TODO: type description here.

    """

    MINUTES = 'Minutes'

    HOURS = 'Hours'

    DAYS = 'Days'

    WEEKS = 'Weeks'

    MONTHS = 'Months'

