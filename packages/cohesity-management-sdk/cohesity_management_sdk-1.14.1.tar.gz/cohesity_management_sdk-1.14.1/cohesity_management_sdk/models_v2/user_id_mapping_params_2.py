# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.rfc_2307_type_params
import cohesity_management_sdk.models_v2.sfu_30_type_params
import cohesity_management_sdk.models_v2.ldap_provider_type_params
import cohesity_management_sdk.models_v2.nis_provider_type_params
import cohesity_management_sdk.models_v2.ad_centrify_type_params
import cohesity_management_sdk.models_v2.fixed_type_params
import cohesity_management_sdk.models_v2.custom_attributes_type_params

class UserIdMappingParams2(object):

    """Implementation of the 'UserIdMappingParams2' model.

    Specifies the information about how the Unix and Windows users are mapped
    for this domain.

    Attributes:
        mtype (TypeEnum): Specifies the type of the mapping.
        rfc_2307_type_params (Rfc2307TypeParams): Specifies the params for
            Rfc2307 mapping type mapping.
        sfu_30_type_params (Sfu30TypeParams): Specifies the params for Sfu30
            mapping type mapping.
        ldap_provider_type_params (LdapProviderTypeParams): Specifies the
            params for LdapProvider mapping type mapping.
        nis_provider_type_params (NisProviderTypeParams): Specifies the params
            for NisProvider mapping type mapping.
        centrify_type_params (AdCentrifyTypeParams): Specifies the params for
            Centrify mapping type mapping.
        fixed_type_params (FixedTypeParams): Specifies the params for Fixed
            mapping type mapping.
        custom_attributes_type_params (CustomAttributesTypeParams): Specifies
            the params for CustomAttributes mapping type mapping.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "mtype":'type',
        "rfc_2307_type_params":'rfc2307TypeParams',
        "sfu_30_type_params":'sfu30TypeParams',
        "ldap_provider_type_params":'ldapProviderTypeParams',
        "nis_provider_type_params":'nisProviderTypeParams',
        "centrify_type_params":'centrifyTypeParams',
        "fixed_type_params":'fixedTypeParams',
        "custom_attributes_type_params":'customAttributesTypeParams'
    }

    def __init__(self,
                 mtype=None,
                 rfc_2307_type_params=None,
                 sfu_30_type_params=None,
                 ldap_provider_type_params=None,
                 nis_provider_type_params=None,
                 centrify_type_params=None,
                 fixed_type_params=None,
                 custom_attributes_type_params=None):
        """Constructor for the UserIdMappingParams2 class"""

        # Initialize members of the class
        self.mtype = mtype
        self.rfc_2307_type_params = rfc_2307_type_params
        self.sfu_30_type_params = sfu_30_type_params
        self.ldap_provider_type_params = ldap_provider_type_params
        self.nis_provider_type_params = nis_provider_type_params
        self.centrify_type_params = centrify_type_params
        self.fixed_type_params = fixed_type_params
        self.custom_attributes_type_params = custom_attributes_type_params


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
        mtype = dictionary.get('type')
        rfc_2307_type_params = cohesity_management_sdk.models_v2.rfc_2307_type_params.Rfc2307TypeParams.from_dictionary(dictionary.get('rfc2307TypeParams')) if dictionary.get('rfc2307TypeParams') else None
        sfu_30_type_params = cohesity_management_sdk.models_v2.sfu_30_type_params.Sfu30TypeParams.from_dictionary(dictionary.get('sfu30TypeParams')) if dictionary.get('sfu30TypeParams') else None
        ldap_provider_type_params = cohesity_management_sdk.models_v2.ldap_provider_type_params.LdapProviderTypeParams.from_dictionary(dictionary.get('ldapProviderTypeParams')) if dictionary.get('ldapProviderTypeParams') else None
        nis_provider_type_params = cohesity_management_sdk.models_v2.nis_provider_type_params.NisProviderTypeParams.from_dictionary(dictionary.get('nisProviderTypeParams')) if dictionary.get('nisProviderTypeParams') else None
        centrify_type_params = cohesity_management_sdk.models_v2.ad_centrify_type_params.AdCentrifyTypeParams.from_dictionary(dictionary.get('centrifyTypeParams')) if dictionary.get('centrifyTypeParams') else None
        fixed_type_params = cohesity_management_sdk.models_v2.fixed_type_params.FixedTypeParams.from_dictionary(dictionary.get('fixedTypeParams')) if dictionary.get('fixedTypeParams') else None
        custom_attributes_type_params = cohesity_management_sdk.models_v2.custom_attributes_type_params.CustomAttributesTypeParams.from_dictionary(dictionary.get('customAttributesTypeParams')) if dictionary.get('customAttributesTypeParams') else None

        # Return an object of this model
        return cls(mtype,
                   rfc_2307_type_params,
                   sfu_30_type_params,
                   ldap_provider_type_params,
                   nis_provider_type_params,
                   centrify_type_params,
                   fixed_type_params,
                   custom_attributes_type_params)


