# -*- coding: utf-8 -*-


class TenantDmaasCertificate(object):

    """Implementation of the 'Tenant Dmaas Certificate.' model.

    Specifies the parameters to of a tenant certificate.

    Attributes:
        tenant_id (string): The id of the tenant.
        certificate (string): Specifies the tenant certificate.
        private_key (string): Specifies the tenant private key.
        connector_ca_chain (string): Specifies the CA chain that is used to
            sign the connector certificate.
        passphrase (string): Specifies the passphrase used to encode the
            private key.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "tenant_id":'tenantId',
        "certificate":'certificate',
        "private_key":'privateKey',
        "connector_ca_chain":'connectorCaChain',
        "passphrase":'passphrase'
    }

    def __init__(self,
                 tenant_id=None,
                 certificate=None,
                 private_key=None,
                 connector_ca_chain=None,
                 passphrase=None):
        """Constructor for the TenantDmaasCertificate class"""

        # Initialize members of the class
        self.tenant_id = tenant_id
        self.certificate = certificate
        self.private_key = private_key
        self.connector_ca_chain = connector_ca_chain
        self.passphrase = passphrase


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
        tenant_id = dictionary.get('tenantId')
        certificate = dictionary.get('certificate')
        private_key = dictionary.get('privateKey')
        connector_ca_chain = dictionary.get('connectorCaChain')
        passphrase = dictionary.get('passphrase')

        # Return an object of this model
        return cls(tenant_id,
                   certificate,
                   private_key,
                   connector_ca_chain,
                   passphrase)


