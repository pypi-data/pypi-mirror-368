# -*- coding: utf-8 -*-


class DataLockConfig(object):

    """Implementation of the 'DataLockConfig' model.

    Specifies WORM retention type for the snapshots. When a WORM retention
    type is specified, the snapshots of the Protection Groups using this
    policy will be kept for the last N days as specified in the duration of
    the datalock. During that time, the snapshots cannot be deleted.

    Attributes:
        mode (Mode2Enum): Specifies the type of WORM retention type. 
            'Compliance' implies WORM retention is set for compliance reason. 
            'Administrative' implies WORM retention is set for administrative
            purposes.
        enable_worm_on_external_target (bool): Specifies whether objects in the external target associated with
          this policy need to be made immutable.
        unit (Unit2Enum): Specificies the Retention Unit of a dataLock
            measured in days, months or years. <br> If unit is 'Months', then
            number specified in duration is multiplied to 30. <br> Example: If
            duration is 4 and unit is 'Months' then number of retention days
            will be 30 * 4 = 120 days. <br> If unit is 'Years', then number
            specified in duration is multiplied to 365. <br> If duration is 2
            and unit is 'Months' then number of retention days will be 365 * 2
            = 730 days.
        duration (long|int): Specifies the duration for a dataLock. <br>
            Example. If duration is 7 and unit is Months, the dataLock is
            enabled for last 7 * 30 = 210 days of the backup.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "mode":'mode',
        "enable_worm_on_external_target":'enableWormOnExternalTarget',
        "unit":'unit',
        "duration":'duration'
    }

    def __init__(self,
                 mode=None,
                 enable_worm_on_external_target=None,
                 unit=None,
                 duration=None):
        """Constructor for the DataLockConfig class"""

        # Initialize members of the class
        self.mode = mode
        self.enable_worm_on_external_target = enable_worm_on_external_target
        self.unit = unit
        self.duration = duration


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
        mode = dictionary.get('mode')
        enable_worm_on_external_target = dictionary.get('enableWormOnExternalTarget')
        unit = dictionary.get('unit')
        duration = dictionary.get('duration')

        # Return an object of this model
        return cls(mode,
                   enable_worm_on_external_target,
                   unit,
                   duration)