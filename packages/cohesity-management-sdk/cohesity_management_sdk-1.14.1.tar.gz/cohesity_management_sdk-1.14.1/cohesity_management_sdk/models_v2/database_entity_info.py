# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.container_database_info
import cohesity_management_sdk.models_v2.oracle_data_gaurd_info

class DatabaseEntityInfo(object):

    """Implementation of the 'DatabaseEntityInfo' model.

    Object details about Oracle database entity info.

    Attributes:
        container_database_info (ContainerDatabaseInfo): Object details about
            Oracle container database.
        data_guard_info (OracleDataGuardInfo): Specifies the dataguard information
            about container database.
        db_type (dbType2Enum): Specifies database type of oracle database.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "container_database_info":'containerDatabaseInfo',
        "data_guard_info":'dataGuardInfo',
        "db_type":'dbType'
    }

    def __init__(self,
                 container_database_info=None,
                 data_guard_info=None,
                 db_type=None):
        """Constructor for the DatabaseEntityInfo class"""

        # Initialize members of the class
        self.container_database_info = container_database_info
        self.data_guard_info = data_guard_info
        self.db_type = db_type


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
        container_database_info = cohesity_management_sdk.models_v2.container_database_info.ContainerDatabaseInfo.from_dictionary(dictionary.get('containerDatabaseInfo')) if dictionary.get('containerDatabaseInfo') else None
        data_gaurd_info = dictionary.get('dataGuardInfo')
        db_type = dictionary.get('dbType')

        # Return an object of this model
        return cls(container_database_info,
                   data_gaurd_info,
                   db_type)