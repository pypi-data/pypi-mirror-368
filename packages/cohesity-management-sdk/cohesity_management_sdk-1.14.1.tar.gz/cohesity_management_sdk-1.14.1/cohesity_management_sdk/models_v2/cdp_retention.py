# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.data_lock_config

class CdpRetention(object):

    """Implementation of the 'CdpRetention' model.

    Specifies the retention of a CDP backup.

    Attributes:
        unit (Unit7Enum): Specificies the Retention Unit of a CDP backup
            measured in minutes or hours.
        duration (int): Specifies the duration for a cdp backup retention.
        data_lock_config (DataLockConfig): Specifies WORM retention type for
            the snapshots. When a WORM retention type is specified, the
            snapshots of the Protection Groups using this policy will be kept
            for the last N days as specified in the duration of the datalock.
            During that time, the snapshots cannot be deleted.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "unit":'unit',
        "duration":'duration',
        "data_lock_config":'dataLockConfig'
    }

    def __init__(self,
                 unit=None,
                 duration=None,
                 data_lock_config=None):
        """Constructor for the CdpRetention class"""

        # Initialize members of the class
        self.unit = unit
        self.duration = duration
        self.data_lock_config = data_lock_config


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
        data_lock_config = cohesity_management_sdk.models_v2.data_lock_config.DataLockConfig.from_dictionary(dictionary.get('dataLockConfig')) if dictionary.get('dataLockConfig') else None

        # Return an object of this model
        return cls(unit,
                   duration,
                   data_lock_config)


