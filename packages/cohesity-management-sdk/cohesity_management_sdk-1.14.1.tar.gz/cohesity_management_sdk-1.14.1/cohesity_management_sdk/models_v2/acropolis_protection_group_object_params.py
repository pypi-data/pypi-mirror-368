# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.acropolis_disk_info

class AcropolisProtectionGroupObjectParams(object):

    """Implementation of the 'AcropolisProtectionGroupObjectParams' model.

    Specifies an object protected by a Acropolis Protection Group.

    Attributes:
        exclude_disks (list of AcropolisDiskInfo): Specifies a list of disks to exclude from being protected. This
          is only applicable to VM objects.
        id (long|int): Specifies the ID of the object.
        include_disks (list of AcropolisDiskInfo): Specifies a list of disks to include in the protection. This
          is only applicable to VM objects.
        name (string): Specifies the name of the virtual machine.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "exclude_disks":'excludeDisks',
        "id":'id',
        "include_disks":'includeDisks',
        "name":'name'
    }

    def __init__(self,
                 exclude_disks=None,
                 id=None,
                 include_disks=None,
                 name=None):
        """Constructor for the AcropolisProtectionGroupObjectParams class"""

        # Initialize members of the class
        self.exclude_disks = exclude_disks
        self.id = id
        self.include_disks = include_disks
        self.name = name


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
        exclude_disks = None
        if dictionary.get("excludeDisks") is not None:
            exclude_disks = list()
            for structure in dictionary.get('excludeDisks'):
                exclude_disks.append(cohesity_management_sdk.models_v2.acropolis_disk_info.AcropolisDiskInfo.from_dictionary(structure))
        id = dictionary.get('id')
        include_disks = None
        if dictionary.get("includeDisks") is not None:
            include_disks = list()
            for structure in dictionary.get('includeDisks'):
                include_disks.append(cohesity_management_sdk.models_v2.acropolis_disk_info.AcropolisDiskInfo.from_dictionary(structure))
        name = dictionary.get('name')

        # Return an object of this model
        return cls(include_disks,
                   id,
                   exclude_disks,
                   name)