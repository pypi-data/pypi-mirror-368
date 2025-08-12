# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.disk_information
import cohesity_management_sdk.models_v2.cdp_object_info
import cohesity_management_sdk.models_v2.vmware_standby_object

class VmwareProtectionGroupObjectParams(object):

    """Implementation of the 'VmwareProtectionGroupObjectParams' model.

    Specifies the input for a protection object in the VMware environment.

    Attributes:
        id (long|int): Specifies the id of the object being protected. This
            can be a leaf level or non leaf level object.
        is_autoprotected (bool): Specifies whether the vm is part of an
            Autoprotection. True implies that the vm or its parent directory
            is autoprotected and will remain part of the autoprotection with
            additional settings specified here. False implies the object is
            not part of an Autoprotection and will remain protected and its
            individual settings here even if a parent directory's
            Autoprotection setting is altered. Default is false.
        exclude_disks (list of DiskInformation): Specifies a list of disks to
            exclude from being protected. This is only applicable to VM
            objects.
        truncate_exchange_logs (bool): Specifies whether or not to truncate MS
            Exchange logs while taking an app consistent snapshot of this
            object. This is only applicable to objects which have a registered
            MS Exchange app.
        name (string): Specifies the name of the virtual machine.
        cdp_info (CdpObjectInfo): Specifies the CDP related information for a
            given object. This field will only be populated when protection
            group is configured with policy having CDP retention settings.
        standby_info (VmwareStandbyObject): Specifies the standby related information for a given object.
            This field will only be populated when standby is configured in backup
            job settings.
        type (Type57Enum): Specifies the type of the VMware object.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "is_autoprotected":'isAutoprotected',
        "exclude_disks":'excludeDisks',
        "truncate_exchange_logs":'truncateExchangeLogs',
        "name":'name',
        "cdp_info":'cdpInfo',
        "standby_info":'standbyInfo',
        "mtype":'type'

    }

    def __init__(self,
                 id=None,
                 is_autoprotected=None,
                 exclude_disks=None,
                 truncate_exchange_logs=None,
                 name=None,
                 cdp_info=None,
                 standby_info=None,
                 mtype=None):
        """Constructor for the VmwareProtectionGroupObjectParams class"""

        # Initialize members of the class
        self.id = id
        self.is_autoprotected = is_autoprotected
        self.exclude_disks = exclude_disks
        self.truncate_exchange_logs = truncate_exchange_logs
        self.name = name
        self.cdp_info = cdp_info
        self.standby_info = standby_info
        self.mtype = mtype


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
        is_autoprotected = dictionary.get('isAutoprotected')
        exclude_disks = None
        if dictionary.get("excludeDisks") is not None:
            exclude_disks = list()
            for structure in dictionary.get('excludeDisks'):
                exclude_disks.append(cohesity_management_sdk.models_v2.disk_information.DiskInformation.from_dictionary(structure))
        truncate_exchange_logs = dictionary.get('truncateExchangeLogs')
        name = dictionary.get('name')
        cdp_info = cohesity_management_sdk.models_v2.cdp_object_info.CdpObjectInfo.from_dictionary(dictionary.get('cdpInfo')) if dictionary.get('cdpInfo') else None
        standby_info = cohesity_management_sdk.models_v2.vmware_standby_object.VmwareStandbyObject.from_dictionary(dictionary.get('standbyInfo')) if dictionary.get('standbyInfo') else None
        mtype = dictionary.get('type')

        # Return an object of this model
        return cls(id,
                   is_autoprotected,
                   exclude_disks,
                   truncate_exchange_logs,
                   name,
                   cdp_info,
                   standby_info,
                   mtype)