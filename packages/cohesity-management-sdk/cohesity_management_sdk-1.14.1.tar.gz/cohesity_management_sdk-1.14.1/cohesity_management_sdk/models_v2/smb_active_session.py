# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.smb_active_open

class SmbActiveSession(object):

    """Implementation of the 'SmbActiveSession' model.

    Specifies an active session and its file opens.

    Attributes:
        session_id (long|int): Specifies the id of the session.
        client_ip (string): Specifies the IP address from which the file is open.
        user_name (string): Specifies the username who keeps the file open.
        domain (string): Specifies the domain of the user.
        active_opens (list of SmbActiveOpen): Specifies an active open of an SMB file, its access and sharing
          information.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "session_id":'sessionId',
        "client_ip":'clientIp',
        "user_name":'userName',
        "domain":'domain',
        "active_opens":'activeOpens'
    }

    def __init__(self,
                 session_id=None,
                 client_ip=None,
                 user_name=None,
                 domain=None,
                 active_opens=None):
        """Constructor for the SmbActiveSession class"""

        # Initialize members of the class
        self.session_id = session_id
        self.client_ip = client_ip
        self.user_name = user_name
        self.domain = domain
        self.active_opens = active_opens


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
        session_id = dictionary.get('sessionId')
        client_ip = dictionary.get('clientIp')
        domain = dictionary.get('domain')
        user_name = dictionary.get('userName')
        active_opens = None
        if dictionary.get("activeOpens") is not None:
            active_opens = list()
            for structure in dictionary.get('activeOpens'):
                active_opens.append(cohesity_management_sdk.models_v2.smb_active_open.SmbActiveOpen.from_dictionary(structure))

        # Return an object of this model
        return cls(session_id,
                   client_ip,
                   user_name,
                   domain,
                   active_opens)


