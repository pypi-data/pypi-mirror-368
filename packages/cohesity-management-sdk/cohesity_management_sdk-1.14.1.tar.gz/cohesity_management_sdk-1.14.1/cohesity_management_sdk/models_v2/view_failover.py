# -*- coding: utf-8 -*-


class ViewFailover(object):

    """Implementation of the 'ViewFailover' model.

    Specifies the failover status of a view.

    Attributes:
        is_failover_ready (bool): Specifies if the view is ready for failover.
        remote_view_id (long|int): Specifies the remote view id.
        remote_cluster_id (long|int): Specifies the remote cluster id.
        remote_cluster_incarnation_id (long|int): Specifies the remote cluster
            incarnation id.
        view_uid (string): View uid.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "is_failover_ready":'isFailoverReady',
        "remote_view_id":'remoteViewId',
        "remote_cluster_id":'remoteClusterId',
        "remote_cluster_incarnation_id":'remoteClusterIncarnationId',
        "view_uid":'viewUid'
    }

    def __init__(self,
                 is_failover_ready=None,
                 remote_view_id=None,
                 remote_cluster_id=None,
                 remote_cluster_incarnation_id=None,
                 view_uid=None):
        """Constructor for the ViewFailover class"""

        # Initialize members of the class
        self.is_failover_ready = is_failover_ready
        self.remote_view_id = remote_view_id
        self.remote_cluster_id = remote_cluster_id
        self.remote_cluster_incarnation_id = remote_cluster_incarnation_id
        self.view_uid = view_uid


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
        is_failover_ready = dictionary.get('isFailoverReady')
        remote_view_id = dictionary.get('remoteViewId')
        remote_cluster_id = dictionary.get('remoteClusterId')
        remote_cluster_incarnation_id = dictionary.get('remoteClusterIncarnationId')
        view_uid = dictionary.get('viewUid')

        # Return an object of this model
        return cls(is_failover_ready,
                   remote_view_id,
                   remote_cluster_id,
                   remote_cluster_incarnation_id,
                   view_uid)