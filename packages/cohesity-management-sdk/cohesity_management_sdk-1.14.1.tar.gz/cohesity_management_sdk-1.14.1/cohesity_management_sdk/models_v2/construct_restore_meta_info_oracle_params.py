# -*- coding: utf-8 -*-


class ConstructRestoreMetaInfoOracleParams(object):

    """Implementation of the 'ConstructRestoreMetaInfoOracleParams' model.

    Params to fetch oracle restore meta info

    Attributes:
        db_name (string): Specifies the name of the Oracle database that we
            restore to.
        base_dir (string): Specifies the base directory of Oracle at
            destination.
        home_dir (string): Specifies the home directory of Oracle at
            destination.
        db_file_destination (string): Specifies the location to put the
            database files(datafiles, logfiles etc.)
        is_clone (bool): Specifies whether operation is clone or not
        is_granular_restore (bool): Specifies whether the operation is
            granular restore or not.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "db_name":'dbName',
        "base_dir":'baseDir',
        "home_dir":'homeDir',
        "is_clone":'isClone',
        "db_file_destination":'dbFileDestination',
        "is_granular_restore":'isGranularRestore'
    }

    def __init__(self,
                 db_name=None,
                 base_dir=None,
                 home_dir=None,
                 is_clone=None,
                 db_file_destination=None,
                 is_granular_restore=None):
        """Constructor for the ConstructRestoreMetaInfoOracleParams class"""

        # Initialize members of the class
        self.db_name = db_name
        self.base_dir = base_dir
        self.home_dir = home_dir
        self.db_file_destination = db_file_destination
        self.is_clone = is_clone
        self.is_granular_restore = is_granular_restore


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
        base_dir = dictionary.get('baseDir')
        home_dir = dictionary.get('homeDir')
        is_clone = dictionary.get('isClone')
        db_file_destination = dictionary.get('dbFileDestination')
        is_granular_restore = dictionary.get('isGranularRestore')

        # Return an object of this model
        return cls(db_name,
                   base_dir,
                   home_dir,
                   is_clone,
                   db_file_destination,
                   is_granular_restore)


