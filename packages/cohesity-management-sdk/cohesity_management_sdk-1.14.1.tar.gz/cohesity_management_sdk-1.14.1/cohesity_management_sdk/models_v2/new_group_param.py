# -*- coding: utf-8 -*-


class NewGroupParam(object):

    """Implementation of the 'NewGroupParam' model.

    Specifies the parameters for using a new protection group.

    Attributes:
        name (string): Specifies the name of the new protection group.
        policy_id (string): Specifies the policy id of the new protection
            group.
        storage_domain_id (long|int): Specifies the storage domain id of the
            new protection group.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "policy_id":'policyId',
        "storage_domain_id":'storageDomainId'
    }

    def __init__(self,
                 name=None,
                 policy_id=None,
                 storage_domain_id=None):
        """Constructor for the NewGroupParam class"""

        # Initialize members of the class
        self.name = name
        self.policy_id = policy_id
        self.storage_domain_id = storage_domain_id


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
        name = dictionary.get('name')
        policy_id = dictionary.get('policyId')
        storage_domain_id = dictionary.get('storageDomainId')

        # Return an object of this model
        return cls(name,
                   policy_id,
                   storage_domain_id)


