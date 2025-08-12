# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class DownloadChatsParams(object):

    """Implementation of the 'DownloadChatsParams' model.

    Message containing params for downloading chat/post messages for
    user/teams/channel.

    Attributes:
        channel_ids_vec (list of string): List of channel IDs whose chats needs to be
            downloaded. This will only be populated when specific channel''s
            posts needs to be downloaded. If this is
            not populated full teams posts will be downloaded.
        download_file_type (int): File type which will be downloaded containing
            chat messages.
        html_template (string): HTML template for the downloaded chats. IRIS
            will populate this by reading the template locally.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "channel_ids_vec":'channelIdsVec',
        "download_file_type":'downloadFileType',
        "html_template":'htmlTemplate'
    }

    def __init__(self,
                 channel_ids_vec=None,
                 download_file_type=None,
                 html_template=None):
        """Constructor for the DownloadChatsParams class"""

        # Initialize members of the class
        self.channel_ids_vec = channel_ids_vec
        self.download_file_type = download_file_type
        self.html_template = html_template


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
        channel_ids_vec = dictionary.get('channelIdsVec')
        download_file_type = dictionary.get('downloadFileType')
        html_template = dictionary.get('htmlTemplate')

        # Return an object of this model
        return cls(channel_ids_vec,
                   download_file_type,
                   html_template)


