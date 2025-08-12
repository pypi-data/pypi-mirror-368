# -*- coding: utf-8 -*-


class TdmTeardownTaskRequestParams(object):

    """Implementation of the 'TdmTeardownTaskRequestParams' model.

    Specifies the parameters to teardown a clone.

    Attributes:
        clone_id (string): Specifies the ID of the clone to teardown.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "clone_id":'cloneId'
    }

    def __init__(self,
                 clone_id=None):
        """Constructor for the TdmTeardownTaskRequestParams class"""

        # Initialize members of the class
        self.clone_id = clone_id


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
        clone_id = dictionary.get('cloneId')

        # Return an object of this model
        return cls(clone_id)


