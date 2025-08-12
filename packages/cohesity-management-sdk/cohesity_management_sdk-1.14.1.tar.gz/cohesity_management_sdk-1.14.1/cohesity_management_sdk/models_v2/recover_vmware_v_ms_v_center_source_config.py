# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recovery_object_identifier
import cohesity_management_sdk.models_v2.network_config_5

class RecoverVmwareVMsVCenterSourceConfig(object):

    """Implementation of the 'Recover VMware VMs vCenter Source Config.' model.

    Specifies the new destination Source configuration where the VMs will be
    recovered for vCenter sources.

    Attributes:
        source (RecoveryObjectIdentifier): Specifies the id of the parent source to recover the
            VMs.
        resource_pool (RecoveryObjectIdentifier): Specifies the resource pool object where
            the recovered objects will be attached.
        datastores (list of RecoveryObjectIdentifier): Specifies the datastore
            objects where the object's files should be recovered to.
        vm_folder (RecoveryObjectIdentifier): Folder where the VMs should be created.
        network_config (NetworkConfig5): Specifies the networking
            configuration to be applied to the recovered VMs.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source":'source',
        "resource_pool":'resourcePool',
        "datastores":'datastores',
        "vm_folder":'vmFolder',
        "network_config":'networkConfig'
    }

    def __init__(self,
                 source=None,
                 resource_pool=None,
                 datastores=None,
                 vm_folder=None,
                 network_config=None):
        """Constructor for the RecoverVmwareVMsVCenterSourceConfig class"""

        # Initialize members of the class
        self.source = source
        self.resource_pool = resource_pool
        self.datastores = datastores
        self.vm_folder = vm_folder
        self.network_config = network_config


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
        source = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(dictionary.get('source')) if dictionary.get('source') else None
        resource_pool = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(dictionary.get('resourcePool')) if dictionary.get('resourcePool') else None
        datastores = None
        if dictionary.get("datastores") is not None:
            datastores = list()
            for structure in dictionary.get('datastores'):
                datastores.append(cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(structure))
        vm_folder = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(dictionary.get('vmFolder')) if dictionary.get('vmFolder') else None
        network_config = cohesity_management_sdk.models_v2.network_config_5.NetworkConfig5.from_dictionary(dictionary.get('networkConfig')) if dictionary.get('networkConfig') else None

        # Return an object of this model
        return cls(source,
                   resource_pool,
                   datastores,
                   vm_folder,
                   network_config)