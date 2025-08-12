# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_vmware_v_app_templates_vcloud_director_source_config

class RecoverVmwareVAppTemplatesNewSourceConfig(object):

    """Implementation of the 'Recover VMware vApp Templates New Source Config.' model.

    Specifies the new destination Source configuration where the vApps
    templates will be recovered.

    Attributes:
        source_type (string): Specifies the type of VMware source to which the
            vApp templatess are being restored.
        vcloud_director_params
            (RecoverVmwareVAppTemplatesVcloudDirectorSourceConfig): Specifies
            the new destination Source configuration where the vApp Templates
            will be recovered for vCloudDirector sources.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source_type":'sourceType',
        "vcloud_director_params":'vCloudDirectorParams'
    }

    def __init__(self,
                 source_type='kvCloudDirector',
                 vcloud_director_params=None):
        """Constructor for the RecoverVmwareVAppTemplatesNewSourceConfig class"""

        # Initialize members of the class
        self.source_type = source_type
        self.vcloud_director_params = vcloud_director_params


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
        source_type = dictionary.get("sourceType") if dictionary.get("sourceType") else 'kvCloudDirector'
        vcloud_director_params = cohesity_management_sdk.models_v2.recover_vmware_v_app_templates_vcloud_director_source_config.RecoverVmwareVAppTemplatesVcloudDirectorSourceConfig.from_dictionary(dictionary.get('vCloudDirectorParams')) if dictionary.get('vCloudDirectorParams') else None

        # Return an object of this model
        return cls(source_type,
                   vcloud_director_params)


