# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_recover_object_snapshot_params
import cohesity_management_sdk.models_v2.mailbox_param

class ObjectMailboxParam(object):

    """Implementation of the 'ObjectMailboxParam' model.

    Specifies Mailbox recovery parameters associated with a user.

    Attributes:
        owner_info (CommonRecoverObjectSnapshotParams): Specifies the Mailbox owner info.
        mailbox_params (MailboxParam): Specifies parameters to recover a
            Mailbox.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "owner_info":'ownerInfo',
        "mailbox_params":'mailboxParams'
    }

    def __init__(self,
                 owner_info=None,
                 mailbox_params=None):
        """Constructor for the ObjectMailboxParam class"""

        # Initialize members of the class
        self.owner_info = owner_info
        self.mailbox_params = mailbox_params


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
        owner_info = cohesity_management_sdk.models_v2.common_recover_object_snapshot_params.CommonRecoverObjectSnapshotParams.from_dictionary(dictionary.get('ownerInfo')) if dictionary.get('ownerInfo') else None
        mailbox_params = cohesity_management_sdk.models_v2.mailbox_param.MailboxParam.from_dictionary(dictionary.get('mailboxParams')) if dictionary.get('mailboxParams') else None

        # Return an object of this model
        return cls(owner_info,
                   mailbox_params)