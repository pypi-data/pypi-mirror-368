# -*- coding: utf-8 -*-

class PhysicalObjectEntityParams(object):

    """Implementation of the 'PhysicalObjectEntityParams' model.

    Specifies the common parameters for physical objects.

    Attributes:
        enable_system_backup (bool): Specifies if system backup was enabled for the source in a particular
          run.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "enable_system_backup":'enableSystemBackup'
    }

    def __init__(self,
                 enable_system_backup=None):
        """Constructor for the PhysicalObjectEntityParams class"""

        # Initialize members of the class
        self.enable_system_backup = enable_system_backup


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
        enable_system_backup = dictionary.get('enableSystemBackup')

        # Return an object of this model
        return cls(enable_system_backup)