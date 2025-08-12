# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.o_365_search_emails_request_params

class SearchEmailsRequestParams(object):

    """Implementation of the 'Search emails request params.' model.

    Specifies the request parameters to search for emails and email folders.

    Attributes:
        has_attachment (bool): Filters the emails which have attachment.
        sender_address (string): Filters the emails which are received from
            specified User's email address.
        recipient_addresses (list of string): Filters the emails which are
            sent to specified email addresses.
        cc_recipient_addresses (list of string): Filters the emails which are
            sent to specified email addresses in CC.
        bcc_recipient_addresses (list of string): Filters the emails which are
            sent to specified email addresses in BCC.
        received_start_time_secs (long|int): Specifies the start time in Unix
            timestamp epoch in seconds where the received time of the email is
            more than specified value.
        received_end_time_secs (long|int): Specifies the end time in Unix
            timestamp epoch in seconds where the received time of the email is
            less than specified value.
        email_subject (string): Filters the emails which have the specified
            text in its subject.
        folder_name (string): Filters the emails which are categorized to
            specified folder.
        include_only_email_folders (bool): Specifies whether to only include
            email folders in the response. Default is false.
        source_environment (SourceEnvironmentEnum): Specifies the source
            environment.
        o_365_params (O365SearchEmailsRequestParams): Specifies email search
            request params specific to O365 environment.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "has_attachment":'hasAttachment',
        "sender_address":'senderAddress',
        "recipient_addresses":'recipientAddresses',
        "cc_recipient_addresses":'ccRecipientAddresses',
        "bcc_recipient_addresses":'bccRecipientAddresses',
        "received_start_time_secs":'receivedStartTimeSecs',
        "received_end_time_secs":'receivedEndTimeSecs',
        "email_subject":'emailSubject',
        "folder_name":'folderName',
        "include_only_email_folders":'includeOnlyEmailFolders',
        "source_environment":'sourceEnvironment',
        "o_365_params":'o365Params'
    }

    def __init__(self,
                 has_attachment=None,
                 sender_address=None,
                 recipient_addresses=None,
                 cc_recipient_addresses=None,
                 bcc_recipient_addresses=None,
                 received_start_time_secs=None,
                 received_end_time_secs=None,
                 email_subject=None,
                 folder_name=None,
                 include_only_email_folders=False,
                 source_environment=None,
                 o_365_params=None):
        """Constructor for the SearchEmailsRequestParams class"""

        # Initialize members of the class
        self.has_attachment = has_attachment
        self.sender_address = sender_address
        self.recipient_addresses = recipient_addresses
        self.cc_recipient_addresses = cc_recipient_addresses
        self.bcc_recipient_addresses = bcc_recipient_addresses
        self.received_start_time_secs = received_start_time_secs
        self.received_end_time_secs = received_end_time_secs
        self.email_subject = email_subject
        self.folder_name = folder_name
        self.include_only_email_folders = include_only_email_folders
        self.source_environment = source_environment
        self.o_365_params = o_365_params


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
        has_attachment = dictionary.get('hasAttachment')
        sender_address = dictionary.get('senderAddress')
        recipient_addresses = dictionary.get('recipientAddresses')
        cc_recipient_addresses = dictionary.get('ccRecipientAddresses')
        bcc_recipient_addresses = dictionary.get('bccRecipientAddresses')
        received_start_time_secs = dictionary.get('receivedStartTimeSecs')
        received_end_time_secs = dictionary.get('receivedEndTimeSecs')
        email_subject = dictionary.get('emailSubject')
        folder_name = dictionary.get('folderName')
        include_only_email_folders = dictionary.get("includeOnlyEmailFolders") if dictionary.get("includeOnlyEmailFolders") else False
        source_environment = dictionary.get('sourceEnvironment')
        o_365_params = cohesity_management_sdk.models_v2.o_365_search_emails_request_params.O365SearchEmailsRequestParams.from_dictionary(dictionary.get('o365Params')) if dictionary.get('o365Params') else None

        # Return an object of this model
        return cls(has_attachment,
                   sender_address,
                   recipient_addresses,
                   cc_recipient_addresses,
                   bcc_recipient_addresses,
                   received_start_time_secs,
                   received_end_time_secs,
                   email_subject,
                   folder_name,
                   include_only_email_folders,
                   source_environment,
                   o_365_params)


