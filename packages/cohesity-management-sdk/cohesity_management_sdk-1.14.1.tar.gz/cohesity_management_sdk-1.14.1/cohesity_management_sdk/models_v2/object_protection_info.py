# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.object_protection_group_summary
import cohesity_management_sdk.models_v2.protection_summary

class ObjectProtectionInfo(object):

    """Implementation of the 'ObjectProtectionInfo' model.

    Specifies the object info on clsuter.

    Attributes:
        object_id (long|int): Specifies the object id.
        source_id (long|int): Specifies the source id.
        region_id (string): Specifies the region id where this object belongs
            to.
        cluster_id (long|int): Specifies the cluster id where this object
            belongs to.
        cluster_incarnation_id (long|int): Specifies the cluster incarnation
            id where this object belongs to.
        protection_groups (list of ObjectProtectionGroupSummary): Specifies a
            list of protection groups protecting this object.
        object_backup_configuration (list of ProtectionSummary): Specifies a
            list of object protections.
        last_run_status (LastRunStatusEnum): Specifies the status of the
            object's last protection run.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "object_id":'objectId',
        "source_id":'sourceId',
        "region_id":'regionId',
        "cluster_id":'clusterId',
        "cluster_incarnation_id":'clusterIncarnationId',
        "protection_groups":'protectionGroups',
        "object_backup_configuration":'objectBackupConfiguration',
        "last_run_status":'lastRunStatus'
    }

    def __init__(self,
                 object_id=None,
                 source_id=None,
                 region_id=None,
                 cluster_id=None,
                 cluster_incarnation_id=None,
                 protection_groups=None,
                 object_backup_configuration=None,
                 last_run_status=None):
        """Constructor for the ObjectProtectionInfo class"""

        # Initialize members of the class
        self.object_id = object_id
        self.source_id = source_id
        self.region_id = region_id
        self.cluster_id = cluster_id
        self.cluster_incarnation_id = cluster_incarnation_id
        self.protection_groups = protection_groups
        self.object_backup_configuration = object_backup_configuration
        self.last_run_status = last_run_status


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
        object_id = dictionary.get('objectId')
        source_id = dictionary.get('sourceId')
        region_id = dictionary.get('regionId')
        cluster_id = dictionary.get('clusterId')
        cluster_incarnation_id = dictionary.get('clusterIncarnationId')
        protection_groups = None
        if dictionary.get("protectionGroups") is not None:
            protection_groups = list()
            for structure in dictionary.get('protectionGroups'):
                protection_groups.append(cohesity_management_sdk.models_v2.object_protection_group_summary.ObjectProtectionGroupSummary.from_dictionary(structure))
        object_backup_configuration = None
        if dictionary.get("objectBackupConfiguration") is not None:
            object_backup_configuration = list()
            for structure in dictionary.get('objectBackupConfiguration'):
                object_backup_configuration.append(cohesity_management_sdk.models_v2.protection_summary.ProtectionSummary.from_dictionary(structure))
        last_run_status = dictionary.get('lastRunStatus')

        # Return an object of this model
        return cls(object_id,
                   source_id,
                   region_id,
                   cluster_id,
                   cluster_incarnation_id,
                   protection_groups,
                   object_backup_configuration,
                   last_run_status)


