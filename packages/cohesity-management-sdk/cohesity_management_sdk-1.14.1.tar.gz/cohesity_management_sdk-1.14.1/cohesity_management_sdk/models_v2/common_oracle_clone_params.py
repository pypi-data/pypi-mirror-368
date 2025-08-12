# -*- coding: utf-8 -*-


class CommonOracleCloneParams(object):

    """Implementation of the 'CommonOracleCloneParams' model.

    Specifies the common properties of an Oracle clone.

    Attributes:
        db_name (string): Specifies the name of the cloned database.
        home_folder (string): Specifies the home folder for the cloned
            database.
        base_folder (string): Specifies the base folder of Oracle installation
            on the target host.
        sga (string): Specifies the System Global Area (SGA) for the clone
            database.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "db_name":'dbName',
        "home_folder":'homeFolder',
        "base_folder":'baseFolder',
        "sga":'sga'
    }

    def __init__(self,
                 db_name=None,
                 home_folder=None,
                 base_folder=None,
                 sga=None):
        """Constructor for the CommonOracleCloneParams class"""

        # Initialize members of the class
        self.db_name = db_name
        self.home_folder = home_folder
        self.base_folder = base_folder
        self.sga = sga


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
        db_name = dictionary.get('dbName')
        home_folder = dictionary.get('homeFolder')
        base_folder = dictionary.get('baseFolder')
        sga = dictionary.get('sga')

        # Return an object of this model
        return cls(db_name,
                   home_folder,
                   base_folder,
                   sga)


