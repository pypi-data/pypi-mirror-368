# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.remote_disk

class RemoteDisks(object):

    """Implementation of the 'Remote disks' model.

    Specifies a list of remote disks.

    Attributes:
        remote_disks (list of RemoteDisk): Specifies a list of remote disks.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "remote_disks":'remoteDisks'
    }

    def __init__(self,
                 remote_disks=None):
        """Constructor for the RemoteDisks class"""

        # Initialize members of the class
        self.remote_disks = remote_disks


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
        remote_disks = None
        if dictionary.get("remoteDisks") is not None:
            remote_disks = list()
            for structure in dictionary.get('remoteDisks'):
                remote_disks.append(cohesity_management_sdk.models_v2.remote_disk.RemoteDisk.from_dictionary(structure))

        # Return an object of this model
        return cls(remote_disks)


