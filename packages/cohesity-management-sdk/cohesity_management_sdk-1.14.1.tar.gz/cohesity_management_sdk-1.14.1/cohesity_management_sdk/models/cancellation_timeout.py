# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class CancellationTimeout(object):

    """Implementation of the 'CancellationTimeout' model.

    IP Range for range of vip address addition.

    Attributes:
        backup_type (int): The backup type to which this timeout applies to.
        timeout_mins (long| int): The duration of timeout after which the
            run/task will get cancelled automatically.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "backup_type": 'backupType',
        "timeout_mins": 'timeoutMins'
    }

    def __init__(self,
                 backup_type=None,
                 timeout_mins=None):
        """Constructor for the CancellationTimeout class"""

        # Initialize members of the class
        self.backup_type = backup_type
        self.timeout_mins = timeout_mins


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
        backup_type = dictionary.get('backupType', None)
        timeout_mins = dictionary.get('timeoutMins', None)

        # Return an object of this model
        return cls(backup_type,
                   timeout_mins)


