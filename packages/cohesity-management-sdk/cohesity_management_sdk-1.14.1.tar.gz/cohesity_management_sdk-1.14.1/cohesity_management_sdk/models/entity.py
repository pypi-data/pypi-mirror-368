# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.entity_services_to_connector_ids_map_entry
import cohesity_management_sdk.models.label_attributes_info
import cohesity_management_sdk.models.vlan_params
import cohesity_management_sdk.models.vlan_info
import cohesity_management_sdk.models.ip_mode
import cohesity_management_sdk.models.entity_service_annotations_entry
import cohesity_management_sdk.models.entity_storage_class_info
import cohesity_management_sdk.models.pod_info_pod_spec_toleration


class Entity(object):

    """Implementation of the 'Entity' model.

    Message encapsulating a Kubernetes entity


    Attributes:

        datamover_agent_version (string): Software version of the agent running
            in the DataMover pod.
        datamover_image_location (string): Location of the datamover image
            specified by the user.
        datamover_service_type (int): Type of service to be deployed for
            communication with DataMover pods.
            Currently, LoadBalancer and NodePort are supported.
        datamover_upgradability (int): Indicates if deployed datamover needs to
            be upgraded for this kubernetes entity.
        default_vlan_params (VlanParams): VLAN information of the default VLAN
        description (string): This is a general description that could be set
            for some entities.
        distribution (int): K8s distribution. This will only be applicable to
            kCluster entities.
        hosts (list of string): List of hosts to be populated as SAN fields in the agent certificate.
        init_container_image_location (string): Location of the init container
            image specified by the user.
        ip_mode (IPMode): IP mode of the kubernetes source.
        label_attributes_vec (list of LabelAttributesInfo): Label attributes
            vector contains info about the label nodes corresponding to the
            current entity's labels. TODO(jhwang): Make it applicable to
            non-kNamespace type entities also.
        label_vec (list of string): List of labels associated with this entity
            in the form "key:value". Currently, only populated for PVCs to be
            used for label based include/exclude filters.
        name (string): A human readable name for the object.
        namespace (string): Namespace of object, if applicable. For a PV, this
            field stores the namespace of the PVC which is bound to the PV.
        pvc_name (string): Name of the PVC which is bound to the PV. Applicable
            only to 'kPersistentVolume' type entity.
        service_annotations (list of Entity_ServiceAnnotationsEntry): Contains generic
            annotations to be put on services.
        services_to_connector_ids_map (list of
            Entity_ServicesToConnectorIdsMapEntry): A mapping from datamover
            services to corresponding unique connector_params IDs. This will be
            generated during registration and updated during refresh.
            Applicable only for 'kCluster' type entities.
        storage_class_vec (list of Entity_StorageClassInfo): This is populated
            for the root entity only (type kCluster).
        tolerations_vec (list of PodInfo_PodSpec_Toleration):  Custom toleration
            for Datamover pods.
        mtype (int): The type of entity this proto refers to.
        uuid (string): The UUID of the object.
        velero_aws_plugin_image_location (string): Location of the Velero AWS
            plugin image specified by the user.
        velero_image_location (string): Location of the Velero image specified
            by the user.
        velero_openshift_plugin_image_location (string): Location of the Velero
            Openshift plugin image specified by the user.
        velero_upgradability (int): Indicates if deployed Velero image needs to
            be upgraded for this kubernetes entity.
        velero_version (string): Velero version deployed.
        version (string): Kubernetes cluster version.
        vlan_info_vec (list of VlanInfo):  VLAN information provided during
            registration.
    """


    # Create a mapping from Model property names to API property names
    _names = {
        "datamover_agent_version":'datamoverAgentVersion',
        "datamover_image_location":'datamoverImageLocation',
        "datamover_service_type": 'datamoverServiceType',
        "datamover_upgradability":'datamoverUpgradability',
        "default_vlan_params": 'defaultVlanParams',
        "description":'description',
        "distribution":'distribution',
        "hosts":'hosts',
        "init_container_image_location":'initContainerImageLocation',
        "ip_mode": 'ipMode',
        "label_attributes_vec":'labelAttributesVec',
        "label_vec": 'labelVec',
        "name":'name',
        "namespace":'namespace',
        "pvc_name":'pvcName',
        "service_annotations": 'serviceAnnotations',
        "services_to_connector_ids_map":'servicesToConnectorIdsMap',
        "storage_class_vec": 'storageClassVec',
        "tolerations_vec": 'tolerationsVec',
        "mtype":'type',
        "uuid":'uuid',
        "velero_aws_plugin_image_location":'veleroAwsPluginImageLocation',
        "velero_image_location":'veleroImageLocation',
        "velero_openshift_plugin_image_location":'veleroOpenshiftPluginImageLocation',
        "velero_upgradability":'veleroUpgradability',
        "velero_version":'veleroVersion',
        "version":'version',
        "vlan_info_vec": 'vlanInfoVec'
    }
    def __init__(self,
                 datamover_agent_version=None,
                 datamover_image_location=None,
                 datamover_service_type=None,
                 datamover_upgradability=None,
                 default_vlan_params=None,
                 description=None,
                 distribution=None,
                 hosts=None,
                 init_container_image_location=None,
                 ip_mode=None,
                 label_attributes_vec=None,
                 label_vec=None,
                 name=None,
                 namespace=None,
                 pvc_name=None,
                 service_annotations=None,
                 services_to_connector_ids_map=None,
                 storage_class_vec=None,
                 tolerations_vec=None,
                 mtype=None,
                 uuid=None,
                 velero_aws_plugin_image_location=None,
                 velero_image_location=None,
                 velero_openshift_plugin_image_location=None,
                 velero_upgradability=None,
                 velero_version=None,
                 version=None,
                 vlan_info_vec=None
            ):

        """Constructor for the Entity class"""

        # Initialize members of the class
        self.datamover_agent_version = datamover_agent_version
        self.datamover_image_location = datamover_image_location
        self.datamover_service_type = datamover_service_type
        self.datamover_upgradability = datamover_upgradability
        self.default_vlan_params = default_vlan_params
        self.description = description
        self.distribution = distribution
        self.hosts = hosts
        self.init_container_image_location = init_container_image_location
        self.ip_mode = ip_mode
        self.label_attributes_vec = label_attributes_vec
        self.label_vec = label_vec
        self.name = name
        self.namespace = namespace
        self.pvc_name = pvc_name
        self.service_annotations = service_annotations
        self.services_to_connector_ids_map = services_to_connector_ids_map
        self.storage_class_vec = storage_class_vec
        self.tolerations_vec = tolerations_vec
        self.mtype = mtype
        self.uuid = uuid
        self.velero_aws_plugin_image_location = velero_aws_plugin_image_location
        self.velero_image_location = velero_image_location
        self.velero_openshift_plugin_image_location = velero_openshift_plugin_image_location
        self.velero_upgradability = velero_upgradability
        self.velero_version = velero_version
        self.version = version
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
        datamover_agent_version = dictionary.get('datamoverAgentVersion')
        datamover_image_location = dictionary.get('datamoverImageLocation')
        datamover_service_type = dictionary.get('datamoverServiceType')
        datamover_upgradability = dictionary.get('datamoverUpgradability')
        default_vlan_params = cohesity_management_sdk.models.vlan_params.VlanParams.from_dictionary(dictionary.get('defaultVlanParams')) if dictionary.get('defaultVlanParams') else None
        description = dictionary.get('description')
        distribution = dictionary.get('distribution')
        hosts = dictionary.get('hosts')
        init_container_image_location = dictionary.get('initContainerImageLocation')
        ip_mode = cohesity_management_sdk.models.ip_mode.IPMode.from_dictionary(dictionary.get('ipMode')) if dictionary.get('ipMode') else None
        label_vec = dictionary.get('labelVec')
        label_attributes_vec = None
        if dictionary.get("labelAttributesVec") is not None:
            label_attributes_vec = list()
            for structure in dictionary.get('labelAttributesVec'):
                label_attributes_vec.append(cohesity_management_sdk.models.label_attributes_info.LabelAttributesInfo.from_dictionary(structure))
        name = dictionary.get('name')
        namespace = dictionary.get('namespace')
        pvc_name = dictionary.get('pvcName')
        service_annotations = None 
        if dictionary.get("serviceAnnotations") is not None:
            service_annotations = list()
            for structure in dictionary.get('serviceAnnotations'):
                service_annotations.append(cohesity_management_sdk.models.entity_service_annotations_entry.Entity_ServiceAnnotationsEntry.from_dictionary(structure))
        services_to_connector_ids_map = None
        if dictionary.get("servicesToConnectorIdsMap") is not None:
            services_to_connector_ids_map = list()
            for structure in dictionary.get('servicesToConnectorIdsMap'):
                services_to_connector_ids_map.append(cohesity_management_sdk.models.entity_services_to_connector_ids_map_entry.Entity_ServicesToConnectorIdsMapEntry.from_dictionary(structure))
        tolerations_vec = None
        if dictionary.get("tolerationsVec") is not None:
            tolerations_vec = list()
            for structure in dictionary.get('tolerationsVec'):
                tolerations_vec.append(cohesity_management_sdk.models.pod_info_pod_spec_toleration.PodInfo_PodSpec_Toleration.from_dictionary(structure))
        storage_class_vec = None
        if dictionary.get("storageClassVec") is not None:
            storage_class_vec = list()
            for structure in dictionary.get('storageClassVec'):
                storage_class_vec.append(cohesity_management_sdk.models.entity_storage_class_info.Entity_StorageClassInfo.from_dictionary(structure))
        mtype = dictionary.get('type')
        uuid = dictionary.get('uuid')
        velero_aws_plugin_image_location = dictionary.get('veleroAwsPluginImageLocation')
        velero_image_location = dictionary.get('veleroImageLocation')
        velero_openshift_plugin_image_location = dictionary.get('veleroOpenshiftPluginImageLocation')
        velero_upgradability = dictionary.get('veleroUpgradability')
        velero_version = dictionary.get('veleroVersion')
        version = dictionary.get('version')
        vlan_info_vec = None
        if dictionary.get("vlanInfoVec") is not None:
            vlan_info_vec = list()
            for structure in dictionary.get('vlanInfoVec'):
                vlan_info_vec.append(cohesity_management_sdk.models.vlan_info.VlanInfo.from_dictionary(structure))

        # Return an object of this model
        return cls(
            datamover_agent_version,
            datamover_image_location,
            datamover_service_type,
            datamover_upgradability,
            default_vlan_params,
            description,
            distribution,
            hosts,
            init_container_image_location,
            ip_mode,
            label_attributes_vec,
            label_vec,
            name,
            namespace,
            pvc_name,
            service_annotations,
            services_to_connector_ids_map,
            storage_class_vec,
            tolerations_vec,
            mtype,
            uuid,
            velero_aws_plugin_image_location,
            velero_image_location,
            velero_openshift_plugin_image_location,
            velero_upgradability,
            velero_version,
            version,
            vlan_info_vec
)