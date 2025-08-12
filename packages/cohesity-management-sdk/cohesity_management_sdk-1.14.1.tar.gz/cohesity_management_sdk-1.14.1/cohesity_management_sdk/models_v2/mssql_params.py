# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.host_information
import cohesity_management_sdk.models_v2.aag_info

class MssqlParams(object):

    """Implementation of the 'MssqlParams' model.

    Specifies the parameters for Msssql object.

    Attributes:
        host_info (HostInformation): Specifies the host information for a
            objects. This is mainly populated in case of App objects where app
            object is hosted by another object such as VM or physical server.
        aag_info (AAGInfo): Object details for Mssql.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "host_info":'hostInfo',
        "aag_info":'aagInfo'
    }

    def __init__(self,
                 host_info=None,
                 aag_info=None):
        """Constructor for the MssqlParams class"""

        # Initialize members of the class
        self.host_info = host_info
        self.aag_info = aag_info


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
        host_info = cohesity_management_sdk.models_v2.host_information.HostInformation.from_dictionary(dictionary.get('hostInfo')) if dictionary.get('hostInfo') else None
        aag_info = cohesity_management_sdk.models_v2.aag_info.AAGInfo.from_dictionary(dictionary.get('aagInfo')) if dictionary.get('aagInfo') else None

        # Return an object of this model
        return cls(host_info,
                   aag_info)


