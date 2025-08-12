# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.disk_information

class VmwareObjectProtectionRequest(object):

    """Implementation of the 'VmwareObjectProtectionRequest' model.

    Specifies the VMware object level settings for object protection.

    Attributes:
        id (long|int): Specifies the id of the object being protected. This
            can be a leaf level or non leaf level object.
        exclude_object_ids (list of long|int): Specifies the list of IDs of
            the objects to not be protected in this backup. This field only
            applies if provided object id is non leaf entity such as Tag or a
            folder. This can be used to ignore specific objects under a parent
            object which has been included for protection.
        exclude_disks (list of DiskInformation): Specifies a list of disks to
            exclude from being protected. This is only applicable to VM
            objects.
        truncate_exchange_logs (bool): Specifies whether or not to truncate MS
            Exchange logs while taking an app consistent snapshot of this
            object. This is only applicable to objects which have a registered
            MS Exchange app.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "exclude_object_ids":'excludeObjectIds',
        "exclude_disks":'excludeDisks',
        "truncate_exchange_logs":'truncateExchangeLogs'
    }

    def __init__(self,
                 id=None,
                 exclude_object_ids=None,
                 exclude_disks=None,
                 truncate_exchange_logs=None):
        """Constructor for the VmwareObjectProtectionRequest class"""

        # Initialize members of the class
        self.id = id
        self.exclude_object_ids = exclude_object_ids
        self.exclude_disks = exclude_disks
        self.truncate_exchange_logs = truncate_exchange_logs


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
        id = dictionary.get('id')
        exclude_object_ids = dictionary.get('excludeObjectIds')
        exclude_disks = None
        if dictionary.get("excludeDisks") is not None:
            exclude_disks = list()
            for structure in dictionary.get('excludeDisks'):
                exclude_disks.append(cohesity_management_sdk.models_v2.disk_information.DiskInformation.from_dictionary(structure))
        truncate_exchange_logs = dictionary.get('truncateExchangeLogs')

        # Return an object of this model
        return cls(id,
                   exclude_object_ids,
                   exclude_disks,
                   truncate_exchange_logs)


