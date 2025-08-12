# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

class OracleRecoveryValidationInfo(object):
    """Implementation of the 'OracleRecoveryValidationInfo' model.

    Specifies information related to Oracle Recovery Validation.

    Attributes:
        create_dummy_instance (bool): Specifies whether we will be creating a dummy oracle instance to run the validations. Generally if source and target location are different we create a dummy oracle instance else we use the source db.
    """

    _names = {
        "create_dummy_instance":"createDummyInstance",
    }

    def __init__(self,
                 create_dummy_instance=None):
        """Constructor for the OracleRecoveryValidationInfo class"""

        self.create_dummy_instance = create_dummy_instance


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

        create_dummy_instance = dictionary.get('createDummyInstance')

        return cls(
            create_dummy_instance
        )