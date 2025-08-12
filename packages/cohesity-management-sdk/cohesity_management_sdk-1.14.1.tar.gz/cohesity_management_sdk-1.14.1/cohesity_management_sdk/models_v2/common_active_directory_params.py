# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.machine_account
import cohesity_management_sdk.models_v2.domain_controller
import cohesity_management_sdk.models_v2.trusted_domain_params_2

class CommonActiveDirectoryParams(object):

    """Implementation of the 'CommonActiveDirectoryParams' model.

    Specifies the params of Active Directory which are used across creating
    and updating.

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
        "nis_provider_domain_name":'nisProviderDomainName'
    }

    def __init__(self,
                 machine_accounts=None,
                 id=None,
                 organizational_unit_name=None,
                 work_group_name=None,
                 preferred_domain_controllers=None,
                 ldap_provider_id=None,
                 trusted_domain_params=None,
                 nis_provider_domain_name=None):
        """Constructor for the CommonActiveDirectoryParams class"""

        # Initialize members of the class
        self.machine_accounts = machine_accounts
        self.id = id
        self.organizational_unit_name = organizational_unit_name
        self.work_group_name = work_group_name
        self.preferred_domain_controllers = preferred_domain_controllers
        self.ldap_provider_id = ldap_provider_id
        self.trusted_domain_params = trusted_domain_params
        self.nis_provider_domain_name = nis_provider_domain_name


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

        # Return an object of this model
        return cls(machine_accounts,
                   id,
                   organizational_unit_name,
                   work_group_name,
                   preferred_domain_controllers,
                   ldap_provider_id,
                   trusted_domain_params,
                   nis_provider_domain_name)


