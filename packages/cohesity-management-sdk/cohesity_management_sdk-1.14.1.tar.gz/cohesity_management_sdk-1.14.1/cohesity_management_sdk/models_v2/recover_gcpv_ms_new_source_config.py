# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.source
import cohesity_management_sdk.models_v2.project
import cohesity_management_sdk.models_v2.region_2
import cohesity_management_sdk.models_v2.availability_zone_1
import cohesity_management_sdk.models_v2.network_config_12

class RecoverGCPVMsNewSourceConfig(object):

    """Implementation of the 'Recover GCP VMs New Source Config.' model.

    Specifies the new destination Source configuration where the VMs will be
    recovered.

    Attributes:
        source (Source): Specifies the id of the parent source to recover the
            VMs.
        project (Project): Specifies the GCP project in which to deploy the
            VM.
        region (Region2): Specifies the GCP region in which to deploy the VM.
        availability_zone (AvailabilityZone1): Specifies the GCP zone in which
            to deploy the VM.
        network_config (NetworkConfig12): Specifies the networking
            configuration to be applied to the recovered VMs.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source":'source',
        "project":'project',
        "region":'region',
        "availability_zone":'availabilityZone',
        "network_config":'networkConfig'
    }

    def __init__(self,
                 source=None,
                 project=None,
                 region=None,
                 availability_zone=None,
                 network_config=None):
        """Constructor for the RecoverGCPVMsNewSourceConfig class"""

        # Initialize members of the class
        self.source = source
        self.project = project
        self.region = region
        self.availability_zone = availability_zone
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
        project = cohesity_management_sdk.models_v2.project.Project.from_dictionary(dictionary.get('project')) if dictionary.get('project') else None
        region = cohesity_management_sdk.models_v2.region_2.Region2.from_dictionary(dictionary.get('region')) if dictionary.get('region') else None
        availability_zone = cohesity_management_sdk.models_v2.availability_zone_1.AvailabilityZone1.from_dictionary(dictionary.get('availabilityZone')) if dictionary.get('availabilityZone') else None
        network_config = cohesity_management_sdk.models_v2.network_config_12.NetworkConfig12.from_dictionary(dictionary.get('networkConfig')) if dictionary.get('networkConfig') else None

        # Return an object of this model
        return cls(source,
                   project,
                   region,
                   availability_zone,
                   network_config)


