# -*- coding: utf-8 -*-

class Unit9Enum(object):

    """Implementation of the 'Unit9' enum.

    Specifies the unit interval for retention of Snapshots. <br>'Runs' means
    that the Snapshot copy retained after the number of Protection Group Runs
    equals the number specified in the frequency. <br>'Hours' means that the
    Snapshot copy retained hourly at the frequency set in the frequency, for
    example if scheduleFrequency is 2, the copy occurs every 2 hours.
    <br>'Days' means that the Snapshot copy gets retained daily at the
    frequency set in the frequency. <br>'Weeks' means that the Snapshot copy
    is retained weekly at the frequency set in the frequency. <br>'Months'
    means that the Snapshot copy is retained monthly at the frequency set in
    the Frequency. <br>'Years' means that the Snapshot copy is retained yearly
    at the frequency set in the Frequency.

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

