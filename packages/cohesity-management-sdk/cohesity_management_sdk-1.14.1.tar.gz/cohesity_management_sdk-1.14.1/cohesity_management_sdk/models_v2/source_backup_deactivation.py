# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.failover_objects

class SourceBackupDeactivation(object):

    """Implementation of the 'SourceBackupDeactivation' model.

    Specifies the request parmeters to deactivate the backup of failover
    entities on source cluster.

    Attributes:
        replication_cluster_id (long|int): Specifies the replication cluster
            Id involved in failover operation.
        view_id (string): If failover is initiated by view based orchastrator,
            then this field specifies the local view id of source cluster
            which is being failed over. Backup will be deactivated for view
            object.
        objects (list of FailoverObjects): Specifies the list of all local
            entity ids of all the objects being failed from the source
            cluster. Backup will be deactiaved for all given objects.
        protection_group_id (string): Specifies the protection group id of the
            source cluster from where the objects being failed over. If this
            is not specified then it will be infer from the list of objects
            being failed over.
        keep_failover_objects (bool): If this is set to true then objects will
            not be removed from protection group. If this is set to false,
            then all objects which are being failed over will be removed from
            the protection group. If protection group left with zero entities
            then it will be paused automatically.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "replication_cluster_id":'replicationClusterId',
        "view_id":'viewId',
        "objects":'objects',
        "protection_group_id":'protectionGroupId',
        "keep_failover_objects":'keepFailoverObjects'
    }

    def __init__(self,
                 replication_cluster_id=None,
                 view_id=None,
                 objects=None,
                 protection_group_id=None,
                 keep_failover_objects=None):
        """Constructor for the SourceBackupDeactivation class"""

        # Initialize members of the class
        self.replication_cluster_id = replication_cluster_id
        self.view_id = view_id
        self.objects = objects
        self.protection_group_id = protection_group_id
        self.keep_failover_objects = keep_failover_objects


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
        replication_cluster_id = dictionary.get('replicationClusterId')
        view_id = dictionary.get('viewId')
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.failover_objects.FailoverObjects.from_dictionary(structure))
        protection_group_id = dictionary.get('protectionGroupId')
        keep_failover_objects = dictionary.get('keepFailoverObjects')

        # Return an object of this model
        return cls(replication_cluster_id,
                   view_id,
                   objects,
                   protection_group_id,
                   keep_failover_objects)


