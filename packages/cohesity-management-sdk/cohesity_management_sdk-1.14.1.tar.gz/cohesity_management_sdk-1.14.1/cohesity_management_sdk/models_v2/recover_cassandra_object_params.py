# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.no_sql_object_property

class RecoverCassandraObjectParams(object):

    """Implementation of the 'Recover Cassandra Object Params.' model.

    Specifies the fully qualified object name and other attributes of each
    object to be recovered.

    Attributes:
        object_name (string): Specifies the fully qualified name of the object
            to be restored.
        rename_to (string): Specifies the new name to which the object should
            be renamed to after the recovery.
        object_properties (list of NoSqlObjectProperty): Specifies the
            properties to be applied to the object at the time of recovery.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "object_name":'objectName',
        "rename_to":'renameTo',
        "object_properties":'objectProperties'
    }

    def __init__(self,
                 object_name=None,
                 rename_to=None,
                 object_properties=None):
        """Constructor for the RecoverCassandraObjectParams class"""

        # Initialize members of the class
        self.object_name = object_name
        self.rename_to = rename_to
        self.object_properties = object_properties


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
        object_name = dictionary.get('objectName')
        rename_to = dictionary.get('renameTo')
        object_properties = None
        if dictionary.get("objectProperties") is not None:
            object_properties = list()
            for structure in dictionary.get('objectProperties'):
                object_properties.append(cohesity_management_sdk.models_v2.no_sql_object_property.NoSqlObjectProperty.from_dictionary(structure))

        # Return an object of this model
        return cls(object_name,
                   rename_to,
                   object_properties)


