# -*- coding: utf-8 -*-


class UpdateStateOfProtectionGroups(object):

    """Implementation of the 'Update state of Protection Groups.' model.

    Specifies the parameters to perform an action of list of Protection
    Groups.

    Attributes:
        action (Action5Enum): Specifies the action to be performed on all the
            specfied Protection Groups. 'kActivate' specifies that Protection
            Group should be activated. 'kDeactivate' sepcifies that Protection
            Group should be deactivated. 'kPause' specifies that Protection
            Group should be paused. 'kResume' specifies that Protection Group
            should be resumed.
        ids (list of string): Specifies a list of Protection Group ids for
            which the state should change.
        last_pause_reason (long|int): Specifies the reason why the protection group was paused
        paused_note (string): A note from the current user explaining the reason for pausing
          future runs, if applicable.
        tenant_id (string): Specifies the tenant id who has access to these protection groups.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "action":'action',
        "ids":'ids',
        "last_pause_reason":'lastPauseReason',
        "paused_note":'pausedNote',
        "tenant_id":'tenantId'
    }

    def __init__(self,
                 action=None,
                 ids=None,
                 last_pause_reason=None,
                 paused_note=None,
                 tenant_id=None):
        """Constructor for the UpdateStateOfProtectionGroups class"""

        # Initialize members of the class
        self.action = action
        self.ids = ids
        self.last_pause_reason = last_pause_reason
        self.paused_note = paused_note
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
        action = dictionary.get('action')
        ids = dictionary.get('ids')
        last_pause_reason = dictionary.get('lastPauseReason')
        paused_note = dictionary.get('pausedNote')
        tenant_id = dictionary.get('tenantId')

        # Return an object of this model
        return cls(action,
                   ids,
                   last_pause_reason,
                   paused_note,
                   tenant_id)