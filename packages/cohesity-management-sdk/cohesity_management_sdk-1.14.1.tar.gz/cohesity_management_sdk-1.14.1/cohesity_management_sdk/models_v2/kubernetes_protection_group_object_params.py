# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.kubernetes_pvc_info

class KubernetesProtectionGroupObjectParams(object):

    """Implementation of the 'Kubernetes ProtectionGroup Object Params' model.

    Specifies the object parameters to create Kubernetes Protection Group.

    Attributes:
        exclude_pvcs (list of KubernetesPvcInfo): Specifies a list of pvcs to exclude from being protected. This
          is only applicable to kubernetes.
        id (long|int): Specifies the id of the object.
        include_pvcs (list of KubernetesPvcInfo): Specifies a list of Pvcs to include in the protection. This is
          only applicable to kubernetes.
        name (string): Specifies the name of the object.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "exclude_pvcs":'excludePvcs',
        "include_pvcs":'includePvcs',
        "id":'id',
        "name":'name'
    }

    def __init__(self,
                 exclude_pvcs=None,
                 include_pvcs=None,
                 id=None,
                 name=None):
        """Constructor for the KubernetesProtectionGroupObjectParams class"""

        # Initialize members of the class
        self.exclude_pvcs = exclude_pvcs
        self.include_pvcs = include_pvcs
        self.id = id
        self.name = name


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
        exclude_pvcs = None
        if dictionary.get("excludePvcs") is not None:
            exclude_pvcs = list()
            for structure in dictionary.get('excludePvcs'):
                exclude_pvcs.append(cohesity_management_sdk.models_v2.kubernetes_pvc_info.KubernetesPvcInfo.from_dictionary(structure))
        include_pvcs = None
        if dictionary.get("includePvcs") is not None:
            include_pvcs = list()
            for structure in dictionary.get('includePvcs'):
                include_pvcs.append(cohesity_management_sdk.models_v2.kubernetes_pvc_info.KubernetesPvcInfo.from_dictionary(structure))
        id = dictionary.get('id')
        name = dictionary.get('name')

        # Return an object of this model
        return cls(exclude_pvcs,
                   include_pvcs,
                    id,
                   name)