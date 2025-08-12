# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.object_mailbox_param
import cohesity_management_sdk.models_v2.target_mailbox_param
import cohesity_management_sdk.models_v2.ews_exchange_target_params

class RecoverMailboxParams(object):

    """Implementation of the 'RecoverMailboxParams' model.

    Specifies the parameters to recover an Office 365 Mailbox.

    Attributes:
        objects (list of ObjectMailboxParam): Specifies a list of Mailbox
            params associated with the objects to recover.
        target_mailbox (TargetMailboxParam): Specifies the target Mailbox to
            recover to. If not specified, the objects will be recovered to
            original location.
        continue_on_error (bool): Specifies whether to continue recovering
            other Mailboxes if one of Mailbox failed to recover. Default value
            is false.
        ews_exchange_target (EwsExchangeTargetParam): Specifies the Exchange target to recover to.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "target_mailbox":'targetMailbox',
        "continue_on_error":'continueOnError',
        "ews_exchange_target": 'ewsExchangeTarget'
    }

    def __init__(self,
                 objects=None,
                 target_mailbox=None,
                 continue_on_error=None,
                 ews_exchange_target=None):
        """Constructor for the RecoverMailboxParams class"""

        # Initialize members of the class
        self.objects = objects
        self.target_mailbox = target_mailbox
        self.continue_on_error = continue_on_error
        self.ews_exchange_target = ews_exchange_target


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
        ews_exchange_target = cohesity_management_sdk.models_v2.ews_exchange_target_params.EwsExchangeTargetParam.from_dictionary(dictionary.get('ewsExchangeTarget')) if dictionary.get('ewsExchangeTarget') else None

        # Return an object of this model
        return cls(objects,
                   target_mailbox,
                   continue_on_error,
                   ews_exchange_target)