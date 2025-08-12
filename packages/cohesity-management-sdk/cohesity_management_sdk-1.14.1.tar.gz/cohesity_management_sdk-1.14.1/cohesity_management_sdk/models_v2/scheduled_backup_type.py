# -*- coding: utf-8 -*-


class ScheduledBackupType(object):

    """Implementation of the 'Scheduled Backup type.' model.

    Scheduled Backup type.

    Attributes:
        scheduled_backup (ScheduledBackupEnum): Specifies Scheduled Backup
            type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "scheduled_backup":'scheduledBackup'
    }

    def __init__(self,
                 scheduled_backup=None):
        """Constructor for the ScheduledBackupType class"""

        # Initialize members of the class
        self.scheduled_backup = scheduled_backup


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
        scheduled_backup = dictionary.get('scheduledBackup')

        # Return an object of this model
        return cls(scheduled_backup)


