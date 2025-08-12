# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.remote_adapter_host
import cohesity_management_sdk.models_v2.remote_adapter_replication_parameters
import cohesity_management_sdk.models_v2.indexing_policy

class RemoteAdapterProtectionGroupParameters(object):

    """Implementation of the 'Remote Adapter Protection Group Parameters' model.

    Specifies the parameters which are specific to Remote Adapter related
    Protection Groups.

    Attributes:
        hosts (list of RemoteAdapterHost): Specifies a list of hosts to
            protected in this protection group.
        view_id (long|int): Specifies the id of the view where we put the
            script result data.
        remote_view_params (RemoteAdapterReplicationParameters): Specifies the
            parameters for Remote Adapter replication.
        indexing_policy (IndexingPolicy): Specifies settings for indexing
            files found in an Object (such as a VM) so these files can be
            searched and recovered. This also specifies inclusion and
            exclusion rules that determine the directories to index.
        app_consistent_snapshot (bool): Specifies whether or not to quiesce
            apps and the file system in order to take app consistent
            snapshots.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "hosts":'hosts',
        "view_id":'viewId',
        "remote_view_params":'remoteViewParams',
        "indexing_policy":'indexingPolicy',
        "app_consistent_snapshot":'appConsistentSnapshot'
    }

    def __init__(self,
                 hosts=None,
                 view_id=None,
                 remote_view_params=None,
                 indexing_policy=None,
                 app_consistent_snapshot=None):
        """Constructor for the RemoteAdapterProtectionGroupParameters class"""

        # Initialize members of the class
        self.hosts = hosts
        self.view_id = view_id
        self.remote_view_params = remote_view_params
        self.indexing_policy = indexing_policy
        self.app_consistent_snapshot = app_consistent_snapshot


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
        hosts = None
        if dictionary.get("hosts") is not None:
            hosts = list()
            for structure in dictionary.get('hosts'):
                hosts.append(cohesity_management_sdk.models_v2.remote_adapter_host.RemoteAdapterHost.from_dictionary(structure))
        view_id = dictionary.get('viewId')
        remote_view_params = cohesity_management_sdk.models_v2.remote_adapter_replication_parameters.RemoteAdapterReplicationParameters.from_dictionary(dictionary.get('remoteViewParams')) if dictionary.get('remoteViewParams') else None
        indexing_policy = cohesity_management_sdk.models_v2.indexing_policy.IndexingPolicy.from_dictionary(dictionary.get('indexingPolicy')) if dictionary.get('indexingPolicy') else None
        app_consistent_snapshot = dictionary.get('appConsistentSnapshot')

        # Return an object of this model
        return cls(hosts,
                   view_id,
                   remote_view_params,
                   indexing_policy,
                   app_consistent_snapshot)


