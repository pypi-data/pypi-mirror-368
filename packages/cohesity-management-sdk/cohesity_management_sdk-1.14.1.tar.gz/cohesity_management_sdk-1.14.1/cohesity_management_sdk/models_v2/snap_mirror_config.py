# -*- coding: utf-8 -*-


class SnapMirrorConfig(object):

    """Implementation of the 'SnapMirrorConfig' model.

    Specifies the snapshot backup configuration if S3 views are used for
    backing up NetApp Data-Protect volumes.

    Attributes:
        view_id (long|int): Specifies the Id of the S3 view where data need to
            be written.
        incremental_prefix (string): Specifies the incremental snapshot prefix
            value.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "view_id":'viewId',
        "incremental_prefix":'incrementalPrefix'
    }

    def __init__(self,
                 view_id=None,
                 incremental_prefix=None):
        """Constructor for the SnapMirrorConfig class"""

        # Initialize members of the class
        self.view_id = view_id
        self.incremental_prefix = incremental_prefix


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
        view_id = dictionary.get('viewId')
        incremental_prefix = dictionary.get('incrementalPrefix')

        # Return an object of this model
        return cls(view_id,
                   incremental_prefix)


