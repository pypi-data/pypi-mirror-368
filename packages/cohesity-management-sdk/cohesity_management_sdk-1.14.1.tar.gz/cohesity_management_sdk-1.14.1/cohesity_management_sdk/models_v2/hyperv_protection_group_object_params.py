# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.hyperv_disk_information

class HypervProtectionGroupObjectParams(object):

    """Implementation of the 'HyperV Protection Group Object Params.' model.

    Specifies the object parameters to create HyperV Protection Group.

    Attributes:
        exclude_disks (list of HypervDiskInformation): Specifies a list of disks to exclude from being protected for
          the object/vm.
        id (long|int): Specifies the id of the object.
        include_disks (list of HypervDiskInformation): Specifies a list of disks to included in the protection for the
          object/vm.
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
        """Constructor for the HypervProtectionGroupObjectParams class"""

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
                exclude_disks.append(cohesity_management_sdk.models_v2.hyperv_disk_information.HypervDiskInformation.from_dictionary(structure))
        id = dictionary.get('id')
        include_disks = None
        if dictionary.get("includeDisks") is not None:
            include_disks = list()
            for structure in dictionary.get('includeDisks'):
                include_disks.append(cohesity_management_sdk.models_v2.hyperv_disk_information.HypervDiskInformation.from_dictionary(structure))
        name = dictionary.get('name')

        # Return an object of this model
        return cls(exclude_disks,
                   id,
                   include_disks,
                   name)