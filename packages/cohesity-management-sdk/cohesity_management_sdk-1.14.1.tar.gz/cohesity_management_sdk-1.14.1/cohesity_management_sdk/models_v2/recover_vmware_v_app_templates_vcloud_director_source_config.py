# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.source_8
import cohesity_management_sdk.models_v2.vdc
import cohesity_management_sdk.models_v2.catalog
import cohesity_management_sdk.models_v2.recovery_object_identifier
import cohesity_management_sdk.models_v2.storage_profile
import cohesity_management_sdk.models_v2.network_config_11
import cohesity_management_sdk.models_v2.org_vdc_network

class RecoverVmwareVAppTemplatesVcloudDirectorSourceConfig(object):

    """Implementation of the 'Recover VMware vApp Templates vCloudDirector Source Config.' model.

    Specifies the new destination Source configuration where the vApp
    Templates will be recovered for vCloudDirector sources.

    Attributes:
        org_vdc_network (OrgVDCNetwork): Specifies the VDC organization network which will be attached
          with recoverd VM under current VApp template.
        source (Source8): Specifies the id of the parent source to recover the
            vApp templates.
        vdc (Vdc): Specifies the VDC object where the recovered objects will
            be attached.
        catalog (Catalog): Specifies the catalog where the vApp template
            should reside.
        datastores (list of RecoveryObjectIdentifier): Specifies the datastore
            objects where the object's files should be recovered to.
        storage_profile (StorageProfile): Specifies the storage profile to
            which the objects should be recovered. This should only be
            specified if datastores are not specified.
        network_config (NetworkConfig11): Specifies the networking
            configuration to be applied to the recovered vApp templates.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "org_vdc_network":'orgVdcNetwork',
        "source":'source',
        "vdc":'vdc',
        "catalog":'catalog',
        "datastores":'datastores',
        "storage_profile":'storageProfile',
        "network_config":'networkConfig'
    }

    def __init__(self,
                 org_vdc_network=None,
                 source=None,
                 vdc=None,
                 catalog=None,
                 datastores=None,
                 storage_profile=None,
                 network_config=None):
        """Constructor for the RecoverVmwareVAppTemplatesVcloudDirectorSourceConfig class"""

        # Initialize members of the class
        self.org_vdc_network = org_vdc_network
        self.source = source
        self.vdc = vdc
        self.catalog = catalog
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
        org_vdc_network = cohesity_management_sdk.models_v2.org_vdc_network.OrgVDCNetwork.from_dictionary(
            dictionary.get('orgVdcNetwork')) if dictionary.get('orgVdcNetwork') else None
        source = cohesity_management_sdk.models_v2.source_8.Source8.from_dictionary(dictionary.get('source')) if dictionary.get('source') else None
        vdc = cohesity_management_sdk.models_v2.vdc.Vdc.from_dictionary(dictionary.get('vdc')) if dictionary.get('vdc') else None
        catalog = cohesity_management_sdk.models_v2.catalog.Catalog.from_dictionary(dictionary.get('catalog')) if dictionary.get('catalog') else None
        datastores = None
        if dictionary.get("datastores") is not None:
            datastores = list()
            for structure in dictionary.get('datastores'):
                datastores.append(cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(structure))
        storage_profile = cohesity_management_sdk.models_v2.storage_profile.StorageProfile.from_dictionary(dictionary.get('storageProfile')) if dictionary.get('storageProfile') else None
        network_config = cohesity_management_sdk.models_v2.network_config_11.NetworkConfig11.from_dictionary(dictionary.get('networkConfig')) if dictionary.get('networkConfig') else None

        # Return an object of this model
        return cls(org_vdc_network,
                   source,
                   vdc,
                   catalog,
                   datastores,
                   storage_profile,
                   network_config)