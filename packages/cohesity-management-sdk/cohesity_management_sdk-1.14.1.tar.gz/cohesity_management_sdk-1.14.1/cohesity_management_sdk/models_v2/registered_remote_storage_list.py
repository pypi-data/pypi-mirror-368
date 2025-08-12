# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.remote_storage_registration_parameters

class RegisteredRemoteStorageList(object):

    """Implementation of the 'Registered Remote Storage List' model.

    Specifies information about registered remote storage servers which are
    used by cohesity cluster.

    Attributes:
        remote_storages (list of RemoteStorageRegistrationParameters):
            Specifies the list of registered remote storage info.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "remote_storages":'remoteStorages'
    }

    def __init__(self,
                 remote_storages=None):
        """Constructor for the RegisteredRemoteStorageList class"""

        # Initialize members of the class
        self.remote_storages = remote_storages


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
        remote_storages = None
        if dictionary.get("remoteStorages") is not None:
            remote_storages = list()
            for structure in dictionary.get('remoteStorages'):
                remote_storages.append(cohesity_management_sdk.models_v2.remote_storage_registration_parameters.RemoteStorageRegistrationParameters.from_dictionary(structure))

        # Return an object of this model
        return cls(remote_storages)


