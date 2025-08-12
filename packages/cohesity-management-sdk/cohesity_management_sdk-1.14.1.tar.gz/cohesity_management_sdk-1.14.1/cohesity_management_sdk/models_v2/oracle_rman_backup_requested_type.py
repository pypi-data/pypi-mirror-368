# -*- coding: utf-8 -*-


class OracleRMANBackupRequestedType(object):

    """Implementation of the 'Oracle RMAN backup requested type.' model.

    Specifies Oracle RMAN backup requested type.

    Attributes:
        oracle_rman_backup (OracleRmanBackupEnum): Specifies Oracle RMAN
            backup requested type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "oracle_rman_backup":'oracleRmanBackup'
    }

    def __init__(self,
                 oracle_rman_backup=None):
        """Constructor for the OracleRMANBackupRequestedType class"""

        # Initialize members of the class
        self.oracle_rman_backup = oracle_rman_backup


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
        oracle_rman_backup = dictionary.get('oracleRmanBackup')

        # Return an object of this model
        return cls(oracle_rman_backup)


