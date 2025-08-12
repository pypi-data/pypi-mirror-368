# -*- coding: utf-8 -*-


class QOSPolicyType(object):

    """Implementation of the 'QOS Policy type.' model.

    QOS Policy type.

    Attributes:
        qos_policy (QosPolicy3Enum): Specifies QOS Policy type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "qos_policy":'qosPolicy'
    }

    def __init__(self,
                 qos_policy=None):
        """Constructor for the QOSPolicyType class"""

        # Initialize members of the class
        self.qos_policy = qos_policy


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
        qos_policy = dictionary.get('qosPolicy')

        # Return an object of this model
        return cls(qos_policy)


