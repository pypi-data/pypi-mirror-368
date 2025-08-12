# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.oracle_protection_group_database_params

class OracleProtectionGroupObjectIdentifier(object):

    """Implementation of the 'Oracle Protection Group Object Identifier.' model.

    Specifies the object identifier to create Oracle Protection Group.

    Attributes:
        source_id (long|int): Specifies the id of the host on which databases
            are hosted.
        source_name (string): Specifies the name of the host on which
            databases are hosted.
        db_params (list of OracleProtectionGroupDatabaseParams): Specifies the
            properties of the Oracle databases.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source_id":'sourceId',
        "source_name":'sourceName',
        "db_params":'dbParams'
    }

    def __init__(self,
                 source_id=None,
                 source_name=None,
                 db_params=None):
        """Constructor for the OracleProtectionGroupObjectIdentifier class"""

        # Initialize members of the class
        self.source_id = source_id
        self.source_name = source_name
        self.db_params = db_params


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
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')
        db_params = None
        if dictionary.get("dbParams") is not None:
            db_params = list()
            for structure in dictionary.get('dbParams'):
                db_params.append(cohesity_management_sdk.models_v2.oracle_protection_group_database_params.OracleProtectionGroupDatabaseParams.from_dictionary(structure))

        # Return an object of this model
        return cls(source_id,
                   source_name,
                   db_params)


