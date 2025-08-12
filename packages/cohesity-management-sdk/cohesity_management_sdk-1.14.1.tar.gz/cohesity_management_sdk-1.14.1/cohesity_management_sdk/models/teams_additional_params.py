# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class TeamsAdditionalParams(object):

    """Implementation of the 'TeamsAdditionalParams' model.

    Specifies additional params for Teams entities. It should only be populated
    if the 'DiscoveryParams.discoverableObjectTypeList' includes 'kTeams'
    otherwise this will be ignored.

    Attributes:
        allow_posts_backup (bool): Specifies whether the Teams
            posts/conversations will be backed up or not.
            If this is false or not specified teams' posts backup will not be
            done.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "allow_posts_backup":'allowPostsBackup'
    }

    def __init__(self,
                 allow_posts_backup=None):
        """Constructor for the TeamsAdditionalParams class"""

        # Initialize members of the class
        self.allow_posts_backup = allow_posts_backup


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
        allow_posts_backup = dictionary.get('allowPostsBackup')

        # Return an object of this model
        return cls(allow_posts_backup)


