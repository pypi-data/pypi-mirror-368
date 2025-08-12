# -*- coding: utf-8 -*-

class Unit1Enum(object):

    """Implementation of the 'Unit1' enum.

    Specificies the Retention Unit of a backup measured in days, months or
    years. <br> If unit is 'Months', then number specified in duration is
    multiplied to 30. <br> Example: If duration is 4 and unit is 'Months' then
    number of retention days will be 30 * 4 = 120 days. <br> If unit is
    'Years', then number specified in duration is multiplied to 365. <br> If
    duration is 2 and unit is 'Months' then number of retention days will be
    365 * 2 = 730 days.

    Attributes:
        DAYS: TODO: type description here.
        WEEKS: TODO: type description here.
        MONTHS: TODO: type description here.
        YEARS: TODO: type description here.

    """

    DAYS = 'Days'

    WEEKS = 'Weeks'

    MONTHS = 'Months'

    YEARS = 'Years'

