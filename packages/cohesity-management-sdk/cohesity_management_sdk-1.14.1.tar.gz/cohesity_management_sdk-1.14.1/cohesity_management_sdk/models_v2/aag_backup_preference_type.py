# -*- coding: utf-8 -*-


class AagBackupPreferenceType(object):

    """Implementation of the 'Aag Backup Preference Type.' model.

    Specifies Aag Backup Preference Type.

    Attributes:
        aag_backup_preference (AagBackupPreferenceEnum): Specifies Aag Backup
            Preference Type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "aag_backup_preference":'aagBackupPreference'
    }

    def __init__(self,
                 aag_backup_preference=None):
        """Constructor for the AagBackupPreferenceType class"""

        # Initialize members of the class
        self.aag_backup_preference = aag_backup_preference


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
        aag_backup_preference = dictionary.get('aagBackupPreference')

        # Return an object of this model
        return cls(aag_backup_preference)


