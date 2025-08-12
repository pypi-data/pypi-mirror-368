# -*- coding: utf-8 -*-


class AdFixedTypeParams(object):

    """Implementation of the 'AdFixedTypeParams' model.

    Specifies the properties accociated to a Fixed type user id mapping.

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
        """Constructor for the AdFixedTypeParams class"""

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


