# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class LinuxSupportUserSudoAccessReqParams(object):

    """Implementation of the 'LinuxSupportUserSudoAccessReqParams' model.

    Linux Support Sudo Access Req Params.

    Attributes:
        sudo_access_enable (bool): If sudoAccessEnable is set to true, the
            token would be regenerated and the new token will be returned.
        sudo_access_end_timestamp_msecs (long|int64): sudo access end time stamp in
            milliseconds since unix epoch.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "sudo_access_enable":'sudoAccessEnable',
        "sudo_access_end_timestamp_msecs":'sudoAccessEndTimestampMsecs'
    }

    def __init__(self,
                 sudo_access_enable=None,
                 sudo_access_end_timestamp_msecs=None):
        """Constructor for the LinuxSupportUserSudoAccessReqParams class"""

        # Initialize members of the class
        self.sudo_access_enable = sudo_access_enable
        self.sudo_access_end_timestamp_msecs = sudo_access_end_timestamp_msecs


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
        sudo_access_enable = dictionary.get('sudoAccessEnable')
        sudo_access_end_timestamp_msecs = dictionary.get('sudoAccessEndTimestampMsecs')

        # Return an object of this model
        return cls(sudo_access_enable,
                   sudo_access_end_timestamp_msecs)