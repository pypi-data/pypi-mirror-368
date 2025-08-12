# -*- coding: utf-8 -*-


class OraclePdbObjectInfo(object):

    """Implementation of the 'OraclePdbObjectInfo' model.

    Specifies information PDB object to restore.

    Attributes:
        db_id (string): Specifies pluggable database id.
        db_name (string): Specifies name of the DB.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "db_id":'dbId',
        "db_name":'dbName'
    }

    def __init__(self,
                 db_id=None,
                 db_name=None):
        """Constructor for the OraclePdbObjectInfo class"""

        # Initialize members of the class
        self.db_id = db_id
        self.db_name = db_name


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
        db_id = dictionary.get('dbId')
        db_name = dictionary.get('dbName')

        # Return an object of this model
        return cls(db_id,
                   db_name)


