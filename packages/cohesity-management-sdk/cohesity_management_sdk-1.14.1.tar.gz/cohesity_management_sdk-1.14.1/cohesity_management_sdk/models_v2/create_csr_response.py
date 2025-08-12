# -*- coding: utf-8 -*-


class CreateCSRResponse(object):

    """Implementation of the 'Create CSR response' model.

    TODO: type model description here.

    Attributes:
        public_key_server (string): Specifies the public key generated for
            this CSR for the server.
        csr_server (string): Specifies the CSR generated for the server.
        public_key_client (string): Specifies the public key generated for
            this CSR for the client.
        csr_client (string): Specifies the CSR generated for the client.
        file_csr_server (string): Specifies the path to CSR generated for the
            server
        file_csr_client (string): Specifies the path to CSR generated for the
            client

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "public_key_server":'publicKeyServer',
        "csr_server":'csrServer',
        "public_key_client":'publicKeyClient',
        "csr_client":'csrClient',
        "file_csr_server":'fileCsrServer',
        "file_csr_client":'fileCsrClient'
    }

    def __init__(self,
                 public_key_server=None,
                 csr_server=None,
                 public_key_client=None,
                 csr_client=None,
                 file_csr_server=None,
                 file_csr_client=None):
        """Constructor for the CreateCSRResponse class"""

        # Initialize members of the class
        self.public_key_server = public_key_server
        self.csr_server = csr_server
        self.public_key_client = public_key_client
        self.csr_client = csr_client
        self.file_csr_server = file_csr_server
        self.file_csr_client = file_csr_client


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
        public_key_server = dictionary.get('publicKeyServer')
        csr_server = dictionary.get('csrServer')
        public_key_client = dictionary.get('publicKeyClient')
        csr_client = dictionary.get('csrClient')
        file_csr_server = dictionary.get('fileCsrServer')
        file_csr_client = dictionary.get('fileCsrClient')

        # Return an object of this model
        return cls(public_key_server,
                   csr_server,
                   public_key_client,
                   csr_client,
                   file_csr_server,
                   file_csr_client)


