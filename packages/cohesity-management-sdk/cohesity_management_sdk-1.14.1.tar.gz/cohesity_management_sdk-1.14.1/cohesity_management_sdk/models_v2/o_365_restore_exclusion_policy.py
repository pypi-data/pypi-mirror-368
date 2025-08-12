# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models_v2.o_365_task_item_restore_exclusion_policy
import cohesity_management_sdk.models_v2.o_365_note_item_restore_exclusion_policy
import cohesity_management_sdk.models_v2.o_365_mail_item_restore_exclusion_policy
import cohesity_management_sdk.models_v2.o_365_contact_item_restore_exclusion_policy
import cohesity_management_sdk.models_v2.o_365_calender_item_restore_exclusion_policy

class O365RestoreExclusionPolicy(object):
    """Implementation of the 'O365RestoreExclusionPolicy' model.

    Specifies the filter policy to be applied for exclusions in Microsoft
      365 restores.

    Attributes:
        calendar_item_policy (O365CalendarItemRestoreExclusionPolicy): Specifies the filter policy to be applied for calendar item exclusions
          in Microsoft 365 mailbox restores.
        contact_item_policy (O365ContactItemRestoreExclusionPolicy): Specifies the filter policy to be applied for contact item exclusions
          in Microsoft 365 mailbox restores.
        mail_item_policy (O365MailItemRestoreExclusionPolicy): Specifies the filter policy to be applied for mail item exclusions
          in Microsoft 365 mailbox restores.
        note_item_policy (O365NoteItemRestoreExclusionPolicy): Specifies the filter policy to be applied for note item exclusions
          in Microsoft 365 mailbox restores.
        task_item_policy (O365TaskItemRestoreExclusionPolicy): Specifies the filter policy to be applied for task item exclusions
          in Microsoft 365 mailbox restores.
    """

    _names = {
        "calendar_item_policy":"calendarItemPolicy",
        "contact_item_policy":"contactItemPolicy",
        "mail_item_policy":"mailItemPolicy",
        "note_item_policy":"noteItemPolicy",
        "task_item_policy":"taskItemPolicy"
    }

    def __init__(self,
                 calendar_item_policy=None,
                 contact_item_policy=None,
                 mail_item_policy=None,
                 note_item_policy=None,
                 task_item_policy=None):
        """Constructor for the O365RestoreExclusionPolicy class"""

        self.calendar_item_policy = calendar_item_policy
        self.contact_item_policy = contact_item_policy
        self.mail_item_policy = mail_item_policy
        self.note_item_policy = note_item_policy
        self.task_item_policy = task_item_policy


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

        calendar_item_policy = cohesity_management_sdk.models_v2.o_365_calender_item_restore_exclusion_policy.O365CalendarItemRestoreExclusionPolicy.from_dictionary(dictionary.get('calendarItemPolicy')) if dictionary.get('calendarItemPolicy') else None
        contact_item_policy = cohesity_management_sdk.models_v2.o_365_contact_item_restore_exclusion_policy.O365ContactItemRestoreExclusionPolicy.from_dictionary(dictionary.get('contactItemPolicy')) if dictionary.get('contactItemPolicy') else None
        mail_item_policy = cohesity_management_sdk.models_v2.o_365_mail_item_restore_exclusion_policy.O365MailItemRestoreExclusionPolicy.from_dictionary(dictionary.get('mailItemPolicy')) if dictionary.get('mailItemPolicy') else None
        note_item_policy = cohesity_management_sdk.models_v2.o_365_note_item_restore_exclusion_policy.O365NoteItemRestoreExclusionPolicy.from_dictionary(dictionary.get('noteItemPolicy')) if dictionary.get('noteItemPolicy') else None
        task_item_policy = cohesity_management_sdk.models_v2.o_365_task_item_restore_exclusion_policy.O365TaskItemRestoreExclusionPolicy.from_dictionary(dictionary.get('taskItemPolicy')) if dictionary.get('taskItemPolicy') else None

        return cls(
            calendar_item_policy,
            contact_item_policy,
            mail_item_policy,
            note_item_policy,
            task_item_policy
        )