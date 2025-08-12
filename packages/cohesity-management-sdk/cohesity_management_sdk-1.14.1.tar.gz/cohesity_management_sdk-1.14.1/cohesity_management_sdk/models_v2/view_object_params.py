# -*- coding: utf-8 -*-


class ViewObjectParams(object):

    """Implementation of the 'ViewObjectParams' model.

    Specifies the details of a view.

    Attributes:
        name (string): Specifies the name of the view.
        uid (string): Specifies a distinct value that's unique to a source.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "uid":'uid'
    }

    def __init__(self,
                 name=None,
                 uid=None) :
        """Constructor for the ViewObjectParams class"""

        # Initialize members of the class
        self.name = name
        self.uid = uid

    @classmethod
    def from_dictionary(cls ,
                        dictionary) :
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None :
            return None

        # Extract variables from the dictionary
        name = dictionary.get('name')
        uid = dictionary.get('uid')

        # Return an object of this model
        return cls(name,
                   uid)