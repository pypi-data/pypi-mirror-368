# -*- coding: utf-8 -*-


class RedoLogGroupConfig(object):

    """Implementation of the 'RedoLogGroupConfig' model.

    Specifies Redo log group configuration

    Attributes:
        num_groups (int): Specifies no. of redo log groups.
        member_prefix (string): Specifies Log member name prefix.
        size_m_bytes (int): Specifies Size of the member in MB.
        group_members (list of string): Specifies list of members of this redo
            log group.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "num_groups":'numGroups',
        "member_prefix":'memberPrefix',
        "size_m_bytes":'sizeMBytes',
        "group_members":'groupMembers'
    }

    def __init__(self,
                 num_groups=None,
                 member_prefix=None,
                 size_m_bytes=None,
                 group_members=None):
        """Constructor for the RedoLogGroupConfig class"""

        # Initialize members of the class
        self.num_groups = num_groups
        self.member_prefix = member_prefix
        self.size_m_bytes = size_m_bytes
        self.group_members = group_members


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
        num_groups = dictionary.get('numGroups')
        member_prefix = dictionary.get('memberPrefix')
        size_m_bytes = dictionary.get('sizeMBytes')
        group_members = dictionary.get('groupMembers')

        # Return an object of this model
        return cls(num_groups,
                   member_prefix,
                   size_m_bytes,
                   group_members)


