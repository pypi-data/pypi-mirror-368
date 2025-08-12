# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.kubernetes_protection_group_object_params
import cohesity_management_sdk.models_v2.vlan_params_for_backup_restore_operation
import cohesity_management_sdk.models_v2.kubernetes_filter_params

class KubernetesProtectionGroupParams(object):

    """Implementation of the 'KubernetesProtectionGroupParams' model.

    Specifies the parameters which are related to Kubernetes Protection
    Groups.

    Attributes:
        objects (list of KubernetesProtectionGroupObjectParams): Specifies the
            objects included in the Protection Group.
        exclude_label_ids (list of long|int): Array of arrays of label IDs that specify labels to exclude.
          Optionally specify a list of labels to exclude from protecting by listing
          protection source ids of labels in this two dimensional array. Using this
          two dimensional array of label IDs, the Cluster generates a list of namespaces
          to exclude from protecting, which are derived from intersections of the
          inner arrays and union of the outer array
        exclude_params (KubernetesFilterParams): Specifies the paramaters to exclude objects attached to Kubernetes
          pods. Exclusion takes precedence over inclusion.
        exclude_object_ids (list of long|int): Specifies the objects to be
            excluded in the Protection Group.
        include_params ( KubernetesFilterParams): Specifies the paramaters to include objects (e.g.: volumes)
          attached to Kubernetes pods. If not populated, all objects are included
          unless specifically excluded otherwise.
        label_ids (list of long|int): Array of array of label IDs that specify labels to protect. Optionally
          specify a list of labels to protect by listing protection source ids of
          labels in this two dimensional array. Using this two dimensional array of
          label IDs, the cluster generates a list of namespaces to protect, which
          are derived from intersections of the inner arrays and union of the outer
          array.
        leverage_csi_snapshot (bool): Specifies if CSI snapshots should be used for backup of namespaces.
        source_id (long|int): Specifies the id of the parent of the objects.
        source_name (string): Specifies the name of the parent of the
            objects.
        vlan_params (VlanParams): Specifies the VLAN preference that is selected by the user for
          doing backup.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "exclude_label_ids" : 'excludeLabelIds' ,
        "exclude_params":'excludeParams',
        "exclude_object_ids":'excludeObjectIds',
        "include_params":'includeParams',
        "label_ids":'labelIds',
        "leverage_csi_snapshot":'leverageCSISnapshot',
        "source_id":'sourceId',
        "source_name":'sourceName',
        "vlan_params" : 'vlanParams'
    }

    def __init__(self,
                 objects=None,
                 exclude_label_ids=None,
                 exclude_params=None,
                 exclude_object_ids=None,
                 include_params=None,
                 label_ids=None,
                 leverage_csi_snapshot=None,
                 source_id=None,
                 source_name=None,
                 vlan_params=None):
        """Constructor for the KubernetesProtectionGroupParams class"""

        # Initialize members of the class
        self.objects = objects
        self.exclude_label_ids = exclude_label_ids
        self.exclude_params = exclude_params
        self.exclude_object_ids = exclude_object_ids
        self.include_params = include_params
        self.label_ids = label_ids
        self.leverage_csi_snapshot = leverage_csi_snapshot
        self.source_id = source_id
        self.source_name = source_name
        self.vlan_params = vlan_params


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
                objects.append(cohesity_management_sdk.models_v2.kubernetes_protection_group_object_params.KubernetesProtectionGroupObjectParams.from_dictionary(structure))
        exclude_label_ids = dictionary.get('excludeLabelIds')
        exclude_params = cohesity_management_sdk.models_v2.kubernetes_filter_params.KubernetesFilterParams.from_dictionary(dictionary.get('excludeParams')) if dictionary.get('excludeParams') else None
        exclude_object_ids = dictionary.get('excludeObjectIds')
        include_params = cohesity_management_sdk.models_v2.kubernetes_filter_params.KubernetesFilterParams.from_dictionary(dictionary.get('includeParams')) if dictionary.get('includeParams') else None
        label_ids = dictionary.get('labelIds')
        leverage_csi_snapshot = dictionary.get('leverageCSISnapshot')
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')
        vlan_params = cohesity_management_sdk.models_v2.vlan_params_for_backup_restore_operation.VlanParamsForBackupRestoreOperation.from_dictionary(dictionary.get('vlanParams')) if dictionary.get('vlanParams') else None

        # Return an object of this model
        return cls(
                   objects,
                   exclude_label_ids,
                   exclude_params,
                   exclude_object_ids,
                   include_params,
                   label_ids,
                   leverage_csi_snapshot,
                   source_id,
                   source_name,
                   vlan_params)