# -*- coding: utf-8 -*-


class TargetSiteParam(object):

    """Implementation of the 'TargetSiteParam' model.

    Specifies the target Site to recover to.

    Attributes:
        id (long|int): Specifies the id of the object.
        name (string): Specifies the name of the object.
        target_doc_lib_name (string): Specifies the name for the target doc lib.
        target_doc_lib_prefix (string): Specifies the prefix for the target doc lib.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "target_doc_lib_name":'targetDocLibName',
        "target_doc_lib_prefix":'targetDocLibPrefix'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 target_doc_lib_name=None,
                 target_doc_lib_prefix=None
                 ):
        """Constructor for the ObjectSiteParam class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.target_doc_lib_name = target_doc_lib_name
        self.target_doc_lib_prefix = target_doc_lib_prefix


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
        id = dictionary.get('id')
        name = dictionary.get('name')
        target_doc_lib_name = dictionary.get('targetDocLibName')
        target_doc_lib_prefix = dictionary.get('targetDocLibPrefix')

        # Return an object of this model
        return cls(id,
                   name,
                   target_doc_lib_name,
                   target_doc_lib_prefix
                   )