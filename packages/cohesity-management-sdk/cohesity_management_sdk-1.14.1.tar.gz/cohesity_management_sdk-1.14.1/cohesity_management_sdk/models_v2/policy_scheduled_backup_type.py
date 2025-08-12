# -*- coding: utf-8 -*-


class PolicyScheduledBackupType(object):

    """Implementation of the 'Policy Scheduled Backup type.' model.

    Policy Scheduled Backup type.

    Attributes:
        policy_scheduled_backup (PolicyScheduledBackupEnum): Specifies
            Scheduled Backup type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "policy_scheduled_backup":'PolicyScheduledBackup'
    }

    def __init__(self,
                 policy_scheduled_backup=None):
        """Constructor for the PolicyScheduledBackupType class"""

        # Initialize members of the class
        self.policy_scheduled_backup = policy_scheduled_backup


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
        policy_scheduled_backup = dictionary.get('PolicyScheduledBackup')

        # Return an object of this model
        return cls(policy_scheduled_backup)


