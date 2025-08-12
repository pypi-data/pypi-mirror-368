# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

class Schema(object):

    """Implementation of the 'Schema' model.

    Specifies the metric data point where public data metric as key and
      the schema defined metric name as value.

    Attributes:
        entity_id (string): Specifies the id of the entity.
        metric_name (string): Specifies the name of schema metric.
        schema_name (string): Specifies the name of the schema.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "entity_id":'entityId',
        "metric_name":'metricName',
        "schema_name":'schemaName'
    }

    def __init__(self,
                 entity_id=None,
                 metric_name=None,
                 schema_name=None):
        """Constructor for the Schema class"""

        # Initialize members of the class
        self.entity_id = entity_id
        self.metric_name = metric_name
        self.schema_name = schema_name


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
        entity_id = dictionary.get('entityId')
        metric_name = dictionary.get('metricName')
        schema_name = dictionary.get('schemaName')

        # Return an object of this model
        return cls(entity_id,
                   metric_name,
                   schema_name)