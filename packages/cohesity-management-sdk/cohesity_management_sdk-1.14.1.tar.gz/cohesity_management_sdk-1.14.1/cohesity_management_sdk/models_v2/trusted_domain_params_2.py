# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.trusted_domain

class TrustedDomainParams2(object):

    """Implementation of the 'TrustedDomainParams2' model.

    Specifies the params of trusted domain info of an Active Directory.

    Attributes:
        enabled (bool): Specifies if trusted domain discovery is enabled.
        trusted_domains (list of TrustedDomain): Specifies a list of trusted
            domains.
        blacklisted_domains (list of string): Specifies a list of domains to
            add to blacklist. These domains will be blacklisted in trusted
            domain discorvery.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "enabled":'enabled',
        "trusted_domains":'trustedDomains',
        "blacklisted_domains":'blacklistedDomains'
    }

    def __init__(self,
                 enabled=None,
                 trusted_domains=None,
                 blacklisted_domains=None):
        """Constructor for the TrustedDomainParams2 class"""

        # Initialize members of the class
        self.enabled = enabled
        self.trusted_domains = trusted_domains
        self.blacklisted_domains = blacklisted_domains


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
        enabled = dictionary.get('enabled')
        trusted_domains = None
        if dictionary.get("trustedDomains") is not None:
            trusted_domains = list()
            for structure in dictionary.get('trustedDomains'):
                trusted_domains.append(cohesity_management_sdk.models_v2.trusted_domain.TrustedDomain.from_dictionary(structure))
        blacklisted_domains = dictionary.get('blacklistedDomains')

        # Return an object of this model
        return cls(enabled,
                   trusted_domains,
                   blacklisted_domains)


