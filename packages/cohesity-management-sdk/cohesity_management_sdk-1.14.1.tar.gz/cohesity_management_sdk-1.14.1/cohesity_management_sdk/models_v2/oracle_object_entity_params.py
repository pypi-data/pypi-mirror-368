# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.database_entity_info
import cohesity_management_sdk.models_v2.host_information

class OracleObjectEntityParams(object):

    """Implementation of the 'OracleObjectEntityParams' model.

    Object details for Oracle.

    Attributes:
        database_entity_info (DatabaseEntityInfo): Object details about Oracle
            database entity info.
        host_info (HostInformation): Specifies the host information for a
            objects. This is mainly populated in case of App objects where app
            object is hosted by another object such as VM or physical server.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "database_entity_info":'databaseEntityInfo',
        "host_info":'hostInfo'
    }

    def __init__(self,
                 database_entity_info=None,
                 host_info=None):
        """Constructor for the OracleObjectEntityParams class"""

        # Initialize members of the class
        self.database_entity_info = database_entity_info
        self.host_info = host_info


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
        database_entity_info = cohesity_management_sdk.models_v2.database_entity_info.DatabaseEntityInfo.from_dictionary(dictionary.get('databaseEntityInfo')) if dictionary.get('databaseEntityInfo') else None
        host_info = cohesity_management_sdk.models_v2.host_information.HostInformation.from_dictionary(dictionary.get('hostInfo')) if dictionary.get('hostInfo') else None

        # Return an object of this model
        return cls(database_entity_info,
                   host_info)


