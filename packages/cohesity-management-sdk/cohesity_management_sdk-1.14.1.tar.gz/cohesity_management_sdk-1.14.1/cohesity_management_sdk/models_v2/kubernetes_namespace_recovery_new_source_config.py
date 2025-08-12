# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.source_16

class KubernetesNamespaceRecoveryNewSourceConfig(object):

    """Implementation of the 'Kubernetes Namespace Recovery New Source Config' model.

    Specifies the new source configuration if a Kubernetes Namespace is being
    restored to a different source than the one from which it was protected.

    Attributes:
        source (Source16): Specifies the id of the parent source to recover
            the Namespaces.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source":'source'
    }

    def __init__(self,
                 source=None):
        """Constructor for the KubernetesNamespaceRecoveryNewSourceConfig class"""

        # Initialize members of the class
        self.source = source


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
        source = cohesity_management_sdk.models_v2.source_16.Source16.from_dictionary(dictionary.get('source')) if dictionary.get('source') else None

        # Return an object of this model
        return cls(source)


