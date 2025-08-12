# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.target_vm_credentials_6

class OriginalTargetConfig3(object):

    """Implementation of the 'OriginalTargetConfig3' model.

    Specifies the configuration for mounting to the original target.

    Attributes:
        bring_disks_online (bool): Specifies whether the volumes need to be
            online within the target environment after attaching the disks.
            For linux VMs, this should always be set to true. For Windows,
            this is optional. If this is set to true, VMware tools must be
            installed on the VM. If this is set to false, useExistingAgent and
            targetCredentials are not needed.
        use_existing_agent (bool): Specifies whether this will use an existing
            agent on the target vm or will deploy a new agent. This is
            required if bringDisksOnline is set to true.
        target_vm_credentials (TargetVmCredentials6): Specifies credentials to
            access the target VM. This is required if bringDisksOnline is set
            to true and useExistingAgent set to false.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "bring_disks_online":'bringDisksOnline',
        "use_existing_agent":'useExistingAgent',
        "target_vm_credentials":'targetVmCredentials'
    }

    def __init__(self,
                 bring_disks_online=None,
                 use_existing_agent=None,
                 target_vm_credentials=None):
        """Constructor for the OriginalTargetConfig3 class"""

        # Initialize members of the class
        self.bring_disks_online = bring_disks_online
        self.use_existing_agent = use_existing_agent
        self.target_vm_credentials = target_vm_credentials


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
        bring_disks_online = dictionary.get('bringDisksOnline')
        use_existing_agent = dictionary.get('useExistingAgent')
        target_vm_credentials = cohesity_management_sdk.models_v2.target_vm_credentials_6.TargetVmCredentials6.from_dictionary(dictionary.get('targetVmCredentials')) if dictionary.get('targetVmCredentials') else None

        # Return an object of this model
        return cls(bring_disks_online,
                   use_existing_agent,
                   target_vm_credentials)


