# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.disk_information

class CommonVmwareObjectParams(object):

    """Implementation of the 'CommonVmwareObjectParams' model.

    Specifies the common object parameters required for VMware protection.

    Attributes:
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
        "exclude_disks":'excludeDisks',
        "truncate_exchange_logs":'truncateExchangeLogs'
    }

    def __init__(self,
                 exclude_disks=None,
                 truncate_exchange_logs=None):
        """Constructor for the CommonVmwareObjectParams class"""

        # Initialize members of the class
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
        exclude_disks = None
        if dictionary.get("excludeDisks") is not None:
            exclude_disks = list()
            for structure in dictionary.get('excludeDisks'):
                exclude_disks.append(cohesity_management_sdk.models_v2.disk_information.DiskInformation.from_dictionary(structure))
        truncate_exchange_logs = dictionary.get('truncateExchangeLogs')

        # Return an object of this model
        return cls(exclude_disks,
                   truncate_exchange_logs)


