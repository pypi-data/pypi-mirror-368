# -*- coding: utf-8 -*-


class ImportCertificateResponse(object):

    """Implementation of the 'Import Certificate Response' model.

    Specifies the response to import a certificate.

    Attributes:
        certificate_server (string): Specifies the server certificate.
        private_key (string): Specifies the private key of agent.
        file_server_cert (string): Specifies the path to the file to be
            uploaded to server. This file has the server cert, id and
            encrypted private key

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "certificate_server":'certificateServer',
        "private_key":'privateKey',
        "file_server_cert":'fileServerCert'
    }

    def __init__(self,
                 certificate_server=None,
                 private_key=None,
                 file_server_cert=None):
        """Constructor for the ImportCertificateResponse class"""

        # Initialize members of the class
        self.certificate_server = certificate_server
        self.private_key = private_key
        self.file_server_cert = file_server_cert


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
        certificate_server = dictionary.get('certificateServer')
        private_key = dictionary.get('privateKey')
        file_server_cert = dictionary.get('fileServerCert')

        # Return an object of this model
        return cls(certificate_server,
                   private_key,
                   file_server_cert)


