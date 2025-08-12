# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class IPMode(object):

    """Implementation of the 'IPMode' model.

    Attributes:
        ip_family_policy (int): IP family policy in use.
        preferred_ip_family (int): IP family preferred (in case of dual stack)
            or in use (for single stack).

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "ip_family_policy": 'ipFamilyPolicy',
        "preferred_ip_family": 'preferredIpFamily'
    }

    def __init__(self,
                 ip_family_policy=None,
                 preferred_ip_family=None):
        """Constructor for the IPMode class"""

        # Initialize members of the class
        self.ip_family_policy = ip_family_policy
        self.preferred_ip_family = preferred_ip_family


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
        ip_family_policy = dictionary.get('ipFamilyPolicy', None)
        preferred_ip_family = dictionary.get('preferredIpFamily', None)

        # Return an object of this model
        return cls(ip_family_policy,
                   preferred_ip_family)


