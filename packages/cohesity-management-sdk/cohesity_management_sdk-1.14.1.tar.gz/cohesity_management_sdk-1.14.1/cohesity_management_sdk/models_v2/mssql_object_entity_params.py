# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.host_information
import cohesity_management_sdk.models_v2.aag_info

class MssqlObjectEntityParams(object):

    """Implementation of the 'MssqlObjectEntityParams' model.

    Object details for Mssql.

    Attributes:
        aag_info (AAGInfo): Object details for Mssql.
        host_info (HostInformation): Specifies the host information for a
            objects. This is mainly populated in case of App objects where app
            object is hosted by another object such as VM or physical server.
        is_encrypted (bool): Specifies whether the database is TDE enabled.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "aag_info":'aagInfo',
        "host_info":'hostInfo',
        "is_encrypted":'isEncrypted'
    }

    def __init__(self,
                 aag_info=None,
                 host_info=None,
                 is_encrypted=None):
        """Constructor for the MssqlObjectEntityParams class"""

        # Initialize members of the class
        self.aag_info = aag_info
        self.host_info = host_info
        self.is_encrypted = is_encrypted


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
        aag_info = cohesity_management_sdk.models_v2.aag_info.AAGInfo.from_dictionary(dictionary.get('aagInfo')) if dictionary.get('aagInfo') else None
        host_info = cohesity_management_sdk.models_v2.host_information.HostInformation.from_dictionary(dictionary.get('hostInfo')) if dictionary.get('hostInfo') else None
        is_encrypted = dictionary.get('isEncrypted')

        # Return an object of this model
        return cls(
                   aag_info,
                   host_info,
                   is_encrypted)