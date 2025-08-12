# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.pluggable_database_info

class ContainerDatabaseInfo(object):

    """Implementation of the 'ContainerDatabaseInfo' model.

    Object details about Oracle container database.

    Attributes:
        pluggable_database_list (list of PluggableDatabaseInfo): Specifies the
            list of Pluggable databases within a container database.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "pluggable_database_list":'pluggableDatabaseList'
    }

    def __init__(self,
                 pluggable_database_list=None):
        """Constructor for the ContainerDatabaseInfo class"""

        # Initialize members of the class
        self.pluggable_database_list = pluggable_database_list


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
        pluggable_database_list = None
        if dictionary.get("pluggableDatabaseList") is not None:
            pluggable_database_list = list()
            for structure in dictionary.get('pluggableDatabaseList'):
                pluggable_database_list.append(cohesity_management_sdk.models_v2.pluggable_database_info.PluggableDatabaseInfo.from_dictionary(structure))

        # Return an object of this model
        return cls(pluggable_database_list)


