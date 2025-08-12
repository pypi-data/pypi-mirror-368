# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_recover_object_snapshot_params
import cohesity_management_sdk.models_v2.kubernetes_pvc_info
import cohesity_management_sdk.models_v2.rename_recovered_namespaces_params
import cohesity_management_sdk.models_v2.recover_protection_group_run_params
import cohesity_management_sdk.models_v2.kubernetes_namespace_recovery_target_config

class KubernetesTargetParams(object):

    """Implementation of the 'KubernetesTargetParams' model.

    Specifies the params for recovering to a Kubernetes host.

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
        excluded_pvcs (list of KubernetesPvcInfo): Specifies the list of pvc to be excluded from recovery.
        recover_protection_group_runs_params (list of RecoverProtectionGroupRunParams): Specifies the Protection Group Runs params to recover. All the
          VM's that are successfully backed up by specified Runs will be recovered.
          This can be specified along with individual snapshots of VMs. User has to
          make sure that specified Object snapshots and Protection Group Runs should
          not have any intersection. For example, user cannot specify multiple Runs
          which has same Object or an Object snapshot and a Run which has same Object's
          snapshot.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "recovery_target_config":'recoveryTargetConfig',
        "rename_recovered_namespaces_params":'renameRecoveredNamespacesParams',
        "excluded_pvcs":'excludedPvcs',
        "recover_protection_group_runs_params":'recoverProtectionGroupRunsParams'
    }

    def __init__(self,
                 objects=None,
                 recovery_target_config=None,
                 rename_recovered_namespaces_params=None,
                 excluded_pvcs=None,
                 recover_protection_group_runs_params=None):
        """Constructor for the KubernetesTargetParams class"""

        # Initialize members of the class
        self.objects = objects
        self.rename_recovered_namespaces_params = rename_recovered_namespaces_params
        self.recovery_target_config = recovery_target_config
        self.excluded_pvcs = excluded_pvcs
        self.recover_protection_group_runs_params = recover_protection_group_runs_params


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
        excluded_pvcs = None
        if dictionary.get('excludedPvcs') is not None:
            excluded_pvcs = list()
            for structure in dictionary.get('excludedPvcs'):
                excluded_pvcs.append(cohesity_management_sdk.models_v2.kubernetes_pvc_info.KubernetesPvcInfo.from_dictionary(structure))
        recover_protection_group_runs_params = None
        if dictionary.get('recoverProtectionGroupRunsParams') is not None:
            recover_protection_group_runs_params = list()
            for structure in dictionary.get('recoverProtectionGroupRunsParams'):
                recover_protection_group_runs_params.append(cohesity_management_sdk.models_v2.recover_protection_group_run_params.RecoverProtectionGroupRunParams.from_dictionary(structure))

        # Return an object of this model
        return cls(objects,
                   recovery_target_config,
                   rename_recovered_namespaces_params,
                   excluded_pvcs,
                   recover_protection_group_runs_params
                   )