# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.san_storage_array
import cohesity_management_sdk.models.san_volume

class IbmFlashSystemProtectionSource(object):

    """Implementation of the 'IbmFlashSystemProtectionSource' model.

    Specifies a Protection Source in a Ibm Flash System environment.

    Attributes:
        name (string): Specifies a unique name of the Protection Source
        storage_array (SanStorageArray): 'Specifies a SAN Storage Array information.
           This is set only when the type is kStorageArray.
        mtype (TypeIbmFlashSystemProtectionSourceEnum): Specifies the type of
            managed Object in a SAN/Ibm Flash System Protection
            Source like a kStorageArray or kVolume
        volume (SanVolume): Specifies a SAN Volume information within a storage array.
            This is set only when the type is kVolume.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "storage_array":'storageArray',
        "mtype":'type',
        "volume":'volume'
    }

    def __init__(self,
                 name=None,
                 storage_array=None,
                 mtype=None,
                 volume=None):
        """Constructor for the IbmFlashSystemProtectionSource class"""

        # Initialize members of the class
        self.name = name
        self.storage_array = storage_array
        self.mtype = mtype
        self.volume = volume


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
        name = dictionary.get('name')
        storage_array = cohesity_management_sdk.models.san_storage_array.SanStorageArray.from_dictionary(dictionary.get('storageArray')) if dictionary.get('storageArray') else None
        mtype = dictionary.get('type')
        volume = cohesity_management_sdk.models.san_volume.SanVolume.from_dictionary(dictionary.get('volume')) if dictionary.get('volume') else None

        # Return an object of this model
        return cls(name,
                   storage_array,
                   mtype,
                   volume)


