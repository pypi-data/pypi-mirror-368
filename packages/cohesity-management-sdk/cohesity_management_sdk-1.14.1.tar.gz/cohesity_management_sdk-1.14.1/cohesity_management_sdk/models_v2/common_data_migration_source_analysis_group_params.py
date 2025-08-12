# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.data_migration_source

class CommonDataMigrationSourceAnalysisGroupParams(object):

    """Implementation of the 'CommonDataMigrationSourceAnalysisGroupParams' model.

    Specifies the Data Migration source analysis group.

    Attributes:
        name (string): Specifies the name of the Data Migration analysis
            group.
        source (DataMigrationSource): Specifies the objects to be migrated.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "source":'source'
    }

    def __init__(self,
                 name=None,
                 source=None):
        """Constructor for the CommonDataMigrationSourceAnalysisGroupParams class"""

        # Initialize members of the class
        self.name = name
        self.source = source


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
        name = dictionary.get('name')
        source = cohesity_management_sdk.models_v2.data_migration_source.DataMigrationSource.from_dictionary(dictionary.get('source')) if dictionary.get('source') else None

        # Return an object of this model
        return cls(name,
                   source)


class DataMigrationSourceAnalysisGroup(CommonDataMigrationSourceAnalysisGroupParams):

    """Implementation of the 'DataMigrationSourceAnalysisGroup' model.

    Specifies the Data Migration source analysis group.
    NOTE: This class inherits from
    'CommonDataMigrationSourceAnalysisGroupParams'.

    Attributes:
        id (string): Specifies the ID of the Data Migration source analysis
            group.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "source":'source'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 source=None):
        """Constructor for the DataMigrationSourceAnalysisGroup class"""

        # Initialize members of the class
        self.id = id

        # Call the constructor for the base class
        super(DataMigrationSourceAnalysisGroup, self).__init__(name,
                                                               source)


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
        name = dictionary.get('name')
        source = cohesity_management_sdk.models_v2.data_migration_source.DataMigrationSource.from_dictionary(dictionary.get('source')) if dictionary.get('source') else None

        # Return an object of this model
        return cls(id,
                   name,
                   source)


