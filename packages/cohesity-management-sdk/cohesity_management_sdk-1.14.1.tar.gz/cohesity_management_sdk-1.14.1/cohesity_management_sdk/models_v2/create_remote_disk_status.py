# -*- coding: utf-8 -*-


class CreateRemoteDiskStatus(object):

    """Implementation of the 'CreateRemoteDiskStatus' model.

    Specifies the status of creating remote disk.

    Attributes:
        mount_path (string): Specifies the NFS mount path of the remote disk.
        node_id (long|int): Specifies the node id of the disk. If not
            specified, the disk will be evenly distributed across all the
            nodes.
        tier (TierEnum): Specifies the tier of the disk
        status (Status1Enum): Specifies the creating status of this disk.
        message (string): Specifies the error message when creating remote
            disk fails.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "mount_path":'mountPath',
        "node_id":'nodeId',
        "tier":'tier',
        "status":'status',
        "message":'message'
    }

    def __init__(self,
                 mount_path=None,
                 node_id=None,
                 tier=None,
                 status=None,
                 message=None):
        """Constructor for the CreateRemoteDiskStatus class"""

        # Initialize members of the class
        self.mount_path = mount_path
        self.node_id = node_id
        self.tier = tier
        self.status = status
        self.message = message


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
        mount_path = dictionary.get('mountPath')
        node_id = dictionary.get('nodeId')
        tier = dictionary.get('tier')
        status = dictionary.get('status')
        message = dictionary.get('message')

        # Return an object of this model
        return cls(mount_path,
                   node_id,
                   tier,
                   status,
                   message)


