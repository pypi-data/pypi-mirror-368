# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.failover_objects

class ReplicationBackupActivation(object):

    """Implementation of the 'ReplicationBackupActivation' model.

    Specifies the request parmeters to activate the backup of failover
    entities on replication cluster.

    Attributes:
        objects (list of FailoverObjects): Specifies the list of failover
            object that need to be protected on replication cluster. If the
            object set that was sent earlier is provided again then API will
            return an error. If this objects list is not specified then
            internally it will be inferred if '/objectLinkage' API has been
            called previously.
        protection_group_id (string): Specifies the protection group id that
            will be used for backing up the failover entities on replication
            cluster. This is a optional argument and only need to be passed if
            user wants to use the existing job for the backup. If specified
            then Orchastrator should enusre that protection group is
            compatible to handle all provided failover objects.
        enable_reverse_replication (bool): If this is specifed as true, then
            reverse replication of failover objects will be enabled from
            replication cluster to source cluster. If source cluster is not
            reachable, then replications will fail until source cluster comes
            up again. Here orchastrator should also ensure that storage domain
            on replication cluster is correctly mapped to the same storage
            domain on the source cluster.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "protection_group_id":'protectionGroupId',
        "enable_reverse_replication":'enableReverseReplication'
    }

    def __init__(self,
                 objects=None,
                 protection_group_id=None,
                 enable_reverse_replication=None):
        """Constructor for the ReplicationBackupActivation class"""

        # Initialize members of the class
        self.objects = objects
        self.protection_group_id = protection_group_id
        self.enable_reverse_replication = enable_reverse_replication


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
                objects.append(cohesity_management_sdk.models_v2.failover_objects.FailoverObjects.from_dictionary(structure))
        protection_group_id = dictionary.get('protectionGroupId')
        enable_reverse_replication = dictionary.get('enableReverseReplication')

        # Return an object of this model
        return cls(objects,
                   protection_group_id,
                   enable_reverse_replication)


