# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.replicated_view_name_config

class ReplicationParameters1(object):

    """Implementation of the 'Replication Parameters1' model.

    Specifies the parameters for view replication.

    Attributes:
        view_name_config_list (list of ReplicatedViewNameConfig):
          Specifies the list of remote view names for the protected views
          in the Protection Group. By default the names will be the same as the name
          of the protected view.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "view_name_config_list":'viewNameConfigList'
    }

    def __init__(self,
                 view_name_config_list=None):
        """Constructor for the ReplicationParameters1 class"""

        # Initialize members of the class
        self.view_name_config_list = view_name_config_list


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
        view_name_config_list = None
        if dictionary.get("viewNameConfigList") is not None:
            view_name_config_list = list()
            for structure in dictionary.get('viewNameConfigList'):
                view_name_config_list.append(cohesity_management_sdk.models_v2.replicated_view_name_config.ReplicatedViewNameConfig.from_dictionary(structure))

        # Return an object of this model
        return cls(view_name_config_list)