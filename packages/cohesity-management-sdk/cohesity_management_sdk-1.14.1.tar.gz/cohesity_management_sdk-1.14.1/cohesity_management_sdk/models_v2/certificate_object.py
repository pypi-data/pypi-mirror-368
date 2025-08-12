# -*- coding: utf-8 -*-


class CertificateObject(object):

    """Implementation of the 'CertificateObject' model.

    Specifies Aag Backup Preference Type.

    Attributes:
        data (string): Raw certificate data.
        format (FormatEnum): Specifies the format of certificate (e.g., PEM, PFX).
        password (string): Password for accessing the certificate.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "data":'data',
        "format":'format',
        "password":'password'
    }

    def __init__(self,
                 data=None,
                 format=None,
                 password=None):
        """Constructor for the CertificateObject class"""

        # Initialize members of the class
        self.data = data
        self.format = format
        self.password = password


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
        data = dictionary.get('data')
        format = dictionary.get('format')
        password = dictionary.get('password')

        # Return an object of this model
        return cls(data, format, password)