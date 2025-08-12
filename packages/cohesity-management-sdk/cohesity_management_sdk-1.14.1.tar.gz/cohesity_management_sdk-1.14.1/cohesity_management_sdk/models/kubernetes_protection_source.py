# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.kubernetes_label_attribute
import cohesity_management_sdk.models.kubernetes_vlan_info
import cohesity_management_sdk.models.vlan_parameters
import cohesity_management_sdk.models.vlan_info_service_annotations_entry

class KubernetesProtectionSource(object):

    """Implementation of the 'KubernetesProtectionSource' model.

    Specifies a Protection Source in Kubernetes environment.

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
        datamover_upgradability (int): Specifies if the deployed Datamover
            image needs to be upgraded for this kubernetes entity
        description (string): Specifies an optional description of the
            object.
        distribution (DistributionEnum): Specifies the type of the entity in a
            Kubernetes environment.
            Determines the K8s distribution.
        init_container_image_location (string): Specifies the location of the
            image for init containers.
        label_attributes (list of KubernetesLabelAttribute): Specifies the list
            of label attributes of this source.
        name (string): Specifies a unique name of the Protection Source.
        san_field (list of string): Specifies the SAN field for agent certificate
        service_annotations (list of VlanInfo_ServiceAnnotationsEntry):
            Specifies annotations to be put on services for IP allocation.
            Applicable only when service is of type LoadBalancer.
        mtype (TypeKubernetesProtectionSourceEnum): Specifies the type of the
            entity in a Kubernetes environment. Specifies the type of a
            Kubernetes Protection Source. 'kCluster' indicates a Kubernetes
            Cluster. 'kNamespace' indicates a namespace in a Kubernetes
            Cluster. 'kService' indicates a service running on a Kubernetes
            Cluster.
        uuid (string): Specifies the UUID of the object.
        velero_aws_plugin_image_location (string): Specifies the location of
            Velero AWS plugin image in private registry.
        velero_image_location (string): Specifies the location of Velero image
            in private registry.
        velero_openshift_plugin_image_location (string):  Specifies the
            location of the image for openshift plugin container.
        velero_upgradability (string): Specifies if the deployed Velero image
            needs to be upgraded for this kubernetes entity.
        vlan_info_vec (list of KubernetesVlanInfo): Specifies VLAN information
            provided during registration.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "datamover_image_location": 'datamoverImageLocation',
        "datamover_service_type": 'datamoverServiceType',
        "datamover_upgradability":'datamoverUpgradability',
        "default_vlan_params": 'defaultVlanParams',
        "description":'description',
        "distribution":'distribution',
        "init_container_image_location":'initContainerImageLocation',
        "label_attributes":'labelAttributes',
        "name":'name',
        "san_field":'sanField',
        "service_annotations": 'serviceAnnotations',
        "mtype":'type',
        "uuid":'uuid',
        "velero_aws_plugin_image_location":'veleroAwsPluginImageLocation',
        "velero_image_location":'veleroImageLocation',
        "velero_openshift_plugin_image_location":'veleroOpenshiftPluginImageLocation',
        "velero_upgradability":'veleroUpgradability',
        "vlan_info_vec": 'vlanInfoVec'
    }

    def __init__(self,
                 datamover_image_location=None,
                 datamover_service_type=None,
                 datamover_upgradability=None,
                 default_vlan_params=None,
                 description=None,
                 distribution=None,
                 init_container_image_location=None,
                 label_attributes=None,
                 name=None,
                 san_field=None,
                 service_annotations=None,
                 mtype=None,
                 uuid=None,
                 velero_aws_plugin_image_location=None,
                 velero_image_location=None,
                 velero_openshift_plugin_image_location=None,
                 velero_upgradability=None,
                 vlan_info_vec=None):
        """Constructor for the KubernetesProtectionSource class"""

        # Initialize members of the class
        self.datamover_image_location = datamover_image_location
        self.datamover_service_type = datamover_service_type
        self.datamover_upgradability = datamover_upgradability
        self.default_vlan_params = default_vlan_params
        self.description = description
        self.distribution = distribution
        self.init_container_image_location = init_container_image_location
        self.label_attributes = label_attributes
        self.name = name
        self.san_field = san_field
        self.service_annotations =service_annotations
        self.mtype = mtype
        self.uuid = uuid
        self.velero_aws_plugin_image_location = velero_aws_plugin_image_location
        self.velero_image_location = velero_image_location
        self.velero_openshift_plugin_image_location = velero_openshift_plugin_image_location
        self.velero_upgradability = velero_upgradability
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
        datamover_service_type = dictionary.get('datamoverServiceType')
        datamover_upgradability = dictionary.get('datamoverUpgradability')
        default_vlan_params = cohesity_management_sdk.models.vlan_parameters.VlanParameters.from_dictionary(dictionary.get('defaultVlanParams')) if dictionary.get('defaultVlanParams') else None
        description = dictionary.get('description')
        distribution = dictionary.get('distribution')
        init_container_image_location = dictionary.get('initContainerImageLocation')
        label_attributes = None
        if dictionary.get("labelAttributes") is not None:
            label_attributes = list()
            for structure in dictionary.get('labelAttributes'):
                label_attributes.append(cohesity_management_sdk.models.kubernetes_label_attribute.KubernetesLabelAttribute.from_dictionary(structure))
        name = dictionary.get('name')
        san_field = dictionary.get('sanField')
        service_annotations = None
        if dictionary.get("serviceAnnotations") is not None:
            service_annotations = list()
            for structure in dictionary.get('serviceAnnotations'):
                service_annotations.append(cohesity_management_sdk.models.vlan_info_service_annotations_entry.VlanInfo_ServiceAnnotationsEntry.from_dictionary(structure))
        mtype = dictionary.get('type')
        uuid = dictionary.get('uuid')
        velero_aws_plugin_image_location = dictionary.get('veleroAwsPluginImageLocation')
        velero_image_location = dictionary.get('veleroImageLocation')
        velero_openshift_plugin_image_location = dictionary.get('veleroOpenshiftPluginImageLocation')
        velero_upgradability = dictionary.get('veleroUpgradability')
        vlan_info_vec = None
        if dictionary.get("vlanInfoVec") is not None:
            vlan_info_vec = list()
            for structure in dictionary.get('vlanInfoVec'):
                vlan_info_vec.append(cohesity_management_sdk.models.kubernetes_vlan_info.KubernetesVlanInfo.from_dictionary(structure))

        # Return an object of this model
        return cls(datamover_image_location,
                   datamover_service_type,
                   datamover_upgradability,
                   default_vlan_params,
                   description,
                   distribution,
                   init_container_image_location,
                   label_attributes,
                   name,
                   san_field,
                   service_annotations,
                   mtype,
                   uuid,
                   velero_aws_plugin_image_location,
                   velero_image_location,
                   velero_openshift_plugin_image_location,
                   velero_upgradability,
                   vlan_info_vec)