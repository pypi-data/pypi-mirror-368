# -*- coding: utf-8 -*-


class RecoverUdaObjectParams(object):

    """Implementation of the 'RecoverUdaObjectParams' model.

    Specifies details of objects to be recovered.

    Attributes:
        object_id (long|int): Specifies the ID of the object.
        object_name (string): Specifies the fully qualified name of the object
            to be restored.
        overwrite (bool): Set to true to overwrite an existing object at the
            destination. If set to false, and the same object exists at the
            destination, then recovery will fail for that object.
        rename_to (string): Specifies the new name to which the object should
            be renamed to after the recovery.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "object_id":'objectId',
        "object_name":'objectName',
        "overwrite":'overwrite',
        "rename_to":'renameTo'
    }

    def __init__(self,
                 object_id=None,
                 object_name=None,
                 overwrite=None,
                 rename_to=None):
        """Constructor for the RecoverUdaObjectParams class"""

        # Initialize members of the class
        self.object_id = object_id
        self.object_name = object_name
        self.overwrite = overwrite
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
        object_id = dictionary.get('objectId')
        object_name = dictionary.get('objectName')
        overwrite = dictionary.get('overwrite')
        rename_to = dictionary.get('renameTo')

        # Return an object of this model
        return cls(object_id,
                   object_name,
                   overwrite,
                   rename_to)