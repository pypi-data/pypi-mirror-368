# -*- coding: utf-8 -*-


class OracleUpdateRestoreOptions(object):

    """Implementation of the 'OracleUpdateRestoreOptions' model.

    Specifies the parameters that are needed for updating oracle restore
    options.

    Attributes:
        delay_secs (long|int): Specifies when the migration of the oracle
            instance should be started after successful recovery.
        target_path_vec (list of string): Specifies the target paths to be
            used for DB migration.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "delay_secs":'delaySecs',
        "target_path_vec":'targetPathVec'
    }

    def __init__(self,
                 delay_secs=None,
                 target_path_vec=None):
        """Constructor for the OracleUpdateRestoreOptions class"""

        # Initialize members of the class
        self.delay_secs = delay_secs
        self.target_path_vec = target_path_vec


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
        delay_secs = dictionary.get('delaySecs')
        target_path_vec = dictionary.get('targetPathVec')

        # Return an object of this model
        return cls(delay_secs,
                   target_path_vec)


