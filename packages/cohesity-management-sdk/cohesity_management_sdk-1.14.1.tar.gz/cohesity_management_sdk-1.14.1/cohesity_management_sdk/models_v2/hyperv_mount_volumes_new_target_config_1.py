# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_target
import cohesity_management_sdk.models_v2.server_credentials

class HypervMountVolumesNewTargetConfig1(object):

    """Implementation of the 'HyperV Mount Volumes New Target Config.1' model.

    Specifies the configuration for mounting volumes to a new target.

    Attributes:
        mount_target (RecoverTarget): Specifies the target entity to recover
            to.
        server_credentials (ServerCredentials): Specifies credentials to
            access the target server. This is required if the server is of
            Linux OS.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "mount_target":'mountTarget',
        "server_credentials":'serverCredentials'
    }

    def __init__(self,
                 mount_target=None,
                 server_credentials=None):
        """Constructor for the HypervMountVolumesNewTargetConfig1 class"""

        # Initialize members of the class
        self.mount_target = mount_target
        self.server_credentials = server_credentials


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
        mount_target = cohesity_management_sdk.models_v2.recover_target.RecoverTarget.from_dictionary(dictionary.get('mountTarget')) if dictionary.get('mountTarget') else None
        server_credentials = cohesity_management_sdk.models_v2.server_credentials.ServerCredentials.from_dictionary(dictionary.get('serverCredentials')) if dictionary.get('serverCredentials') else None

        # Return an object of this model
        return cls(mount_target,
                   server_credentials)


