# -*- coding: utf-8 -*-


class ReplicatedViewNameConfig(object):

    """Implementation of the 'ReplicatedViewNameConfig' model.

    Specifies an object protected by a View Protection Group.

    Attributes:
        source_view_id (long|int): Specifies the ID of the protected view.
        use_same_view_name (bool): Specifies if the remote view name to be
            kept is same as the source view name. If this field is true,
            viewName field will be ignored.
        view_name (string): Specifies the name of the remote view. This field
            is only used when useSameViewName is false. If useSameViewName is
            true, this field is not used.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source_view_id":'sourceViewId',
        "use_same_view_name":'useSameViewName',
        "view_name":'viewName'
    }

    def __init__(self,
                 source_view_id=None,
                 use_same_view_name=None,
                 view_name=None):
        """Constructor for the ReplicatedViewNameConfig class"""

        # Initialize members of the class
        self.source_view_id = source_view_id
        self.use_same_view_name = use_same_view_name
        self.view_name = view_name


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
        source_view_id = dictionary.get('sourceViewId')
        use_same_view_name = dictionary.get('useSameViewName')
        view_name = dictionary.get('viewName')

        # Return an object of this model
        return cls(source_view_id,
                   use_same_view_name,
                   view_name)


