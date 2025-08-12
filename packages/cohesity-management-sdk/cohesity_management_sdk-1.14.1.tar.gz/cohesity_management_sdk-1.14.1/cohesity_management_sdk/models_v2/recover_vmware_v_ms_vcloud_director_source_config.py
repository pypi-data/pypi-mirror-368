# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.source
import cohesity_management_sdk.models_v2.vdc
import cohesity_management_sdk.models_v2.v_app
import cohesity_management_sdk.models_v2.recovery_object_identifier
import cohesity_management_sdk.models_v2.storage_profile
import cohesity_management_sdk.models_v2.network_config_5

class RecoverVmwareVMsVcloudDirectorSourceConfig(object):

    """Implementation of the 'Recover VMware VMs vCloudDirector Source Config.' model.

    Specifies the new destination Source configuration where the VMs will be
    recovered for vCloudDirector sources.

    Attributes:
        source (Source): Specifies the id of the parent source to recover the
            VMs.
        vdc (Vdc): Specifies the VDC object where the recovered objects will
            be attached.
        v_app (VApp): Specifies the vApp object where the recovered objects
            will be attached.
        datastores (list of RecoveryObjectIdentifier): Specifies the datastore
            objects where the object's files should be recovered to. This
            should only be specified if storageProfile is not specified.
        storage_profile (StorageProfile): Specifies the storage profile to
            which the objects should be recovered. This should only be
            specified if datastores are not specified.
        network_config (NetworkConfig5): Specifies the networking
            configuration to be applied to the recovered VMs.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source":'source',
        "vdc":'vdc',
        "v_app":'vApp',
        "datastores":'datastores',
        "storage_profile":'storageProfile',
        "network_config":'networkConfig'
    }

    def __init__(self,
                 source=None,
                 vdc=None,
                 v_app=None,
                 datastores=None,
                 storage_profile=None,
                 network_config=None):
        """Constructor for the RecoverVmwareVMsVcloudDirectorSourceConfig class"""

        # Initialize members of the class
        self.source = source
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
        source = cohesity_management_sdk.models_v2.source.Source.from_dictionary(dictionary.get('source')) if dictionary.get('source') else None
        vdc = cohesity_management_sdk.models_v2.vdc.Vdc.from_dictionary(dictionary.get('vdc')) if dictionary.get('vdc') else None
        v_app = cohesity_management_sdk.models_v2.v_app.VApp.from_dictionary(dictionary.get('vApp')) if dictionary.get('vApp') else None
        datastores = None
        if dictionary.get("datastores") is not None:
            datastores = list()
            for structure in dictionary.get('datastores'):
                datastores.append(cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(structure))
        storage_profile = cohesity_management_sdk.models_v2.storage_profile.StorageProfile.from_dictionary(dictionary.get('storageProfile')) if dictionary.get('storageProfile') else None
        network_config = cohesity_management_sdk.models_v2.network_config_5.NetworkConfig5.from_dictionary(dictionary.get('networkConfig')) if dictionary.get('networkConfig') else None

        # Return an object of this model
        return cls(source,
                   vdc,
                   v_app,
                   datastores,
                   storage_profile,
                   network_config)


