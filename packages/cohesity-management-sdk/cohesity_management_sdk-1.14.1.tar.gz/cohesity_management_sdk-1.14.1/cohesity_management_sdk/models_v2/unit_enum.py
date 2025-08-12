# -*- coding: utf-8 -*-

class UnitEnum(object):

    """Implementation of the 'Unit' enum.

    Specifies the frequency that Snapshots should be copied to the specified
    target. Used in combination with multiplier. <br>'Runs' means that the
    Snapshot copy occurs after the number of Protection Group Runs equals the
    number specified in the frequency. <br>'Hours' means that the Snapshot
    copy occurs hourly at the frequency set in the frequency, for example if
    scheduleFrequency is 2, the copy occurs every 2 hours. <br>'Days' means
    that the Snapshot copy occurs daily at the frequency set in the frequency.
    <br>'Weeks' means that the Snapshot copy occurs weekly at the frequency
    set in the frequency. <br>'Months' means that the Snapshot copy occurs
    monthly at the frequency set in the Frequency. <br>'Years' means that the
    Snapshot copy occurs yearly at the frequency set in the
    scheduleFrequency.

    Attributes:
        RUNS: TODO: type description here.
        HOURS: TODO: type description here.
        DAYS: TODO: type description here.
        WEEKS: TODO: type description here.
        MONTHS: TODO: type description here.
        YEARS: TODO: type description here.

    """

    RUNS = 'Runs'

    HOURS = 'Hours'

    DAYS = 'Days'

    WEEKS = 'Weeks'

    MONTHS = 'Months'

    YEARS = 'Years'

