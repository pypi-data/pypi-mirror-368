# -*- coding: utf-8 -*-


class RegisterOrUpdateKerberosProviderRequest(object):

    """Implementation of the 'RegisterOrUpdateKerberosProviderRequest' model.

    Specifies the request to register or update a Kerberos
    Provider.

    Attributes:
        id (string): Specifies the id.
        realm_name (string): Specifies the realm name.
        kdc_servers (list of string): Specifies a list of Key distribution
            Centre(KDC) Severs.
        admin_server (string): Specifies the admin server used for
            registration from the list of KDC servers.
        ldap_provider_id (long|int): Specifies the LDAP provider id to be
            mapped
        overwritehost_alias (bool): Specifies if specified host alias should
            overwrite existing host alias.
        host_alias (list of string): Specifies the DNS routable host alias
            names.
        admin_password (string): Specifies the password

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "realm_name":'realmName',
        "kdc_servers":'kdcServers',
        "admin_server":'adminServer',
        "host_alias":'hostAlias',
        "admin_password":'adminPassword',
        "id":'id',
        "ldap_provider_id":'ldapProviderId',
        "overwritehost_alias":'overwritehostAlias'
    }

    def __init__(self,
                 realm_name=None,
                 kdc_servers=None,
                 admin_server=None,
                 host_alias=None,
                 admin_password=None,
                 id=None,
                 ldap_provider_id=None,
                 overwritehost_alias=None):
        """Constructor for the RegisterOrUpdateKerberosProviderRequest class"""

        # Initialize members of the class
        self.id = id
        self.realm_name = realm_name
        self.kdc_servers = kdc_servers
        self.admin_server = admin_server
        self.ldap_provider_id = ldap_provider_id
        self.overwritehost_alias = overwritehost_alias
        self.host_alias = host_alias
        self.admin_password = admin_password


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
        realm_name = dictionary.get('realmName')
        kdc_servers = dictionary.get('kdcServers')
        admin_server = dictionary.get('adminServer')
        host_alias = dictionary.get('hostAlias')
        admin_password = dictionary.get('adminPassword')
        id = dictionary.get('id')
        ldap_provider_id = dictionary.get('ldapProviderId')
        overwritehost_alias = dictionary.get('overwritehostAlias')

        # Return an object of this model
        return cls(realm_name,
                   kdc_servers,
                   admin_server,
                   host_alias,
                   admin_password,
                   id,
                   ldap_provider_id,
                   overwritehost_alias)


