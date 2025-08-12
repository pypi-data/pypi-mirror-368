# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.object_mailbox_param
import cohesity_management_sdk.models_v2.target_mailbox_param
import cohesity_management_sdk.models_v2.pst_param

class RecoverMailboxParams2(object):

    """Implementation of the 'RecoverMailboxParams2' model.

    Specifies the parameters to recover Office 365 Mailbox.

    Attributes:
        objects (list of ObjectMailboxParam): Specifies a list of Mailbox
            params associated with the objects to recover.
        target_mailbox (TargetMailboxParam): Specifies the target Mailbox to
            recover to. If not specified, the objects will be recovered to
            original location.
        continue_on_error (bool): Specifies whether to continue recovering
            other Mailboxes if one of Mailbox failed to recover. Default value
            is false.
        skip_recover_recoverable_items (bool): Specifies whether to skip the recovery of the Recoverable Items
          present in the selected snapshot. Default value is true
        skip_recover_archive_recoverable_items (bool): Specifies whether to skip the recovery of the Archive Recoverable
          Items present in the selected snapshot. Default value is true
        skip_recover_archive_mailbox (bool): Specifies whether to skip the recovery of the archive mailbox
          and/or items present in the archive mailbox. Default value is true
        pst_params (PstParam): Specifies the PST conversion specific parameters. This should
          always be specified when need to convert selected items to PST.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "target_mailbox":'targetMailbox',
        "continue_on_error":'continueOnError',
        "skip_recover_recoverable_items":'skipRecoverRecoverableItems',
        "skip_recover_archive_recoverable_items":'skipRecoverArchiveRecoverableItems',
        "skip_recover_archive_mailbox":'skipRecoverArchiveMailbox',
        "pst_params":'pstParams'
    }

    def __init__(self,
                 objects=None,
                 target_mailbox=None,
                 continue_on_error=None,
                 skip_recover_recoverable_items=None,
                 skip_recover_archive_recoverable_items=None,
                 skip_recover_archive_mailbox=None,
                 pst_params=None):
        """Constructor for the RecoverMailboxParams2 class"""

        # Initialize members of the class
        self.objects = objects
        self.target_mailbox = target_mailbox
        self.continue_on_error = continue_on_error
        self.skip_recover_recoverable_items = skip_recover_recoverable_items
        self.skip_recover_archive_recoverable_items = skip_recover_archive_recoverable_items
        self.skip_recover_archive_mailbox = skip_recover_archive_mailbox
        self.pst_params = pst_params


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
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.object_mailbox_param.ObjectMailboxParam.from_dictionary(structure))
        target_mailbox = cohesity_management_sdk.models_v2.target_mailbox_param.TargetMailboxParam.from_dictionary(dictionary.get('targetMailbox')) if dictionary.get('targetMailbox') else None
        continue_on_error = dictionary.get('continueOnError')
        skip_recover_recoverable_items = dictionary.get('skipRecoverRecoverableItems')
        skip_recover_archive_recoverable_items = dictionary.get('skipRecoverArchiveRecoverableItems')
        skip_recover_archive_mailbox = dictionary.get('skipRecoverArchiveMailbox')
        pst_params = cohesity_management_sdk.models_v2.pst_param.PstParam.from_dictionary(dictionary.get('pstParams')) if dictionary.get('pstParams') else None

        # Return an object of this model
        return cls(objects,
                   target_mailbox,
                   continue_on_error,
                   skip_recover_recoverable_items,
                   skip_recover_archive_recoverable_items,
                   skip_recover_archive_mailbox,
                   pst_params
                   )