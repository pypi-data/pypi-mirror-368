# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.object_summary

class Email(object):

    """Implementation of the 'Email' model.

    Specifies an email or an email folder.

    Attributes:
        id (string): Specifies the id of the email object.
        user_object_info (ObjectSummary): Specifies the Object Summary.
        folder_name (string): Specify the name of the email folder.
        is_email_folder (bool): Specify if the object is an email folder.
        email_subject (string): Specifies the subject of this email.
        has_attachment (bool): Specifies whether email has an attachment.
        sender_address (string): Specifies the sender's email address.
        recipient_addresses (list of string): Specifies the email addresses of
            all receipients of this email.
        cc_recipient_addresses (list of string): Specifies the email addresses
            of all the CC receipients of this email.
        bcc_recipient_addresses (list of string): Specifies the email
            addresses of all the BCC receipients of this email.
        sent_time_secs (long|int): Specifies the Unix timestamp epoch in
            seconds at which this email is sent.
        received_time_secs (long|int): Specifies the Unix timestamp epoch in
            seconds at which this email is received.
        protection_group_id (string): Specifies the Protection Group id
            protecting the mailbox.
        storage_domain_id (long|int): Specifies the Storage Domain id where
            the backup data of Object is present.
        tenant_id (string): Specify the tenant id to which this email belongs
            to.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "user_object_info":'userObjectInfo',
        "folder_name":'folderName',
        "is_email_folder":'isEmailFolder',
        "email_subject":'emailSubject',
        "has_attachment":'hasAttachment',
        "sender_address":'senderAddress',
        "recipient_addresses":'recipientAddresses',
        "cc_recipient_addresses":'ccRecipientAddresses',
        "bcc_recipient_addresses":'bccRecipientAddresses',
        "sent_time_secs":'sentTimeSecs',
        "received_time_secs":'receivedTimeSecs',
        "protection_group_id":'protectionGroupId',
        "storage_domain_id":'storageDomainId',
        "tenant_id":'tenantId'
    }

    def __init__(self,
                 id=None,
                 user_object_info=None,
                 folder_name=None,
                 is_email_folder=None,
                 email_subject=None,
                 has_attachment=None,
                 sender_address=None,
                 recipient_addresses=None,
                 cc_recipient_addresses=None,
                 bcc_recipient_addresses=None,
                 sent_time_secs=None,
                 received_time_secs=None,
                 protection_group_id=None,
                 storage_domain_id=None,
                 tenant_id=None):
        """Constructor for the Email class"""

        # Initialize members of the class
        self.id = id
        self.user_object_info = user_object_info
        self.folder_name = folder_name
        self.is_email_folder = is_email_folder
        self.email_subject = email_subject
        self.has_attachment = has_attachment
        self.sender_address = sender_address
        self.recipient_addresses = recipient_addresses
        self.cc_recipient_addresses = cc_recipient_addresses
        self.bcc_recipient_addresses = bcc_recipient_addresses
        self.sent_time_secs = sent_time_secs
        self.received_time_secs = received_time_secs
        self.protection_group_id = protection_group_id
        self.storage_domain_id = storage_domain_id
        self.tenant_id = tenant_id


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
        id = dictionary.get('id')
        user_object_info = cohesity_management_sdk.models_v2.object_summary.ObjectSummary.from_dictionary(dictionary.get('userObjectInfo')) if dictionary.get('userObjectInfo') else None
        folder_name = dictionary.get('folderName')
        is_email_folder = dictionary.get('isEmailFolder')
        email_subject = dictionary.get('emailSubject')
        has_attachment = dictionary.get('hasAttachment')
        sender_address = dictionary.get('senderAddress')
        recipient_addresses = dictionary.get('recipientAddresses')
        cc_recipient_addresses = dictionary.get('ccRecipientAddresses')
        bcc_recipient_addresses = dictionary.get('bccRecipientAddresses')
        sent_time_secs = dictionary.get('sentTimeSecs')
        received_time_secs = dictionary.get('receivedTimeSecs')
        protection_group_id = dictionary.get('protectionGroupId')
        storage_domain_id = dictionary.get('storageDomainId')
        tenant_id = dictionary.get('tenantId')

        # Return an object of this model
        return cls(id,
                   user_object_info,
                   folder_name,
                   is_email_folder,
                   email_subject,
                   has_attachment,
                   sender_address,
                   recipient_addresses,
                   cc_recipient_addresses,
                   bcc_recipient_addresses,
                   sent_time_secs,
                   received_time_secs,
                   protection_group_id,
                   storage_domain_id,
                   tenant_id)


