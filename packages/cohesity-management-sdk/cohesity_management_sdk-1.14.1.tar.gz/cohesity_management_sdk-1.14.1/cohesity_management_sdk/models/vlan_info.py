# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


import cohesity_management_sdk.models.vlan_info_service_annotations_entry
import cohesity_management_sdk.models.vlan_params

class VlanInfo(object):

    """Implementation of the 'VlanInfo' model.

    Attributes:
        service_annotations (list of VlanInfo_ServiceAnnotationsEntry):
            Contains annotations to be put on services for IP allocation.
            Applicable only when service is of type LoadBalancer.
        vlan_params (VlanParams):  Contains the VLAN parameters.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "service_annotations": 'serviceAnnotations',
        "vlan_params": 'vlanParams'
    }

    def __init__(self,
                 service_annotations=None,
                 vlan_params=None):
        """Constructor for the VlanInfo class"""

        # Initialize members of the class
        self.service_annotations = service_annotations
        self.vlan_params = vlan_params


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
        service_annotations = None
        if dictionary.get("serviceAnnotations", None) is not None:
            service_annotations = list()
            for structure in dictionary.get('serviceAnnotations'):
                service_annotations.append(cohesity_management_sdk.models.vlan_info_service_annotations_entry.VlanInfo_ServiceAnnotationsEntry.from_dictionary(structure))
        vlan_params = cohesity_management_sdk.models.vlan_params.VlanParams.from_dictionary(dictionary.get('vlanParams', None)) if dictionary.get('vlanParams', None) else None

        # Return an object of this model
        return cls(service_annotations,
                   vlan_params)


