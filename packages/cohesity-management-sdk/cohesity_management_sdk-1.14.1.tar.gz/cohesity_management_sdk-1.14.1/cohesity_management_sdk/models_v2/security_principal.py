# -*- coding: utf-8 -*-


class SecurityPrincipal(object):

    """Implementation of the 'SecurityPrincipal' model.

    Specifies a security principal.

    Attributes:
        domain_name (string): Specifies the domain name where the security
            principal account is maintained.
        full_name (string): Specifies the full name (first and last name) of
            the security principal.
        principal_name (string): Specifies the name of the security
            principal.
        object_class (ObjectClassEnum): Specifies the object class of the
            security principal.
        sid (string): Specifies the SID of the security principal.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "domain_name":'domainName',
        "full_name":'fullName',
        "principal_name":'principalName',
        "object_class":'objectClass',
        "sid":'sid'
    }

    def __init__(self,
                 domain_name=None,
                 full_name=None,
                 principal_name=None,
                 object_class=None,
                 sid=None):
        """Constructor for the SecurityPrincipal class"""

        # Initialize members of the class
        self.domain_name = domain_name
        self.full_name = full_name
        self.principal_name = principal_name
        self.object_class = object_class
        self.sid = sid


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
        domain_name = dictionary.get('domainName')
        full_name = dictionary.get('fullName')
        principal_name = dictionary.get('principalName')
        object_class = dictionary.get('objectClass')
        sid = dictionary.get('sid')

        # Return an object of this model
        return cls(domain_name,
                   full_name,
                   principal_name,
                   object_class,
                   sid)


