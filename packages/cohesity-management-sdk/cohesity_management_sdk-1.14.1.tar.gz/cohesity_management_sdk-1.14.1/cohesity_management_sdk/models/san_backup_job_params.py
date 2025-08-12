# -*- coding: utf-8 -*-
# Copyright 2019 Cohesity Inc.


class SanBackupJobParams(object):

    """Implementation of the 'SanBackupJobParams' model.

    Message to capture any additional backup params for SAN environment.

    Attributes:
        use_secured_snapshot (bool): Whether backup should continue use secured
            snapshot. For example IBM
            FlashSystem SAN env uses this param to create safeguarded snapshot.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "use_secured_snapshot":'useSecuredSnapshot'
    }

    def __init__(self,
                 use_secured_snapshot=None):
        """Constructor for the SanBackupJobParams class"""

        # Initialize members of the class
        self.use_secured_snapshot = use_secured_snapshot


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
        use_secured_snapshot = dictionary.get('useSecuredSnapshot')

        # Return an object of this model
        return cls(use_secured_snapshot)


