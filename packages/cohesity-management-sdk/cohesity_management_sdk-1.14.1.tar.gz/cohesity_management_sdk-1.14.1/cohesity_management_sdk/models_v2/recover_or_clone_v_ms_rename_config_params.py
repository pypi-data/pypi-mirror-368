# -*- coding: utf-8 -*-


class RecoverOrCloneVMsRenameConfigParams(object):

    """Implementation of the 'Recover or Clone VMs Rename Config params.' model.

    Specifies the prefix and suffix to be added to VMs that are recovered or
    cloned.

    Attributes:
        prefix (string): Specifies the prefix string to be added to recovered
            or cloned object names.
        suffix (string): Specifies the suffix string to be added to recovered
            or cloned object names.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "prefix":'prefix',
        "suffix":'suffix'
    }

    def __init__(self,
                 prefix=None,
                 suffix=None):
        """Constructor for the RecoverOrCloneVMsRenameConfigParams class"""

        # Initialize members of the class
        self.prefix = prefix
        self.suffix = suffix


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
        prefix = dictionary.get('prefix')
        suffix = dictionary.get('suffix')

        # Return an object of this model
        return cls(prefix,
                   suffix)


