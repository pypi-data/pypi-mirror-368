# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_couchbase_params

class RecoverCouchbaseEnvironmentParams(object):

    """Implementation of the 'Recover Couchbase environment params.' model.

    Specifies the recovery options specific to Couchbase environment.

    Attributes:
        recovery_action (string): Specifies the type of recover action to be
            performed.
        recover_couchbase_params (RecoverCouchbaseParams): Specifies the
            parameters to recover Couchbase objects.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recovery_action":'recoveryAction',
        "recover_couchbase_params":'recoverCouchbaseParams'
    }

    def __init__(self,
                 recovery_action='RecoverObjects',
                 recover_couchbase_params=None):
        """Constructor for the RecoverCouchbaseEnvironmentParams class"""

        # Initialize members of the class
        self.recovery_action = recovery_action
        self.recover_couchbase_params = recover_couchbase_params


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
        recover_couchbase_params = cohesity_management_sdk.models_v2.recover_couchbase_params.RecoverCouchbaseParams.from_dictionary(dictionary.get('recoverCouchbaseParams')) if dictionary.get('recoverCouchbaseParams') else None

        # Return an object of this model
        return cls(recovery_action,
                   recover_couchbase_params)


