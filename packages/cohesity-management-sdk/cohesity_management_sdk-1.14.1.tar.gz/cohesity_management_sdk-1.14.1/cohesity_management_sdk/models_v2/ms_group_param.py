# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_recover_object_snapshot_params
import cohesity_management_sdk.models_v2.mailbox_param
import cohesity_management_sdk.models_v2.one_drive_param

class MsGroupParam(object):

    """Implementation of the 'MsGroupParam' model.

    Specifies parameters to recover MS group.

    Attributes:
        mailbox_restore_params (MailboxParam): Specifies parameters to recover a MSGroup Mailbox.
        recover_object (CommonRecoverObjectSnapshotParams): Specifies the MS group recover Object
            info.
        recover_entire_group (bool): Specifies if the entire Group (mailbox +
            site) is to be restored.
        mailbox_restore_type (MailboxRestoreTypeEnum): Specifies whether
            mailbox restore is full or granular.
        site_restore_type (SiteRestoreTypeEnum): Specifies whether site
            restore is full or granular.
        site_restore_params (list of OneDriveParam): Specifies the parameters to recover a MSGroup site document.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "mailbox_restore_params":'mailboxRestoreParams',
        "recover_object":'recoverObject',
        "recover_entire_group":'recoverEntireGroup',
        "mailbox_restore_type":'mailboxRestoreType',
        "site_restore_type":'siteRestoreType',
        "site_restore_params":"siteRestoreParams"
    }

    def __init__(self,
                 mailbox_restore_params=None,
                 recover_object=None,
                 recover_entire_group=None,
                 mailbox_restore_type=None,
                 site_restore_type=None,
                 site_restore_params=None):
        """Constructor for the MsGroupParam class"""

        # Initialize members of the class
        self.mailbox_restore_params = mailbox_restore_params
        self.recover_object = recover_object
        self.recover_entire_group = recover_entire_group
        self.mailbox_restore_type = mailbox_restore_type
        self.site_restore_type = site_restore_type
        self.site_restore_params = site_restore_params


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
        mailbox_restore_params = cohesity_management_sdk.models_v2.mailbox_param.MailboxParam.from_dictionary(dictionary.get('mailboxRestoreParams')) if dictionary.get('mailboxRestoreParams') else None
        recover_object = cohesity_management_sdk.models_v2.common_recover_object_snapshot_params.CommonRecoverObjectSnapshotParams.from_dictionary(dictionary.get('recoverObject')) if dictionary.get('recoverObject') else None
        recover_entire_group = dictionary.get('recoverEntireGroup')
        mailbox_restore_type = dictionary.get('mailboxRestoreType')
        site_restore_type = dictionary.get('siteRestoreType')
        site_restore_params = None
        if dictionary.get('siteRestoreParams') is not None:
            site_restore_params = list()
            for structure in dictionary.get('siteRestoreParams'):
                site_restore_params.append(cohesity_management_sdk.models_v2.one_drive_param.OneDriveParam.from_dictionary(structure))

        # Return an object of this model
        return cls(mailbox_restore_params,
                   recover_object,
                   recover_entire_group,
                   mailbox_restore_type,
                   site_restore_type,
                   site_restore_params)