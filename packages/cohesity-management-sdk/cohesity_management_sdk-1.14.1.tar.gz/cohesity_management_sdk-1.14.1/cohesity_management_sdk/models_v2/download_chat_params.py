# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

class DownloadChatParams(object):
    """Implementation of the 'DownloadChatParams' model.

    Specifies the Download chat/posts specific parameters.

    Attributes:
        channel_ids (list of string): Specifies channel IDs whose posts needs to be downloaded. If channelIds is nil or empty then full teams' posts will be downloaded.
        download_file_type (string): Specifies the file type for the downloaded content.
        html_template (string): Specifies the html template for the downloaded chats.
    """

    _names = {
        "channel_ids":"channelIds",
        "download_file_type":"downloadFileType",
        "html_template":"htmlTemplate",
    }

    def __init__(self,
                 channel_ids=None,
                 download_file_type=None,
                 html_template=None):
        """Constructor for the DownloadChatParams class"""

        self.channel_ids = channel_ids
        self.download_file_type = download_file_type
        self.html_template = html_template


    @classmethod
    def from_dictionary(cls, dictionary):
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

        channel_ids = dictionary.get('channelIds')
        download_file_type = dictionary.get('downloadFileType')
        html_template = dictionary.get('htmlTemplate')

        return cls(
            channel_ids,
            download_file_type,
            html_template
        )