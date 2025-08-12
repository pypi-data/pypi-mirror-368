# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.kubernetes_label

class KubernetesFilterParams(object):

    """Implementation of the 'KubernetesFilterParams' model.

    Specifies the parameters for recovering a Kubernetes namespace to a
    Kubernetes source.

    Attributes:
        label_combination_method (LabelCombinationMethodEnum): Specifies the
            objects to be recovered.
        label_vector (list of KubernetesLabel):
            Array of Object to represent Label that Specify Objects (e.g.:
          Persistent Volumes and Persistent Volume Claims) to Include or Exclude.It
          will be a two-dimensional array, where each inner array will consist of
          a key and value representing labels. Using this two dimensional array of
          Labels, the Cluster generates a list of items to include in the filter,
          which are derived from intersections or the union of these labels, as decided
          by operation parameter.
        objects (list of long|int): Array of objects that are to be included.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "label_combination_method":'labelCombinationMethod',
        "label_vector":'labelVector',
        "objects":'objects'
    }

    def __init__(self,
                 label_combination_method=None,
                 label_vector=None,
                 objects=None):
        """Constructor for the KubernetesFilterParams class"""

        # Initialize members of the class
        self.label_combination_method = label_combination_method
        self.label_vector = label_vector
        self.objects = objects


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
        label_combination_method = dictionary.get('labelCombinationMethod')
        label_vector = None
        if dictionary.get("labelVector") is not None:
            label_vector = list()
            for structure in dictionary.get('labelVector'):
                label_vector.append(cohesity_management_sdk.models_v2.kubernetes_label.KubernetesLabel.from_dictionary(structure))
        objects = dictionary.get('objects')

        # Return an object of this model
        return cls(label_combination_method,
                   label_vector,
                   objects)