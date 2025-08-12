# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.kubernetes_vlan_info
import cohesity_management_sdk.models.vlan_parameters
import cohesity_management_sdk.models.vlan_info_service_annotations_entry

import cohesity_management_sdk.models.kubernetes_vlan_info
import cohesity_management_sdk.models.vlan_parameters
import cohesity_management_sdk.models.vlan_info_service_annotations_entry

class KubernetesParams(object):

    """Implementation of the 'KubernetesParams' model.

    Specifies the parameters required to register Application Servers running
    in a Protection Source.

    Attributes:
        datamover_image_location (string): Specifies the location of Datamover
            image in private registry.
        datamover_service_type (int): Specifies Type of service to be deployed
            for communication with DataMover pods.
            Currently, LoadBalancer and NodePort are supported.
            [default = kNodePort].'
        default_vlan_params (VlanParameters): Specifies the default VLAN
            parameters to be used for performing the
            backup/restore of this entity.
        init_container_image_location (string): Specifies the location of the
            image for init containers.
        kubernetes_distribution (KubernetesDistributionEnum): Specifies the
            distribution if the environment is kKubernetes.
            overrideDescription: true
        san_field (list of string): Specifies the SAN field for agent certificate
        service_annotations (list of VlanInfo_ServiceAnnotationsEntry):
            Specifies annotations to be put on services for IP allocation.
            Applicable only when service is of type LoadBalancer.
        velero_aws_plugin_image_location (string): Specifies the location of
            Velero AWS plugin image in private registry.
        velero_image_location (string): Specifies the location of Velero image
            in private registry.
        velero_openshift_plugin_image_location (string):  Specifies the
            location of the image for openshift plugin container.
        vlan_info_vec (list of KubernetesVlanInfo): Specifies VLAN information
            provided during registration.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "datamover_image_location":'datamoverImageLocation',
        "datamover_service_type": 'datamoverServiceType',
        "default_vlan_params": 'defaultVlanParams',
        "init_container_image_location":'initContainerImageLocation',
        "kubernetes_distribution":'kubernetesDistribution',
        "san_field":'sanField',
        "service_annotations": 'serviceAnnotations',
        "velero_aws_plugin_image_location":'veleroAwsPluginImageLocation',
        "velero_image_location":'veleroImageLocation',
        "velero_openshift_plugin_image_location":'veleroOpenshiftPluginImageLocation',
        "vlan_info_vec": 'vlanInfoVec'
    }

    def __init__(self,
                 datamover_image_location=None,
                 datamover_service_type=None,
                 default_vlan_params=None,
                 init_container_image_location=None,
                 kubernetes_distribution=None,
                 san_field=None,
                 service_annotations=None,
                 velero_aws_plugin_image_location=None,
                 velero_image_location=None,
                 velero_openshift_plugin_image_location=None,
                 vlan_info_vec=None):
        """Constructor for the KubernetesParams class"""

        # Initialize members of the class
        self.datamover_image_location = datamover_image_location
        self.datamover_service_type = datamover_service_type
        self.default_vlan_params = default_vlan_params
        self.init_container_image_location = init_container_image_location
        self.kubernetes_distribution = kubernetes_distribution
        self.san_field = san_field
        self.service_annotations = service_annotations
        self.velero_aws_plugin_image_location = velero_aws_plugin_image_location
        self.velero_image_location = velero_image_location
        self.velero_openshift_plugin_image_location = velero_openshift_plugin_image_location
        self.vlan_info_vec = vlan_info_vec


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
        datamover_image_location = dictionary.get('datamoverImageLocation')
        default_vlan_params = cohesity_management_sdk.models.vlan_parameters.VlanParameters.from_dictionary(dictionary.get('defaultVlanParams')) if dictionary.get('defaultVlanParams') else None
        datamover_service_type = dictionary.get('datamoverServiceType')
        init_container_image_location = dictionary.get('initContainerImageLocation')
        kubernetes_distribution = dictionary.get('kubernetesDistribution')
        san_field = dictionary.get('sanField')
        service_annotations = None
        if dictionary.get("serviceAnnotations") is not None:
            service_annotations = list()
            for structure in dictionary.get('serviceAnnotations'):
                service_annotations.append(cohesity_management_sdk.models.vlan_info_service_annotations_entry.VlanInfo_ServiceAnnotationsEntry.from_dictionary(structure))
        velero_aws_plugin_image_location = dictionary.get('veleroAwsPluginImageLocation')
        velero_image_location = dictionary.get('veleroImageLocation')
        velero_openshift_plugin_image_location = dictionary.get('veleroOpenshiftPluginImageLocation')
        vlan_info_vec = None
        if dictionary.get("vlanInfoVec") is not None:
            vlan_info_vec = list()
            for structure in dictionary.get('vlanInfoVec'):
                vlan_info_vec.append(cohesity_management_sdk.models.kubernetes_vlan_info.KubernetesVlanInfo.from_dictionary(structure))
        

        # Return an object of this model
        return cls(datamover_image_location,
                   datamover_service_type,
                   default_vlan_params,
                   init_container_image_location,
                   kubernetes_distribution,
                   san_field,
                   service_annotations,
                   velero_aws_plugin_image_location,
                   velero_image_location,
                   velero_openshift_plugin_image_location,
                   vlan_info_vec)