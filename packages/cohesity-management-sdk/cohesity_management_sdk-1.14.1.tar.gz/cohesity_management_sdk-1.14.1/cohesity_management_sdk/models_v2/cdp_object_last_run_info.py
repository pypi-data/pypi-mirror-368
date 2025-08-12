# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.cdp_local_backup_info

class CdpObjectLastRunInfo(object):

    """Implementation of the 'CdpObjectLastRunInfo' model.

    Specifies the last backup information for a given CDP object.

    Attributes:
        local_backup_info (CdpLocalBackupInfo): Specifies the last local
            backup information for a given CDP object.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "local_backup_info":'localBackupInfo'
    }

    def __init__(self,
                 local_backup_info=None):
        """Constructor for the CdpObjectLastRunInfo class"""

        # Initialize members of the class
        self.local_backup_info = local_backup_info


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
        local_backup_info = cohesity_management_sdk.models_v2.cdp_local_backup_info.CdpLocalBackupInfo.from_dictionary(dictionary.get('localBackupInfo')) if dictionary.get('localBackupInfo') else None

        # Return an object of this model
        return cls(local_backup_info)


