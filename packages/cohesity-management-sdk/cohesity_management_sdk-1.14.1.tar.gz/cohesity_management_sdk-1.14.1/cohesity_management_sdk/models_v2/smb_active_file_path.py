# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.smb_active_session

class SmbActiveFilePath(object):

    """Implementation of the 'SmbActiveFilePath' model.

    Specifies a file path in an SMB view that has active sessions and

    Attributes:
        view_name (string): Specifies the name of the View.
        view_id (long|int): Specifies the id of the View.
            target information if this is an archival snapshot.
        file_path (string): Specifies the filepath in the view.
        active_sessions (list of SmbActiveSession): Specifies an active
            session where the file is open.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "view_name":'viewName',
        "view_id":'viewId',
        "file_path":'filePath',
        "active_sessions":'activeSessions'
    }

    def __init__(self,
                 view_name=None,
                 view_id=None,
                 file_path=None,
                 active_sessions=None):
        """Constructor for the SmbActiveFilePath class"""

        # Initialize members of the class
        self.view_name = view_name
        self.view_id = view_id
        self.file_path = file_path
        self.active_sessions = active_sessions


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
        view_name = dictionary.get('viewName')
        view_id = dictionary.get('viewId')
        file_path = dictionary.get('filePath')
        active_sessions = None
        if dictionary.get("activeSessions") is not None:
            active_sessions = list()
            for structure in dictionary.get('activeSessions'):
                active_sessions.append(cohesity_management_sdk.models_v2.smb_active_session.SmbActiveSession.from_dictionary(structure))

        # Return an object of this model
        return cls(view_name,
                   view_id,
                   file_path,
                   active_sessions)


