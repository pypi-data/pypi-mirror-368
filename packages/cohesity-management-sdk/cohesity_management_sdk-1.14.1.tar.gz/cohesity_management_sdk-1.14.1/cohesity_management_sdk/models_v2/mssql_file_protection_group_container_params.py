# -*- coding: utf-8 -*-


class MSSQLFileProtectionGroupContainerParams(object):

    """Implementation of the 'MSSQL File Protection Group Container Params' model.

    Specifies the host specific parameters for a host container in this
    protection group. Objects specified here should only be MSSQL root
    containers and will not be protected unless they are also specified in the
    'objects' list. This list is just for specifying source level settings.

    Attributes:
        host_id (long|int): Specifies the id of the host container on which
            databases are hosted.
        host_name (string): Specifies the name of the host container on which
            databases are hosted.
        disable_source_side_deduplication (bool): Specifies whether or not to
            disable source side deduplication on this source. The default
            behavior is false unless the user has set
            'performSourceSideDeduplication' to true.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "host_id":'hostId',
        "host_name":'hostName',
        "disable_source_side_deduplication":'disableSourceSideDeduplication'
    }

    def __init__(self,
                 host_id=None,
                 host_name=None,
                 disable_source_side_deduplication=None):
        """Constructor for the MSSQLFileProtectionGroupContainerParams class"""

        # Initialize members of the class
        self.host_id = host_id
        self.host_name = host_name
        self.disable_source_side_deduplication = disable_source_side_deduplication


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
        host_id = dictionary.get('hostId')
        host_name = dictionary.get('hostName')
        disable_source_side_deduplication = dictionary.get('disableSourceSideDeduplication')

        # Return an object of this model
        return cls(host_id,
                   host_name,
                   disable_source_side_deduplication)


