# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.machine_account
import cohesity_management_sdk.models_v2.domain_controller
import cohesity_management_sdk.models_v2.trusted_domain_params_2
import cohesity_management_sdk.models_v2.id_mapping_params
import cohesity_management_sdk.models_v2.centrify_zones
import cohesity_management_sdk.models_v2.domain_controllers
import cohesity_management_sdk.models_v2.security_principal
import cohesity_management_sdk.models_v2.tenant

class ActiveDirectory(object):

    """Implementation of the 'ActiveDirectory' model.

    Specifies an Active Directory.

    Attributes:
        machine_accounts (list of MachineAccount): Specifies a list of
            computer names used to identify the Cohesity Cluster on the Active
            Directory domain.
        id (long|int): Specifies the id of the Active Directory.
        organizational_unit_name (string): Specifies an optional
            organizational unit name.
        work_group_name (string): Specifies an optional work group name.
        preferred_domain_controllers (list of DomainController): Specifies a
            list of preferred domain controllers of this Active Directory.
        ldap_provider_id (long|int): Specifies the LDAP provider id which is
            mapped to this Active Directory
        trusted_domain_params (TrustedDomainParams2): Specifies the params of
            trusted domain info of an Active Directory.
        nis_provider_domain_name (string): Specifies the name of the NIS
            Provider which is mapped to this Active Directory.
        id_mapping_params (IdMappingParams): Specifies the params of the user
            id mapping info of an Active Directory.
        domain_name (string): Specifies the domain name of the Active
            Directory.
        centrify_zones (list of CentrifyZones): Specifies a list of centrify
            zones.
        domain_controllers (list of DomainControllers): A list of domain names
            with a list of it's domain controllers.
        security_principals (list of SecurityPrincipal): Specifies a list of
            security principals.
        permissions (list of Tenant): Specifies the list of tenants that have
            permissions for this Active Directory.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "machine_accounts":'machineAccounts',
        "id":'id',
        "organizational_unit_name":'organizationalUnitName',
        "work_group_name":'workGroupName',
        "preferred_domain_controllers":'preferredDomainControllers',
        "ldap_provider_id":'ldapProviderId',
        "trusted_domain_params":'trustedDomainParams',
        "nis_provider_domain_name":'nisProviderDomainName',
        "id_mapping_params":'idMappingParams',
        "domain_name":'domainName',
        "centrify_zones":'centrifyZones',
        "domain_controllers":'domainControllers',
        "security_principals":'securityPrincipals',
        "permissions":'permissions'
    }

    def __init__(self,
                 machine_accounts=None,
                 id=None,
                 organizational_unit_name=None,
                 work_group_name=None,
                 preferred_domain_controllers=None,
                 ldap_provider_id=None,
                 trusted_domain_params=None,
                 nis_provider_domain_name=None,
                 id_mapping_params=None,
                 domain_name=None,
                 centrify_zones=None,
                 domain_controllers=None,
                 security_principals=None,
                 permissions=None):
        """Constructor for the ActiveDirectory class"""

        # Initialize members of the class
        self.machine_accounts = machine_accounts
        self.id = id
        self.organizational_unit_name = organizational_unit_name
        self.work_group_name = work_group_name
        self.preferred_domain_controllers = preferred_domain_controllers
        self.ldap_provider_id = ldap_provider_id
        self.trusted_domain_params = trusted_domain_params
        self.nis_provider_domain_name = nis_provider_domain_name
        self.id_mapping_params = id_mapping_params
        self.domain_name = domain_name
        self.centrify_zones = centrify_zones
        self.domain_controllers = domain_controllers
        self.security_principals = security_principals
        self.permissions = permissions


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
        machine_accounts = None
        if dictionary.get("machineAccounts") is not None:
            machine_accounts = list()
            for structure in dictionary.get('machineAccounts'):
                machine_accounts.append(cohesity_management_sdk.models_v2.machine_account.MachineAccount.from_dictionary(structure))
        id = dictionary.get('id')
        organizational_unit_name = dictionary.get('organizationalUnitName')
        work_group_name = dictionary.get('workGroupName')
        preferred_domain_controllers = None
        if dictionary.get("preferredDomainControllers") is not None:
            preferred_domain_controllers = list()
            for structure in dictionary.get('preferredDomainControllers'):
                preferred_domain_controllers.append(cohesity_management_sdk.models_v2.domain_controller.DomainController.from_dictionary(structure))
        ldap_provider_id = dictionary.get('ldapProviderId')
        trusted_domain_params = cohesity_management_sdk.models_v2.trusted_domain_params_2.TrustedDomainParams2.from_dictionary(dictionary.get('trustedDomainParams')) if dictionary.get('trustedDomainParams') else None
        nis_provider_domain_name = dictionary.get('nisProviderDomainName')
        id_mapping_params = cohesity_management_sdk.models_v2.id_mapping_params.IdMappingParams.from_dictionary(dictionary.get('idMappingParams')) if dictionary.get('idMappingParams') else None
        domain_name = dictionary.get('domainName')
        centrify_zones = None
        if dictionary.get("centrifyZones") is not None:
            centrify_zones = list()
            for structure in dictionary.get('centrifyZones'):
                centrify_zones.append(cohesity_management_sdk.models_v2.centrify_zones.CentrifyZones.from_dictionary(structure))
        domain_controllers = None
        if dictionary.get("domainControllers") is not None:
            domain_controllers = list()
            for structure in dictionary.get('domainControllers'):
                domain_controllers.append(cohesity_management_sdk.models_v2.domain_controllers.DomainControllers.from_dictionary(structure))
        security_principals = None
        if dictionary.get("securityPrincipals") is not None:
            security_principals = list()
            for structure in dictionary.get('securityPrincipals'):
                security_principals.append(cohesity_management_sdk.models_v2.security_principal.SecurityPrincipal.from_dictionary(structure))
        permissions = None
        if dictionary.get("permissions") is not None:
            permissions = list()
            for structure in dictionary.get('permissions'):
                permissions.append(cohesity_management_sdk.models_v2.tenant.Tenant.from_dictionary(structure))

        # Return an object of this model
        return cls(machine_accounts,
                   id,
                   organizational_unit_name,
                   work_group_name,
                   preferred_domain_controllers,
                   ldap_provider_id,
                   trusted_domain_params,
                   nis_provider_domain_name,
                   id_mapping_params,
                   domain_name,
                   centrify_zones,
                   domain_controllers,
                   security_principals,
                   permissions)


