# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.entity_proto
import cohesity_management_sdk.models.ews_to_pst_conversion_params
import  cohesity_management_sdk.models.restore_outlook_params_ews_exchange_target
import cohesity_management_sdk.models.restore_outlook_params_mailbox


class RestoreOutlookParams(object):

    """Implementation of the 'RestoreOutlookParams' model.

    TODO: type description here.


    Attributes:
        archive_recoverable_items_prefix (string): Human readable prefix that
            is prepended to the archive recoverable items folder name.
        ews_exchange_target (RestoreOutlookParams_EwsExchangeTarget): Parameters about the Exchange server being recovered to.
        item_recovery_method (long|int): s how items are restored to microsoft. See enum definitions for
          details.
        mailbox_vec (list of RestoreOutlookParams_Mailbox): In a RestoreJob ,
            user will provide the list of mailboxes to be restored. Provision
            is there for restoring full AND partial mailbox recovery.
        pst_params (EwsToPstConversionParams): These are the parameters that
            user can provide for converting/recovering selected EWS items to
            PST format.
        recoverable_items_prefix (string): Human readable prefix that is
            prepended to the recoverable items folder name.
        skip_mbx_permit_for_pst (bool): Indicates whether PST conversion should
            skip mailbox entity permit.
        skip_recover_archive_mailbox (bool): Whether to skip recovery of the
            archive mailbox (or its items).
        skip_recover_archive_recoverable_items (bool): Whether to skip recovery
            of archive recoverable items folders.
        skip_recover_recoverable_items (bool): Whether to skip recovery of
            recoverable items folders.
        target_folder_path (string): User will type the target folder path.
            This will always be specified (whether target_mailbox is original
            mailbox or alternate). If multiple folders are selected, they will
            all be restored to this folder. The appropriate hierarchy along
            with the folder names will be preserved.
        target_mailbox (EntityProto): This is the destination mailbox. All
            mailboxes listed in the mailbox_vec will be restored to this
            mailbox with appropriate names. Let's say mailbox_vec is A and B;
            target_mailbox is C. The final folder-hierarchy after restore job
            is finished will look like this : C : {target_folder_path}/|
            |A/{whatever is there in mailbox A} |B/{whatever is inside B
            mailbox B}
    """


    # Create a mapping from Model property names to API property names
    _names = {
        "archive_recoverable_items_prefix": 'archiveRecoverableItemsPrefix',
        "ews_exchange_target":'ewsExchangeTarget',
        "item_recovery_method":'itemRecoveryMethod',
        "mailbox_vec":'mailboxVec',
        "pst_params":'pstParams',
        "recoverable_items_prefix": 'recoverableItemsPrefix',
        "skip_mbx_permit_for_pst":'skipMbxPermitForPst',
        "skip_recover_archive_mailbox": 'skipRecoverArchiveMailbox',
        "skip_recover_archive_recoverable_items": 'skipRecoverArchiveRecoverableItems',
        "skip_recover_recoverable_items": 'skipRecoverRecoverableItems',
        "target_folder_path":'targetFolderPath',
        "target_mailbox":'targetMailbox',
    }
    def __init__(self,
                 archive_recoverable_items_prefix=None,
                 ews_exchange_target=None,
                 item_recovery_method=None,
                 mailbox_vec=None,
                 pst_params=None,
                 recoverable_items_prefix=None,
                 skip_mbx_permit_for_pst=None,
                 skip_recover_archive_mailbox=None,
                 skip_recover_archive_recoverable_items=None,
                 skip_recover_recoverable_items=None,
                 target_folder_path=None,
                 target_mailbox=None,
            ):

        """Constructor for the RestoreOutlookParams class"""

        # Initialize members of the class
        self.archive_recoverable_items_prefix = archive_recoverable_items_prefix
        self.ews_exchange_target = ews_exchange_target
        self.item_recovery_method = item_recovery_method
        self.mailbox_vec = mailbox_vec
        self.pst_params = pst_params
        self.recoverable_items_prefix = recoverable_items_prefix
        self.skip_mbx_permit_for_pst = skip_mbx_permit_for_pst
        self.skip_recover_archive_mailbox = skip_recover_archive_mailbox
        self.skip_recover_archive_recoverable_items = skip_recover_archive_recoverable_items
        self.skip_recover_recoverable_items = skip_recover_recoverable_items
        self.target_folder_path = target_folder_path
        self.target_mailbox = target_mailbox

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
        archive_recoverable_items_prefix = dictionary.get('archiveRecoverableItemsPrefix')
        ews_exchange_target = cohesity_management_sdk.models.restore_outlook_params_ews_exchange_target.RestoreOutlookParams_EwsExchangeTarget.from_dictionary(dictionary.get('ewsExchangeTarget')) if dictionary.get('ewsExchangeTarget') else None
        item_recovery_method = dictionary.get('itemRecoveryMethod')
        mailbox_vec = None
        if dictionary.get("mailboxVec") is not None:
            mailbox_vec = list()
            for structure in dictionary.get('mailboxVec'):
                mailbox_vec.append(cohesity_management_sdk.models.restore_outlook_params_mailbox.RestoreOutlookParams_Mailbox.from_dictionary(structure))
        pst_params = cohesity_management_sdk.models.ews_to_pst_conversion_params.EwsToPstConversionParams.from_dictionary(dictionary.get('pstParams')) if dictionary.get('pstParams') else None
        skip_mbx_permit_for_pst = dictionary.get('skipMbxPermitForPst')
        skip_recover_archive_mailbox = dictionary.get('skipRecoverArchiveMailbox')
        skip_recover_archive_recoverable_items = dictionary.get('skipRecoverArchiveRecoverableItems')
        skip_recover_recoverable_items = dictionary.get('skipRecoverRecoverableItems')
        recoverable_items_prefix = dictionary.get('recoverableItemsPrefix')
        target_folder_path = dictionary.get('targetFolderPath')
        target_mailbox = cohesity_management_sdk.models.entity_proto.EntityProto.from_dictionary(dictionary.get('targetMailbox')) if dictionary.get('targetMailbox') else None

        # Return an object of this model
        return cls(
            archive_recoverable_items_prefix,
            ews_exchange_target,
            item_recovery_method,
            mailbox_vec,
            pst_params,
            recoverable_items_prefix,
            skip_mbx_permit_for_pst,
            skip_recover_archive_mailbox,
            skip_recover_archive_recoverable_items,
            skip_recover_recoverable_items,
            target_folder_path,
            target_mailbox
)