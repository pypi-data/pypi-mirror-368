# -*- coding: utf-8 -*-


class UserDatabaseBackupPreferenceType(object):

    """Implementation of the 'User Database Backup Preference Type.' model.

    Specifies User Database Backup Preference Type.

    Attributes:
        user_db_backup_preference (UserDbBackupPreferenceEnum): Specifies User
            Database Backup Preference Type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "user_db_backup_preference":'userDbBackupPreference'
    }

    def __init__(self,
                 user_db_backup_preference=None):
        """Constructor for the UserDatabaseBackupPreferenceType class"""

        # Initialize members of the class
        self.user_db_backup_preference = user_db_backup_preference


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
        user_db_backup_preference = dictionary.get('userDbBackupPreference')

        # Return an object of this model
        return cls(user_db_backup_preference)


