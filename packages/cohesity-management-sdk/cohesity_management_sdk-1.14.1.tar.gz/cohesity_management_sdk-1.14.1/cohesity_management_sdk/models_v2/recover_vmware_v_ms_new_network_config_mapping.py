# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.recovery_object_identifier
import  cohesity_management_sdk.models_v2.org_vdc_network

class RecoverVmwareVmNewNetworkConfigMapping(object):

    """Implementation of the 'RecoverVmwareVmNewNetworkConfigMapping' model.

    Specifies source VMs NIC to target network mapping for the VMware
      VMs being recovered.

    Attributes:
        disable_network (bool): Specifies whether the attached network should be left in disabled
          state for this mapping. Default is false.
        network_adapter_name (string): Name of the VM's network adapter name.
        org_vdc_network (OrgVDCNetwork): Specifies the VDC organization network that will be attached
          to the recovered VM for the given network adapter and source network entity.
        preserve_mac_address (bool): Specifies whether to preserve the MAC address of the source network
          entity while attaching to the new target network. Default is false.
        source_network_entity (RecoveryObjectIdentifier): Specifies the source VM's network port group (i.e, either a standard
          switch port group or a distributed port group or an opaque network) which
          is associated with specified network adapter name for which mapping is selected.
        target_network_entity (RecoveryObjectIdentifier): Specifies the network port group (i.e, either a standard switch
          port group or a distributed port group or an opaque network) that will attached
          as backing device on the recovered object for the given network adapter
          name and source network entity.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "disable_network":'disableNetwork',
        "network_adapter_name":'networkAdapterName',
        "org_vdc_network":'orgVdcNetwork',
        "preserve_mac_address":'preserveMacAddress',
        "source_network_entity":'sourceNetworkEntity',
        "target_network_entity":'targetNetworkEntity'
    }

    def __init__(self,
                 disable_network=None,
                 network_adapter_name=None,
                 org_vdc_network=None,
                 preserve_mac_address=None,
                 source_network_entity=None,
                 target_network_entity=None):
        """Constructor for the RecoverVmwareVmNewNetworkConfigMapping class"""

        # Initialize members of the class
        self.disable_network = disable_network
        self.network_adapter_name = network_adapter_name
        self.org_vdc_network = org_vdc_network
        self.preserve_mac_address = preserve_mac_address
        self.source_network_entity = source_network_entity
        self.target_network_entity = target_network_entity


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
        disable_network = dictionary.get('disableNetwork')
        network_adapter_name = dictionary.get('networkAdapterName')
        org_vdc_network = cohesity_management_sdk.models_v2.org_vdc_network.OrgVDCNetwork.from_dictionary(dictionary.get('orgVdcNetwork')) if dictionary.get('orgVdcNetwork') else None
        preserve_mac_address = dictionary.get('preserveMacAddress')
        source_network_entity = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(dictionary.get('sourceNetworkEntity')) if dictionary.get('sourceNetworkEntity') else None
        target_network_entity = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(dictionary.get('targetNetworkEntity')) if dictionary.get('targetNetworkEntity') else None

        # Return an object of this model
        return cls(disable_network,
                   network_adapter_name,
                   org_vdc_network,
                   preserve_mac_address,
                   source_network_entity,
                   target_network_entity)