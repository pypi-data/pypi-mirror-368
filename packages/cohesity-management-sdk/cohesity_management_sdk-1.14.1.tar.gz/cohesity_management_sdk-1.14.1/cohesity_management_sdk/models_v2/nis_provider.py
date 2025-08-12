# -*- coding: utf-8 -*-


class NisProvider(object):

    """Implementation of the 'NisProvider' model.

    Specifies an NIS Provider.

    Attributes:
        domain (string): Specifies the Domain Name of NIS Provider.
        master_server_hostname (string): Specifies the hostname of Master
            Server.
        slave_servers (list of string): Specifies a list of slave servers in
            the NIS Domain.
        tenant_ids (list of string): Specifies the list of tenant Ids for NIS
            Provider.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "domain":'domain',
        "master_server_hostname":'masterServerHostname',
        "slave_servers":'slaveServers',
        "tenant_ids":'tenantIds'
    }

    def __init__(self,
                 domain=None,
                 master_server_hostname=None,
                 slave_servers=None,
                 tenant_ids=None):
        """Constructor for the NisProvider class"""

        # Initialize members of the class
        self.domain = domain
        self.master_server_hostname = master_server_hostname
        self.slave_servers = slave_servers
        self.tenant_ids = tenant_ids


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
        domain = dictionary.get('domain')
        master_server_hostname = dictionary.get('masterServerHostname')
        slave_servers = dictionary.get('slaveServers')
        tenant_ids = dictionary.get('tenantIds')

        # Return an object of this model
        return cls(domain,
                   master_server_hostname,
                   slave_servers,
                   tenant_ids)


