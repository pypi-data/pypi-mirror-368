# -*- coding: utf-8 -*-


class VmwareVCenterCredentialInfo(object):

    """Implementation of the 'VMware vCenter Credential Info' model.

    Specifies the credential information for a specific vcenter.

    Attributes:
        username (string): Specifies the username to access target entity.
        password (string): Specifies the password to access target entity.
        endpoint (string): Specifies the endpoint IPaddress, URL or hostname
            of the host.
        description (string): Specifies the description of the source being
            registered.
        name (string): Specifies the name of the vCenter.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "username":'username',
        "password":'password',
        "endpoint":'endpoint',
        "description":'description',
        "name":'name'
    }

    def __init__(self,
                 username=None,
                 password=None,
                 endpoint=None,
                 description=None,
                 name=None):
        """Constructor for the VmwareVCenterCredentialInfo class"""

        # Initialize members of the class
        self.username = username
        self.password = password
        self.endpoint = endpoint
        self.description = description
        self.name = name


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
        username = dictionary.get('username')
        password = dictionary.get('password')
        endpoint = dictionary.get('endpoint')
        description = dictionary.get('description')
        name = dictionary.get('name')

        # Return an object of this model
        return cls(username,
                   password,
                   endpoint,
                   description,
                   name)


