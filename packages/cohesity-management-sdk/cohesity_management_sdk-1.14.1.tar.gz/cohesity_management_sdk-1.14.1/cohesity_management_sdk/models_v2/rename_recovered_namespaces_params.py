# -*- coding: utf-8 -*-


class RenameRecoveredNamespacesParams(object):

    """Implementation of the 'RenameRecoveredNamespacesParams' model.

    Specifies params to rename the Namespaces that are recovered. If not
    specified, the original names of the Namespaces are preserved. If a name
    collision occurs then the Namespace being recovered will overwrite the
    Namespace already present on the source.

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
        """Constructor for the RenameRecoveredNamespacesParams class"""

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


