# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_recover_object_snapshot_params
import cohesity_management_sdk.models_v2.rename_recovered_namespaces_params
import cohesity_management_sdk.models_v2.kubernetes_namespace_recovery_target_config

class KubernetesTargetParamsForRecoverNamespace(object):

    """Implementation of the 'Kubernetes Target Params For Recover Namespace' model.

    Specifies the parameters for recovering a Kubernetes namespace to a
    Kubernetes source.

    Attributes:
        objects (list of CommonRecoverObjectSnapshotParams): Specifies the
            objects to be recovered.
        rename_recovered_namespaces_params (RenameRecoveredNamespacesParams):
            Specifies params to rename the Namespaces that are recovered. If
            not specified, the original names of the Namespaces are preserved.
            If a name collision occurs then the Namespace being recovered will
            overwrite the Namespace already present on the source.
        recovery_target_config (KubernetesNamespaceRecoveryTargetConfig):
            Specifies the recovery target configuration of the Namespace
            recovery.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "recovery_target_config":'recoveryTargetConfig',
        "rename_recovered_namespaces_params":'renameRecoveredNamespacesParams'
    }

    def __init__(self,
                 objects=None,
                 recovery_target_config=None,
                 rename_recovered_namespaces_params=None):
        """Constructor for the KubernetesTargetParamsForRecoverNamespace class"""

        # Initialize members of the class
        self.objects = objects
        self.rename_recovered_namespaces_params = rename_recovered_namespaces_params
        self.recovery_target_config = recovery_target_config


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
        recovery_target_config = cohesity_management_sdk.models_v2.kubernetes_namespace_recovery_target_config.KubernetesNamespaceRecoveryTargetConfig.from_dictionary(dictionary.get('recoveryTargetConfig')) if dictionary.get('recoveryTargetConfig') else None
        rename_recovered_namespaces_params = cohesity_management_sdk.models_v2.rename_recovered_namespaces_params.RenameRecoveredNamespacesParams.from_dictionary(dictionary.get('renameRecoveredNamespacesParams')) if dictionary.get('renameRecoveredNamespacesParams') else None

        # Return an object of this model
        return cls(objects,
                   recovery_target_config,
                   rename_recovered_namespaces_params)


