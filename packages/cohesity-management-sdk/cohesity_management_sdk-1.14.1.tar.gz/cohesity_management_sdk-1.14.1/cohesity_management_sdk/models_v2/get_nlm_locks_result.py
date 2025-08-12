# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.file_nlm_locks

class GetNlmLocksResult(object):

    """Implementation of the 'GetNlmLocksResult' model.

    Specifies the list of NLM locks.

    Attributes:
        file_nlm_locks (list of FileNlmLocks): Specifies the list of NLM locks.
        cookie (string): Specifies the pagination cookie.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "file_nlm_locks":'fileNlmLocks',
        "cookie":'cookie'
    }

    def __init__(self,
                 file_nlm_locks=None,
                 cookie=None):
        """Constructor for the GetNlmLocksResult class"""

        # Initialize members of the class
        self.file_nlm_locks = file_nlm_locks
        self.cookie = cookie


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
        file_nlm_locks = None
        if dictionary.get("fileNlmLocks") is not None:
            file_nlm_locks = list()
            for structure in dictionary.get('fileNlmLocks'):
                file_nlm_locks.append(cohesity_management_sdk.models_v2.file_nlm_locks.FileNlmLocks.from_dictionary(structure))
        cookie =  dictionary.get('cookie')

        # Return an object of this model
        return cls(file_nlm_locks,
                   cookie)


