# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.disk_information
import cohesity_management_sdk.models_v2.vmware_cdp_object

class VmwareObjectProtectionResponse(object):

    """Implementation of the 'VmwareObjectProtectionResponse' model.

    Specifies the input for a protection object in the VMware environment.

    Attributes:
        exclude_disks (list of DiskInformation): Specifies a list of disks to
            exclude from being protected. This is only applicable to VM
            objects.
        truncate_exchange_logs (bool): Specifies whether or not to truncate MS
            Exchange logs while taking an app consistent snapshot of this
            object. This is only applicable to objects which have a registered
            MS Exchange app.
        exclude_object_ids (list of long|int): Specifies the list of IDs of
            the objects to not be protected in this backup. This field only
            applies if provided object id is non leaf entity such as Tag or a
            folder. This can be used to ignore specific objects under a parent
            object which has been included for protection.
        cdp_info (VmwareCdpObject): Specifies the VMware specific CDP object
            details.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "exclude_disks":'excludeDisks',
        "truncate_exchange_logs":'truncateExchangeLogs',
        "exclude_object_ids":'excludeObjectIds',
        "cdp_info":'cdpInfo'
    }

    def __init__(self,
                 exclude_disks=None,
                 truncate_exchange_logs=None,
                 exclude_object_ids=None,
                 cdp_info=None):
        """Constructor for the VmwareObjectProtectionResponse class"""

        # Initialize members of the class
        self.exclude_disks = exclude_disks
        self.truncate_exchange_logs = truncate_exchange_logs
        self.exclude_object_ids = exclude_object_ids
        self.cdp_info = cdp_info


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
                exclude_disks.append(cohesity_management_sdk.models_v2.disk_information.DiskInformation.from_dictionary(structure))
        truncate_exchange_logs = dictionary.get('truncateExchangeLogs')
        exclude_object_ids = dictionary.get('excludeObjectIds')
        cdp_info = cohesity_management_sdk.models_v2.vmware_cdp_object.VmwareCdpObject.from_dictionary(dictionary.get('cdpInfo')) if dictionary.get('cdpInfo') else None

        # Return an object of this model
        return cls(exclude_disks,
                   truncate_exchange_logs,
                   exclude_object_ids,
                   cdp_info)


