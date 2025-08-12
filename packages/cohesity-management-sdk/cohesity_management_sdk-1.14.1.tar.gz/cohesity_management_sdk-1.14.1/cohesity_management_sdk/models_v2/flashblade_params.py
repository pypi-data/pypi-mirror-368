# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.flash_blade_registration_info

class FlashbladeParams(object):

    """Implementation of the 'FlashbladeParams' model.

    Specifies the information related to Registered Pure Flashblade.

    Attributes:
        registration_params (FlashBladeRegistrationInfo): Specifies the
            information specific to flashblade registration.
        uuid (string): Specifies uuid of the pure flashblade server.
        assigned_data_vips (list of string): Specifies list of data vips that
            are assigned to cohesity cluster to create nfs share mountpoints.
        assigned_capacity_bytes (long|int): Specifies the capacity in bytes
            assigned on pure flashblade for remote storage usage on cohesity
            cluster.
        is_dedicated_storage (bool): If true, cohesity cluster uses all
            available capacity on pure flashblade for remote storage.
        available_data_vips (list of string): Available data vips configured
            on pure flashblade.
        available_capacity (long|int): Available capacity on pure flashblade.
        created_file_system_count (long|int): Number of new file systems
            created on pure flashblade when assignedCapacityBytes is updated.
        updated_file_system_count (long|int): Number of file systems that are
            updated on pure flashblade when assignedCapacityBytes is updated.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "registration_params":'registrationParams',
        "uuid":'uuid',
        "assigned_data_vips":'assignedDataVips',
        "assigned_capacity_bytes":'assignedCapacityBytes',
        "is_dedicated_storage":'isDedicatedStorage',
        "available_data_vips":'availableDataVips',
        "available_capacity":'availableCapacity',
        "created_file_system_count":'createdFileSystemCount',
        "updated_file_system_count":'updatedFileSystemCount'
    }

    def __init__(self,
                 registration_params=None,
                 uuid=None,
                 assigned_data_vips=None,
                 assigned_capacity_bytes=None,
                 is_dedicated_storage=None,
                 available_data_vips=None,
                 available_capacity=None,
                 created_file_system_count=None,
                 updated_file_system_count=None):
        """Constructor for the FlashbladeParams class"""

        # Initialize members of the class
        self.registration_params = registration_params
        self.uuid = uuid
        self.assigned_data_vips = assigned_data_vips
        self.assigned_capacity_bytes = assigned_capacity_bytes
        self.is_dedicated_storage = is_dedicated_storage
        self.available_data_vips = available_data_vips
        self.available_capacity = available_capacity
        self.created_file_system_count = created_file_system_count
        self.updated_file_system_count = updated_file_system_count


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
        registration_params = cohesity_management_sdk.models_v2.flash_blade_registration_info.FlashBladeRegistrationInfo.from_dictionary(dictionary.get('registrationParams')) if dictionary.get('registrationParams') else None
        uuid = dictionary.get('uuid')
        assigned_data_vips = dictionary.get('assignedDataVips')
        assigned_capacity_bytes = dictionary.get('assignedCapacityBytes')
        is_dedicated_storage = dictionary.get('isDedicatedStorage')
        available_data_vips = dictionary.get('availableDataVips')
        available_capacity = dictionary.get('availableCapacity')
        created_file_system_count = dictionary.get('createdFileSystemCount')
        updated_file_system_count = dictionary.get('updatedFileSystemCount')

        # Return an object of this model
        return cls(registration_params,
                   uuid,
                   assigned_data_vips,
                   assigned_capacity_bytes,
                   is_dedicated_storage,
                   available_data_vips,
                   available_capacity,
                   created_file_system_count,
                   updated_file_system_count)


