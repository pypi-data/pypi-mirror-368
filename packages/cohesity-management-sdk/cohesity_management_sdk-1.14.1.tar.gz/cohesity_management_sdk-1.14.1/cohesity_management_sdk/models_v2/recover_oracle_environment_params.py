# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_oracle_database_snapshot_params
import cohesity_management_sdk.models_v2.recover_oracle_db_params

class RecoverOracleEnvironmentParams(object):

    """Implementation of the 'Recover Oracle environment params.' model.

    Specifies the recovery options specific to oracle environment.

    Attributes:
        objects (list of RecoverOracleDatabaseSnapshotParams): Specifies the
            list of parameters for list of objects to be recovered.
        recovery_action (RecoveryAction14Enum): Specifies the type of recover
            action to be performed.
        recover_app_params (RecoverOracleDBParams): Specifies the parameters
            to recover Oracle databases.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "recovery_action":'recoveryAction',
        "recover_app_params":'recoverAppParams'
    }

    def __init__(self,
                 objects=None,
                 recovery_action=None,
                 recover_app_params=None):
        """Constructor for the RecoverOracleEnvironmentParams class"""

        # Initialize members of the class
        self.objects = objects
        self.recovery_action = recovery_action
        self.recover_app_params = recover_app_params


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
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.recover_oracle_database_snapshot_params.RecoverOracleDatabaseSnapshotParams.from_dictionary(structure))
        recovery_action = dictionary.get('recoveryAction')
        recover_app_params = cohesity_management_sdk.models_v2.recover_oracle_db_params.RecoverOracleDBParams.from_dictionary(dictionary.get('recoverAppParams')) if dictionary.get('recoverAppParams') else None

        # Return an object of this model
        return cls(objects,
                   recovery_action,
                   recover_app_params)


