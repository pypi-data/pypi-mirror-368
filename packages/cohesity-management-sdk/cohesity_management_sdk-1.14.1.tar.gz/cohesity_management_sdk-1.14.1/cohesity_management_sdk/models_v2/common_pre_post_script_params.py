# -*- coding: utf-8 -*-

class CommonPrePostScriptParams(object):

    """Implementation of the 'Common PrePost Script Params' model.

    Specifies the path to the remote script and any common parameters expected
    by the remote script.

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

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "path":'path',
        "params":'params',
        "timeout_secs":'timeoutSecs',
        "is_active":'isActive'
    }

    def __init__(self,
                 path=None,
                 params=None,
                 timeout_secs=None,
                 is_active=None):
        """Constructor for the CommonPrePostScriptParams class"""

        # Initialize members of the class
        self.path = path
        self.params = params
        self.timeout_secs = timeout_secs
        self.is_active = is_active


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

        # Return an object of this model
        return cls(path,
                   params,
                   timeout_secs,
                   is_active)