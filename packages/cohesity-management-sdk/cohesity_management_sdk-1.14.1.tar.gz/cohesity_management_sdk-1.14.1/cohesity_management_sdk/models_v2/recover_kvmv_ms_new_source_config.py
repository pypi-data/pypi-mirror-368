# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.source
import cohesity_management_sdk.models_v2.cluster
import cohesity_management_sdk.models_v2.data_center
import cohesity_management_sdk.models_v2.storage_domain
import cohesity_management_sdk.models_v2.network_config_13

class RecoverKVMVMsNewSourceConfig(object):

    """Implementation of the 'Recover KVM VMs New Source Config.' model.

    Specifies the new destination Source configuration where the VMs will be
    recovered.

    Attributes:
        source (Source): Specifies the id of the parent source to recover the
            VMs.
        cluster (Cluster): Specifies the resource (KVMH host) to which the
            restored VM will be attached
        data_center (DataCenter): Specifies the datacenter where the VM's
            files should be restored to.
        storage_domain (StorageDomain): Specifies the Storage Domain where the
            VM's disk should be restored to.
        network_config (NetworkConfig13): Specifies the networking
            configuration to be applied to the recovered VMs.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source":'source',
        "cluster":'cluster',
        "data_center":'dataCenter',
        "storage_domain":'storageDomain',
        "network_config":'networkConfig'
    }

    def __init__(self,
                 source=None,
                 cluster=None,
                 data_center=None,
                 storage_domain=None,
                 network_config=None):
        """Constructor for the RecoverKVMVMsNewSourceConfig class"""

        # Initialize members of the class
        self.source = source
        self.cluster = cluster
        self.data_center = data_center
        self.storage_domain = storage_domain
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
        cluster = cohesity_management_sdk.models_v2.cluster.Cluster.from_dictionary(dictionary.get('cluster')) if dictionary.get('cluster') else None
        data_center = cohesity_management_sdk.models_v2.data_center.DataCenter.from_dictionary(dictionary.get('dataCenter')) if dictionary.get('dataCenter') else None
        storage_domain = cohesity_management_sdk.models_v2.storage_domain.StorageDomain.from_dictionary(dictionary.get('storageDomain')) if dictionary.get('storageDomain') else None
        network_config = cohesity_management_sdk.models_v2.network_config_13.NetworkConfig13.from_dictionary(dictionary.get('networkConfig')) if dictionary.get('networkConfig') else None

        # Return an object of this model
        return cls(source,
                   cluster,
                   data_center,
                   storage_domain,
                   network_config)


