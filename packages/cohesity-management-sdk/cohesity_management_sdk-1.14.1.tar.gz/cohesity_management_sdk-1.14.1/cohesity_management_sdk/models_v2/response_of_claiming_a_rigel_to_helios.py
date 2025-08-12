# -*- coding: utf-8 -*-


class ResponseOfClaimingARigelToHelios(object):

    """Implementation of the 'Response of claiming a Rigel to Helios.' model.

    Specifies the response of claiming a Rigel to Helios.

    Attributes:
        rigel_guid (long|int): Unique id for rigel instance.
        connection_id (long|int): Connection id for rigel instance.
        tenant_id (string): Tenant id associated with the claimed rigel.
        rigel_type (RigelTypeEnum): Specifies the Rigel type that is being
            claimed.
        rigel_certificate (string): Specifies the Rigel certificate.
        rigel_private_key (string): Specifies the Rigel private key.
        rigel_ca_chain (string): Specifies the CA chain that is used to sign
            the Rigel certificate.
        tenant_ca_chain (list of string): Specifies the Tenant CA chain.
        helios_certificate (string): Specifies the Helios certificate that can
            be used to authenticate api calls made from Helios to Rigel.
        dataplane_endpoint (string): Endpoint for associated data plane.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "rigel_guid":'rigelGuid',
        "connection_id":'connectionId',
        "tenant_id":'tenantId',
        "rigel_type":'rigelType',
        "rigel_certificate":'rigelCertificate',
        "rigel_private_key":'rigelPrivateKey',
        "rigel_ca_chain":'rigelCaChain',
        "tenant_ca_chain":'tenantCaChain',
        "helios_certificate":'heliosCertificate',
        "dataplane_endpoint":'dataplaneEndpoint'
    }

    def __init__(self,
                 rigel_guid=None,
                 connection_id=None,
                 tenant_id=None,
                 rigel_type=None,
                 rigel_certificate=None,
                 rigel_private_key=None,
                 rigel_ca_chain=None,
                 tenant_ca_chain=None,
                 helios_certificate=None,
                 dataplane_endpoint=None):
        """Constructor for the ResponseOfClaimingARigelToHelios class"""

        # Initialize members of the class
        self.rigel_guid = rigel_guid
        self.connection_id = connection_id
        self.tenant_id = tenant_id
        self.rigel_type = rigel_type
        self.rigel_certificate = rigel_certificate
        self.rigel_private_key = rigel_private_key
        self.rigel_ca_chain = rigel_ca_chain
        self.tenant_ca_chain = tenant_ca_chain
        self.helios_certificate = helios_certificate
        self.dataplane_endpoint = dataplane_endpoint


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
        rigel_guid = dictionary.get('rigelGuid')
        connection_id = dictionary.get('connectionId')
        tenant_id = dictionary.get('tenantId')
        rigel_type = dictionary.get('rigelType')
        rigel_certificate = dictionary.get('rigelCertificate')
        rigel_private_key = dictionary.get('rigelPrivateKey')
        rigel_ca_chain = dictionary.get('rigelCaChain')
        tenant_ca_chain = dictionary.get('tenantCaChain')
        helios_certificate = dictionary.get('heliosCertificate')
        dataplane_endpoint = dictionary.get('dataplaneEndpoint')

        # Return an object of this model
        return cls(rigel_guid,
                   connection_id,
                   tenant_id,
                   rigel_type,
                   rigel_certificate,
                   rigel_private_key,
                   rigel_ca_chain,
                   tenant_ca_chain,
                   helios_certificate,
                   dataplane_endpoint)


