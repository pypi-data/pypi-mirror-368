# -*- coding: utf-8 -*-


class TrustedCaRequest(object):

    """Implementation of the 'TrustedCaRequest' model.

    Specifies the basic info about CA Root Certificate.

    Attributes:
        certificate (string): Specifies the certificate to be imported.
            Certificate should be in PEM format.
        name (string): Descriptive name of the certificate.
        description (string): Description of the certificate.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "certificate":'certificate',
        "name":'name',
        "description":'description'
    }

    def __init__(self,
                 certificate=None,
                 name=None,
                 description=None):
        """Constructor for the TrustedCaRequest class"""

        # Initialize members of the class
        self.certificate = certificate
        self.name = name
        self.description = description


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
        certificate = dictionary.get('certificate')
        name = dictionary.get('name')
        description = dictionary.get('description')

        # Return an object of this model
        return cls(certificate,
                   name,
                   description)


