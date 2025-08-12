# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recovery_object_identifier
import cohesity_management_sdk.models_v2.network_config_5
import cohesity_management_sdk.models_v2.vcd_storage_profile_params
import cohesity_management_sdk.models_v2.org_vdc_network

class RecoverVmwareVMsVcloudDirectorSourceConfig1(object):

    """Implementation of the 'Recover VMware VMs vCloudDirector Source Config.1' model.

    Specifies the new destination Source configuration where the VMs will be
    recovered for vCloudDirector sources.

    Attributes:
        source (RecoveryObjectIdentifier): Specifies the id of the parent source to recover the
            VMs.
        org_vdc_network (OrgVDCNetwork): Specifies the VDC organization network which will be attached
          with recoverd VM.
        vdc (RecoveryObjectIdentifier): Specifies the VDC object where the recovered objects will
            be attached.
        v_app (RecoveryObjectIdentifier): Specifies the vApp object where the recovered objects will be
          attached.
        datastores (list of RecoveryObjectIdentifier): Specifies the datastore
            objects where the object's files should be recovered to.
        storage_profile (VcdStorageProfileParams): Specifies the storage profile to
            which the objects should be recovered. This should only be
            specified if datastores are not specified.
        network_config (NetworkConfig5): Specifies the networking
            configuration to be applied to the recovered VMs.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source":'source',
        "org_vdc_network":'orgVdcNetwork',
        "vdc":'vdc',
        "v_app":'vApp',
        "datastores":'datastores',
        "storage_profile":'storageProfile',
        "network_config":'networkConfig'
    }

    def __init__(self,
                 source=None,
                 org_vdc_network=None,
                 vdc=None,
                 v_app=None,
                 datastores=None,
                 storage_profile=None,
                 network_config=None):
        """Constructor for the RecoverVmwareVMsVcloudDirectorSourceConfig1 class"""

        # Initialize members of the class
        self.source = source
        self.org_vdc_network = org_vdc_network
        self.vdc = vdc
        self.v_app = v_app
        self.datastores = datastores
        self.storage_profile = storage_profile
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
        org_vdc_network = cohesity_management_sdk.models_v2.org_vdc_network.OrgVDCNetwork.from_dictionary(dictionary.get('orgVdcNetwork')) if dictionary.get('orgVdcNetwork') else None
        vdc = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(dictionary.get('vdc')) if dictionary.get('vdc') else None
        v_app = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(dictionary.get('vApp')) if dictionary.get('vApp') else None
        datastores = None
        if dictionary.get("datastores") is not None:
            datastores = list()
            for structure in dictionary.get('datastores'):
                datastores.append(cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(structure))
        storage_profile = cohesity_management_sdk.models_v2.vcd_storage_profile_params.VCDStorageProfileParams.from_dictionary(dictionary.get('storageProfile')) if dictionary.get('storageProfile') else None
        network_config = cohesity_management_sdk.models_v2.network_config_5.NetworkConfig5.from_dictionary(dictionary.get('networkConfig')) if dictionary.get('networkConfig') else None

        # Return an object of this model
        return cls(source,
                   org_vdc_network,
                   vdc,
                   v_app,
                   datastores,
                   storage_profile,
                   network_config)