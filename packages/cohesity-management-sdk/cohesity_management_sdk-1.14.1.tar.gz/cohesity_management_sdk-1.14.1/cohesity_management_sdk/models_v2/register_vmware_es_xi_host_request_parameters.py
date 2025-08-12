# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.datastore_params

class RegisterVmwareESXiHostRequestParameters(object):

    """Implementation of the 'Register VMware ESXi host request parameters.' model.

    Specifies parameters to register VMware ESXi host.

    Attributes:
        username (string): Specifies the username to access target entity.
        password (string): Specifies the password to access target entity.
        endpoint (string): Specifies the endpoint IPaddress, URL or hostname
            of the host.
        description (string): Specifies the description of the source being
            registered.
        min_free_datastore_space_for_backup_gb (long|int): Specifies the
            minimum free space (in GB) expected to be available in the
            datastore where the virtual disks of the VM being backed up
            reside. If the space available is lower than the specified value,
            backup will be aborted.
        min_free_datastore_space_for_backup_percentage (long|int): Specifies the minimum free space (in percentage) expected to
            be available in the datastore where the virtual disks of the VM being
            backed up reside. If the space available is lower than the specified value,
            backup will be aborted.
        max_concurrent_streams (int): If this value is > 0 and the number of
            streams concurrently active on a datastore is equal to it, then
            any further requests to access the datastore would be denied until
            the number of active streams reduces. This applies for all the
            datastores in the specified host.
        data_store_params (list of DatastoreParams): Specifies the datastore
            specific params.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "username":'username',
        "password":'password',
        "endpoint":'endpoint',
        "description":'description',
        "min_free_datastore_space_for_backup_gb":'minFreeDatastoreSpaceForBackupGb',
        "min_free_datastore_space_for_backup_percentage":'minFreeDatastoreSpaceForBackupPercentage',
        "max_concurrent_streams":'maxConcurrentStreams',
        "data_store_params":'dataStoreParams'
    }

    def __init__(self,
                 username=None,
                 password=None,
                 endpoint=None,
                 description=None,
                 min_free_datastore_space_for_backup_gb=None,
                 min_free_datastore_space_for_backup_percentage=None,
                 max_concurrent_streams=None,
                 data_store_params=None):
        """Constructor for the RegisterVmwareESXiHostRequestParameters class"""

        # Initialize members of the class
        self.username = username
        self.password = password
        self.endpoint = endpoint
        self.description = description
        self.min_free_datastore_space_for_backup_gb = min_free_datastore_space_for_backup_gb
        self.min_free_datastore_space_for_backup_percentage = min_free_datastore_space_for_backup_percentage
        self.max_concurrent_streams = max_concurrent_streams
        self.data_store_params = data_store_params


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
        username = dictionary.get('username')
        password = dictionary.get('password')
        endpoint = dictionary.get('endpoint')
        description = dictionary.get('description')
        min_free_datastore_space_for_backup_gb = dictionary.get('minFreeDatastoreSpaceForBackupGb')
        min_free_datastore_space_for_backup_percentage = dictionary.get('minFreeDatastoreSpaceForBackupPercentage')
        max_concurrent_streams = dictionary.get('maxConcurrentStreams')
        data_store_params = None
        if dictionary.get("dataStoreParams") is not None:
            data_store_params = list()
            for structure in dictionary.get('dataStoreParams'):
                data_store_params.append(cohesity_management_sdk.models_v2.datastore_params.DatastoreParams.from_dictionary(structure))

        # Return an object of this model
        return cls(username,
                   password,
                   endpoint,
                   description,
                   min_free_datastore_space_for_backup_gb,
                   min_free_datastore_space_for_backup_percentage,
                   max_concurrent_streams,
                   data_store_params)