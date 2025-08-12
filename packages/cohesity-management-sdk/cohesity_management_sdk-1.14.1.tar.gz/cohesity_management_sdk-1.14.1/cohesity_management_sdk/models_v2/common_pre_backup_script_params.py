# -*- coding: utf-8 -*-


class CommonPreBackupScriptParams(object):

    """Implementation of the 'Common PreBackup Script Params' model.

    Specifies the common params for PreBackup scripts.

    Attributes:
        path (string): Specifies the absolute path to the script on the remote
            host.
        params (string): Specifies the arguments or parameters and values to
            pass into the remote script. For example if the script expects
            values for the 'database' and 'user' parameters, specify the
            parameters and values using the following string:
            "database=myDatabase user=me".
        timeout_secs (int): Specifies the timeout of the script in seconds.
            The script will be killed if it exceeds this value. By default, no
            timeout will occur if left empty.
        is_active (bool): Specifies whether the script should be enabled,
            default value set to true.
        continue_on_error (bool): Specifies if the script needs to continue
            even if there is an occurence of an error. If this flag is set to
            true, then Backup Run will start even if the pre backup script
            fails. If not specified or false, then backup run will not start
            when script fails.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "path":'path',
        "params":'params',
        "timeout_secs":'timeoutSecs',
        "is_active":'isActive',
        "continue_on_error":'continueOnError'
    }

    def __init__(self,
                 path=None,
                 params=None,
                 timeout_secs=None,
                 is_active=None,
                 continue_on_error=None):
        """Constructor for the CommonPreBackupScriptParams class"""

        # Initialize members of the class
        self.path = path
        self.params = params
        self.timeout_secs = timeout_secs
        self.is_active = is_active
        self.continue_on_error = continue_on_error


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
        path = dictionary.get('path')
        params = dictionary.get('params')
        timeout_secs = dictionary.get('timeoutSecs')
        is_active = dictionary.get('isActive')
        continue_on_error = dictionary.get('continueOnError')

        # Return an object of this model
        return cls(path,
                   params,
                   timeout_secs,
                   is_active,
                   continue_on_error)


