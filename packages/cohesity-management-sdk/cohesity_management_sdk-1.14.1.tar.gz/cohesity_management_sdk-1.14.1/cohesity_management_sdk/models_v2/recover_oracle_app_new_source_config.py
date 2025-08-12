# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recovery_object_identifier
import cohesity_management_sdk.models_v2.recover_database_params
import cohesity_management_sdk.models_v2.recover_view_params

class RecoverOracleAppNewSourceConfig(object):

    """Implementation of the 'Recover Oracle App New Source Config.' model.

    Specifies the new destination Source configuration where the databases
    will be recovered.

    Attributes:
        host (RecoveryObjectIdentifier): Specifies the source id of target host where databases
            will be recovered. This source id can be a physical host or
            virtual machine.
        recovery_target (RecoveryTargetEnum): Specifies if recovery target is
            a database or a view.
        recover_database_params (RecoverDatabaseParams): Specifies recovery
            parameters when recovering to a database
        recover_view_params (RecoverViewParams): Specifies recovery parameters
            when recovering to a view.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "host":'host',
        "recovery_target":'recoveryTarget',
        "recover_database_params":'recoverDatabaseParams',
        "recover_view_params":'recoverViewParams'
    }

    def __init__(self,
                 host=None,
                 recovery_target=None,
                 recover_database_params=None,
                 recover_view_params=None):
        """Constructor for the RecoverOracleAppNewSourceConfig class"""

        # Initialize members of the class
        self.host = host
        self.recovery_target = recovery_target
        self.recover_database_params = recover_database_params
        self.recover_view_params = recover_view_params


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
        host = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(dictionary.get('host')) if dictionary.get('host') else None
        recovery_target = dictionary.get('recoveryTarget')
        recover_database_params = cohesity_management_sdk.models_v2.recover_database_params.RecoverDatabaseParams.from_dictionary(dictionary.get('recoverDatabaseParams')) if dictionary.get('recoverDatabaseParams') else None
        recover_view_params = cohesity_management_sdk.models_v2.recover_view_params.RecoverViewParams.from_dictionary(dictionary.get('recoverViewParams')) if dictionary.get('recoverViewParams') else None

        # Return an object of this model
        return cls(host,
                   recovery_target,
                   recover_database_params,
                   recover_view_params)