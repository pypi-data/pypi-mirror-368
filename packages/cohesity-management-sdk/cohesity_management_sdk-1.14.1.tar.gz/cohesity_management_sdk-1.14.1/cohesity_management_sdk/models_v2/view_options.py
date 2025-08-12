# -*- coding: utf-8 -*-


class ViewOptions(object):

    """Implementation of the 'View Options' model.

    Specifies the parameters related to the Exchange restore of type view. All
    the files related to one database are cloned to a view and the view can be
    used by third party tools like Kroll, etc. to restore exchange databases.

    Attributes:
        whitelist_restore_view_for_all (bool): Whether to white-list the
            Exchange restore view for all the IP addresses
        view_name (string): The name of the view.
        mount_point (string): The path of the SMB share.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "whitelist_restore_view_for_all":'whitelistRestoreViewForAll',
        "view_name":'viewName',
        "mount_point":'mountPoint'
    }

    def __init__(self,
                 whitelist_restore_view_for_all=None,
                 view_name=None,
                 mount_point=None):
        """Constructor for the ViewOptions class"""

        # Initialize members of the class
        self.whitelist_restore_view_for_all = whitelist_restore_view_for_all
        self.view_name = view_name
        self.mount_point = mount_point


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
        whitelist_restore_view_for_all = dictionary.get('whitelistRestoreViewForAll')
        view_name = dictionary.get('viewName')
        mount_point = dictionary.get('mountPoint')

        # Return an object of this model
        return cls(whitelist_restore_view_for_all,
                   view_name,
                   mount_point)


