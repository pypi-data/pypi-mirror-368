# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

class ExchangeEnvJobParams(object):
    """Implementation of the 'ExchangeEnvJobParams' model.

    Specifies job parameters applicable for all 'kExchange' Environment type Protection Sources in a Protection Job.

    Attributes:
        backups_copy_only (bool):
    """

    _names = {
        "backups_copy_only":"backupsCopyOnly",
    }

    def __init__(self,
                 backups_copy_only=None):
        """Constructor for the ExchangeEnvJobParams class"""

        self.backups_copy_only = backups_copy_only


    @classmethod
    def from_dictionary(cls, dictionary):
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

        backups_copy_only = dictionary.get('backupsCopyOnly')

        return cls(
            backups_copy_only
        )