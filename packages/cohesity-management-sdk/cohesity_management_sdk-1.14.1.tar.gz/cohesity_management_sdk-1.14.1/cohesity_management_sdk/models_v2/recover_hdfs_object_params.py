# -*- coding: utf-8 -*-


class RecoverHdfsObjectParams(object):

    """Implementation of the 'Recover Hdfs Object Params.' model.

    Specifies the fully qualified object name and other attributes of each
    object to be recovered.

    Attributes:
        object_name (string): Specifies the fully qualified name of the object
            to be restored.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "object_name":'objectName'
    }

    def __init__(self,
                 object_name=None):
        """Constructor for the RecoverHdfsObjectParams class"""

        # Initialize members of the class
        self.object_name = object_name


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
        object_name = dictionary.get('objectName')

        # Return an object of this model
        return cls(object_name)


