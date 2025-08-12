# -*- coding: utf-8 -*-


class SearchPublicFolderRequestParams(object):

    """Implementation of the 'Search Public Folder request params.' model.

    Specifies the request parameters to search for Public Folder items.

    Attributes:
        search_string (string): Specifies the search string to filter the
            items. User can specify a wildcard character '*' as a suffix to a
            string where all item names are matched with the prefix string.
        types (list of Type31Enum): Specifies a list of public folder item
            types. Only items within the given types will be returned.
        has_attachment (bool): Filters the public folder items which have
            attachment.
        sender_address (string): Filters the public folder items which are
            received from specified user's email address.
        recipient_addresses (list of string): Filters the public folder items
            which are sent to specified email addresses.
        cc_recipient_addresses (list of string): Filters the public folder
            items which are sent to specified email addresses in CC.
        bcc_recipient_addresses (list of string): Filters the public folder
            items which are sent to specified email addresses in BCC.
        received_start_time_secs (long|int): Specifies the start time in Unix
            timestamp epoch in seconds where the received time of the public
            folder item is more than specified value.
        received_end_time_secs (long|int): Specifies the end time in Unix
            timestamp epoch in seconds where the received time of the public
            folder items is less than specified value.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "search_string":'searchString',
        "types":'types',
        "has_attachment":'hasAttachment',
        "sender_address":'senderAddress',
        "recipient_addresses":'recipientAddresses',
        "cc_recipient_addresses":'ccRecipientAddresses',
        "bcc_recipient_addresses":'bccRecipientAddresses',
        "received_start_time_secs":'receivedStartTimeSecs',
        "received_end_time_secs":'receivedEndTimeSecs'
    }

    def __init__(self,
                 search_string=None,
                 types=None,
                 has_attachment=None,
                 sender_address=None,
                 recipient_addresses=None,
                 cc_recipient_addresses=None,
                 bcc_recipient_addresses=None,
                 received_start_time_secs=None,
                 received_end_time_secs=None):
        """Constructor for the SearchPublicFolderRequestParams class"""

        # Initialize members of the class
        self.search_string = search_string
        self.types = types
        self.has_attachment = has_attachment
        self.sender_address = sender_address
        self.recipient_addresses = recipient_addresses
        self.cc_recipient_addresses = cc_recipient_addresses
        self.bcc_recipient_addresses = bcc_recipient_addresses
        self.received_start_time_secs = received_start_time_secs
        self.received_end_time_secs = received_end_time_secs


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
        search_string = dictionary.get('searchString')
        types = dictionary.get('types')
        has_attachment = dictionary.get('hasAttachment')
        sender_address = dictionary.get('senderAddress')
        recipient_addresses = dictionary.get('recipientAddresses')
        cc_recipient_addresses = dictionary.get('ccRecipientAddresses')
        bcc_recipient_addresses = dictionary.get('bccRecipientAddresses')
        received_start_time_secs = dictionary.get('receivedStartTimeSecs')
        received_end_time_secs = dictionary.get('receivedEndTimeSecs')

        # Return an object of this model
        return cls(search_string,
                   types,
                   has_attachment,
                   sender_address,
                   recipient_addresses,
                   cc_recipient_addresses,
                   bcc_recipient_addresses,
                   received_start_time_secs,
                   received_end_time_secs)


