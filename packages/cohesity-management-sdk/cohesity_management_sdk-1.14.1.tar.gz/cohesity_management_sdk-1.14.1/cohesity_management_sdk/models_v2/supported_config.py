# -*- coding: utf-8 -*-


class SupportedConfig(object):

    """Implementation of the 'SupportedConfig' model.

    TODO: type description here.

    Attributes:
        min_nodes_allowed (long|int): Specifies the minimum number of Nodes
           supported for this Cluster type.
        supported_erasure_coding (list of string): Array of Supported Erasure Coding Options.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "min_nodes_allowed":'minNodesAllowed',
        "supported_erasure_coding":'supportedErasureCoding'
    }

    def __init__(self,
                 min_nodes_allowed=None,
                 supported_erasure_coding=None):
        """Constructor for the SupportedConfig class"""

        # Initialize members of the class
        self.min_nodes_allowed = min_nodes_allowed
        self.supported_erasure_coding = supported_erasure_coding


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
        min_nodes_allowed = dictionary.get('minNodesAllowed')
        supported_erasure_coding = dictionary.get('supportedErasureCoding')

        # Return an object of this model
        return cls(min_nodes_allowed,
                   supported_erasure_coding)