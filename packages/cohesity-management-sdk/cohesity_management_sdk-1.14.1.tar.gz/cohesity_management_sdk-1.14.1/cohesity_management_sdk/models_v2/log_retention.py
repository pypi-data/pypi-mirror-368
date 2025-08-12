# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.data_lock_config

class LogRetention(object):

    """Implementation of the 'LogRetention' model.

    Specifies the log retention of a backup.

    Attributes:
        data_lock_config (DataLockConfig): Specifies WORM retention type for the snapshots. When a WORM
          retention type is specified, the snapshots of the Protection Groups using
          this policy will be kept for the last N days as specified in the duration
          of the datalock. During that time, the snapshots cannot be deleted. For
          RPaaS the data lock will always be automatically set to cover the whole
          retention, and any input will be ignored.
        duration (long|int): Specifies the duration for a backup retention. <br> Example.
          If duration is 7 and unit is Months, the retention of a backup is 7 * 30
          = 210 days.
        unit (Unit11Enum): Specificies the Retention Unit of a backup measured in days,
          months or years. <br> If unit is ''Months'', then number specified in duration
          is multiplied to 30. <br> Example: If duration is 4 and unit is ''Months''
          then number of retention days will be 30 * 4 = 120 days. <br> If unit is
          ''Years'', then number specified in duration is multiplied to 365. <br>
          If duration is 2 and unit is ''Years'' then number of retention days will
          be 365 * 2 = 730 days.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "data_lock_config":'dataLockConfig',
        "duration":'duration',
        "unit":'unit'
    }

    def __init__(self,
                 data_lock_config=None,
                 duration=None,
                unit=None):
        """Constructor for the LogRetention class"""

        # Initialize members of the class
        self.data_lock_config = data_lock_config
        self.duration = duration
        self.unit = unit



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
        data_lock_config = cohesity_management_sdk.models_v2.data_lock_config.DataLockConfig.from_dictionary(dictionary.get('dataLockConfig')) if dictionary.get('dataLockConfig') else None
        duration = dictionary.get('duration')
        unit = dictionary.get('unit')

        # Return an object of this model
        return cls(data_lock_config,
                   duration,
                   unit)