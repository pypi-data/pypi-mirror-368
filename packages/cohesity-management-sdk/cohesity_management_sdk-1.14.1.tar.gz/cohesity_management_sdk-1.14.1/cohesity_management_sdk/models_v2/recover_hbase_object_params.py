# -*- coding: utf-8 -*-


class RecoverHbaseObjectParams(object):

    """Implementation of the 'Recover Hbase Object Params.' model.

    Specifies the fully qualified object name and other attributes of each
    object to be recovered.

    Attributes:
        object_name (string): Specifies the fully qualified name of the object
            to be restored.
        rename_to (string): Specifies the new name to which the object should
            be renamed. at the time of recovery.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "object_name":'objectName',
        "rename_to":'renameTo'
    }

    def __init__(self,
                 object_name=None,
                 rename_to=None):
        """Constructor for the RecoverHbaseObjectParams class"""

        # Initialize members of the class
        self.object_name = object_name
        self.rename_to = rename_to


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
        rename_to = dictionary.get('renameTo')

        # Return an object of this model
        return cls(object_name,
                   rename_to)


