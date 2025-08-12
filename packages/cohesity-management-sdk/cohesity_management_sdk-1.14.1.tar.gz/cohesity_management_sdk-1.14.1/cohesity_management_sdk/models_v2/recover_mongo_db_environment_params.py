# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_mongo_db_params

class RecoverMongoDBEnvironmentParams(object):

    """Implementation of the 'Recover MongoDB environment params.' model.

    Specifies the recovery options specific to MongoDB environment.

    Attributes:
        recovery_action (string): Specifies the type of recover action to be
            performed.
        recover_mongodb_params (RecoverMongoDBParams): Specifies the
            parameters to recover MongoDB objects.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recovery_action":'recoveryAction',
        "recover_mongodb_params":'recoverMongodbParams'
    }

    def __init__(self,
                 recovery_action='RecoverObjects',
                 recover_mongodb_params=None):
        """Constructor for the RecoverMongoDBEnvironmentParams class"""

        # Initialize members of the class
        self.recovery_action = recovery_action
        self.recover_mongodb_params = recover_mongodb_params


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
        recovery_action = dictionary.get("recoveryAction") if dictionary.get("recoveryAction") else 'RecoverObjects'
        recover_mongodb_params = cohesity_management_sdk.models_v2.recover_mongo_db_params.RecoverMongoDBParams.from_dictionary(dictionary.get('recoverMongodbParams')) if dictionary.get('recoverMongodbParams') else None

        # Return an object of this model
        return cls(recovery_action,
                   recover_mongodb_params)


