# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.helios_tier

class HeliosRetention(object):

    """Implementation of the 'HeliosRetention' model.

    Specifies the retention of a backup.

    Attributes:
        unit (Unit1Enum): Specificies the Retention Unit of a backup measured
            in days, months or years. <br> If unit is 'Months', then number
            specified in duration is multiplied to 30. <br> Example: If
            duration is 4 and unit is 'Months' then number of retention days
            will be 30 * 4 = 120 days. <br> If unit is 'Years', then number
            specified in duration is multiplied to 365. <br> If duration is 2
            and unit is 'Months' then number of retention days will be 365 * 2
            = 730 days.
        duration (long|int): Specifies the duration for a backup retention.
            <br> Example. If duration is 7 and unit is Months, the retention
            of a backup is 7 * 30 = 210 days.
        tiers (list of HeliosTier): Specifies the list of tiers where backup
            will be moved. This will be populated only if poilcy type is
            DMaaS.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "unit":'unit',
        "duration":'duration',
        "tiers":'tiers'
    }

    def __init__(self,
                 unit=None,
                 duration=None,
                 tiers=None):
        """Constructor for the HeliosRetention class"""

        # Initialize members of the class
        self.unit = unit
        self.duration = duration
        self.tiers = tiers


    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary
        unit = dictionary.get('unit')
        duration = dictionary.get('duration')
        tiers = None
        if dictionary.get("tiers") is not None:
            tiers = list()
            for structure in dictionary.get('tiers'):
                tiers.append(cohesity_management_sdk.models_v2.helios_tier.HeliosTier.from_dictionary(structure))

        # Return an object of this model
        return cls(unit,
                   duration,
                   tiers)


