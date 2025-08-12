# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.oracle_protection_group_database_node_channel

class OracleProtectionGroupDatabaseParams(object):

    """Implementation of the 'Oracle Protection Group Database Params.' model.

    Specifies the parameters of individual databases to create Oracle
    Protection Group.

    Attributes:
        database_id (long|int): Specifies the id of the Oracle database.
        database_name (string): Specifies the name of the Oracle database.
        db_channels (list of OracleProtectionGroupDatabaseNodeChannel):
            Specifies the Oracle database node channels info. If not
            specified, the default values assigned by the server are applied
            to all the databases.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "database_id":'databaseId',
        "database_name":'databaseName',
        "db_channels":'dbChannels'
    }

    def __init__(self,
                 database_id=None,
                 database_name=None,
                 db_channels=None):
        """Constructor for the OracleProtectionGroupDatabaseParams class"""

        # Initialize members of the class
        self.database_id = database_id
        self.database_name = database_name
        self.db_channels = db_channels


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
        database_id = dictionary.get('databaseId')
        database_name = dictionary.get('databaseName')
        db_channels = None
        if dictionary.get("dbChannels") is not None:
            db_channels = list()
            for structure in dictionary.get('dbChannels'):
                db_channels.append(cohesity_management_sdk.models_v2.oracle_protection_group_database_node_channel.OracleProtectionGroupDatabaseNodeChannel.from_dictionary(structure))

        # Return an object of this model
        return cls(database_id,
                   database_name,
                   db_channels)


