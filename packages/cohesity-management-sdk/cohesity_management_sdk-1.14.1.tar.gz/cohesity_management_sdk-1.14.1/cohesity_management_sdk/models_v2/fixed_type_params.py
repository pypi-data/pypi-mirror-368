# -*- coding: utf-8 -*-


class FixedTypeParams(object):

    """Implementation of the 'FixedTypeParams' model.

    Specifies the params for Fixed mapping type mapping.

    Attributes:
        uid (long|int): Specifies the fixed Unix UID, when mapping type is set
            to kFixed.
        gid (long|int): Specifies the fixed Unix GID, when mapping type is set
            to kFixed.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "uid":'uid',
        "gid":'gid'
    }

    def __init__(self,
                 uid=None,
                 gid=None):
        """Constructor for the FixedTypeParams class"""

        # Initialize members of the class
        self.uid = uid
        self.gid = gid


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
        uid = dictionary.get('uid')
        gid = dictionary.get('gid')

        # Return an object of this model
        return cls(uid,
                   gid)


