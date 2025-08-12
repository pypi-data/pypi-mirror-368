# -*- coding: utf-8 -*-


class FailoverSourceCluster1(object):

    """Implementation of the 'Failover source cluster.1' model.

    Specifies the details about source cluster involved in the failover
    operation.

    Attributes:
        id (long|int): Specifies the source cluster Id involved in failover
            operation.
        incarnation_id (long|int): Specifies the source cluster incarnation Id
            involved in failover operation.
        protection_group_id (string): Specifies the protection group Id
            involved in failover operation.
        view_id (long|int): If failover is initiated by view based
            orchastrator, then this field specifies the local view id of
            source cluster which is being failed over.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "incarnation_id":'incarnationId',
        "protection_group_id":'protectionGroupId',
        "view_id":'viewId'
    }

    def __init__(self,
                 id=None,
                 incarnation_id=None,
                 protection_group_id=None,
                 view_id=None):
        """Constructor for the FailoverSourceCluster1 class"""

        # Initialize members of the class
        self.id = id
        self.incarnation_id = incarnation_id
        self.protection_group_id = protection_group_id
        self.view_id = view_id


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
        id = dictionary.get('id')
        incarnation_id = dictionary.get('incarnationId')
        protection_group_id = dictionary.get('protectionGroupId')
        view_id = dictionary.get('viewId')

        # Return an object of this model
        return cls(id,
                   incarnation_id,
                   protection_group_id,
                   view_id)


