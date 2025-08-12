# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.qo_s

class QosPoliciesResult(object):

    """Implementation of the 'QosPoliciesResult.' model.

    Specifies the list of QoS policies.

    Attributes:
        qos_policies (list of QoS): Specifies the list of QoS policies.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "qos_policies":'qosPolicies'
    }

    def __init__(self,
                 qos_policies=None):
        """Constructor for the QosPoliciesResult class"""

        # Initialize members of the class
        self.qos_policies = qos_policies


    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the qos_policies as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.

        Returns:
            qos_policies: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary
        qos_policies = None
        if dictionary.get("qosPolicies") is not None:
            qos_policies = list()
            for structure in dictionary.get('qosPolicies'):
                qos_policies.append(cohesity_management_sdk.models_v2.qo_s.QoS.from_dictionary(structure))

        # Return an qos_policies of this model
        return cls(qos_policies)
