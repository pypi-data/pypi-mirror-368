# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_recover_object_snapshot_params
import cohesity_management_sdk.models_v2.recover_pure_san_volume_params
import cohesity_management_sdk.models_v2.recover_pure_san_group_params

class RecoverPureParams(object):

    """Implementation of the 'Recover Pure Params.' model.

    Specifies the recovery options specific to Pure environment.

    Attributes:
        objects (list of CommonRecoverObjectSnapshotParams): Specifies the
            list of recover object parameters.
        recovery_action (string): Specifies the type of recovery action to be
            performed. The corresponding recovery action params must be filled
            out.
        recover_san_group_params (RecoverPureSANGroupParams): Specifies the parameters to recover SAN Pure Protection Group.
        recover_san_volume_params (RecoverPureSANVolumeParams): Specifies the
            parameters to recover SAN Volume.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "recovery_action":'recoveryAction',
        "recover_san_group_params":'recoverSanGroupParams',
        "recover_san_volume_params":'recoverSanVolumeParams'
    }

    def __init__(self,
                 objects=None,
                 recovery_action='RecoverSanVolumes',
                 recover_san_group_params=None,
                 recover_san_volume_params=None):
        """Constructor for the RecoverPureParams class"""

        # Initialize members of the class
        self.objects = objects
        self.recovery_action = recovery_action
        self.recover_san_group_params = recover_san_group_params
        self.recover_san_volume_params = recover_san_volume_params


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
                objects.append(cohesity_management_sdk.models_v2.common_recover_object_snapshot_params.CommonRecoverObjectSnapshotParams.from_dictionary(structure))
        recovery_action = dictionary.get("recoveryAction") if dictionary.get("recoveryAction") else 'RecoverSanVolumes'
        recover_san_group_params = cohesity_management_sdk.models_v2.recover_pure_san_group_params.RecoverPureSANGroupParams.from_dictionary(
            dictionary.get('recoverSanGroupParams')) if dictionary.get('recoverSanGroupParams') else None
        recover_san_volume_params = cohesity_management_sdk.models_v2.recover_pure_san_volume_params.RecoverPureSANVolumeParams.from_dictionary(dictionary.get('recoverSanVolumeParams')) if dictionary.get('recoverSanVolumeParams') else None

        # Return an object of this model
        return cls(objects,
                   recovery_action,
                   recover_san_group_params,
                   recover_san_volume_params)