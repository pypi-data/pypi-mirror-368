# -*- coding: utf-8 -*-


class ReplicationParameters(object):

    """Implementation of the 'Replication Parameters' model.

    Specifies the parameters for view replication.

    Attributes:
        create_view (bool): Specifies whether or not to create a remote view
            on replication cluster.
        view_name (string): Specifies the name of the remote view. By default
            the name will be same as the protected view.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "create_view":'createView',
        "view_name":'viewName'
    }

    def __init__(self,
                 create_view=None,
                 view_name=None):
        """Constructor for the ReplicationParameters class"""

        # Initialize members of the class
        self.create_view = create_view
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
        create_view = dictionary.get('createView')
        view_name = dictionary.get('viewName')

        # Return an object of this model
        return cls(create_view,
                   view_name)


