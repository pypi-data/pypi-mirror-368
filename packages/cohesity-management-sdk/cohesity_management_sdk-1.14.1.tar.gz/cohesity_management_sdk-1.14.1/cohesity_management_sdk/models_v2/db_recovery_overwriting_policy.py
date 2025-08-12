# -*- coding: utf-8 -*-


class DBRecoveryOverwritingPolicy(object):

    """Implementation of the 'DB Recovery Overwriting Policy.' model.

    DB Recovery Overwriting Policy.

    Attributes:
        db_recovery_over_writing_policy (DbRecoveryOverWritingPolicy1Enum):
            Specifies the overwriting policies in case of SQL App Recoveries.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "db_recovery_over_writing_policy":'dbRecoveryOverWritingPolicy'
    }

    def __init__(self,
                 db_recovery_over_writing_policy=None):
        """Constructor for the DBRecoveryOverwritingPolicy class"""

        # Initialize members of the class
        self.db_recovery_over_writing_policy = db_recovery_over_writing_policy


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
        db_recovery_over_writing_policy = dictionary.get('dbRecoveryOverWritingPolicy')

        # Return an object of this model
        return cls(db_recovery_over_writing_policy)


