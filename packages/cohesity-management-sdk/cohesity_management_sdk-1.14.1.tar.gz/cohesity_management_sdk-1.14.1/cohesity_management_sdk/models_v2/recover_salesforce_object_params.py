# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

class RecoverSalesforceObjectParams(object):

    """Implementation of the 'RecoverSfdcObjectParams' model.

    Specifies the parameters to recover Salesforce objects.

    Attributes:
        child_object_ids (list of string): Specifies a list of child object IDs to include in the recovery. Specified object IDs will also be recovered as part of this recovery.
        filter_query (string): Specifies a Query to filter the records. This filtered list of records will be used for recovery.
        include_deleted_objects (bool): Specifies whether to include deleted Objects in the recovery.
        mutation_types (list of MutationTypesEnum): Specifies a list of mutuation types for an object. Mutation type is required in conjunction with 'filterQuery'.
        object_name (string): Specifies the name of the object to be restored.
        parent_object_ids (list of string): Specifies a list of parent object IDs to include in recovery. Specified parent objects will also be recovered as part of this recovery.
        records (list of string): Specifies a list of records IDs to be recovered for the specified Object.
    """

    _names = {
        "child_object_ids":"childObjectIds",
        "filter_query":"filterQuery",
        "include_deleted_objects":"includeDeletedObjects",
        "mutation_types":"mutationTypes",
        "object_name":"objectName",
        "parent_object_ids":"parentObjectIds",
        "records":"records",
    }

    def __init__(self,
                 child_object_ids=None,
                 filter_query=None,
                 include_deleted_objects=None,
                 mutation_types=None,
                 object_name=None,
                 parent_object_ids=None,
                 records=None):
        """Constructor for the RecoverSfdcObjectParams class"""

        self.child_object_ids = child_object_ids
        self.filter_query = filter_query
        self.include_deleted_objects = include_deleted_objects
        self.mutation_types = mutation_types
        self.object_name = object_name
        self.parent_object_ids = parent_object_ids
        self.records = records


    @classmethod
    def from_dictionary(cls, dictionary):
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

        child_object_ids = dictionary.get('childObjectIds')
        filter_query = dictionary.get('filterQuery')
        include_deleted_objects = dictionary.get('includeDeletedObjects')
        mutation_types = dictionary.get('mutationTypes')
        object_name = dictionary.get('objectName')
        parent_object_ids = dictionary.get('parentObjectIds')
        records = dictionary.get('records')

        return cls(
            child_object_ids,
            filter_query,
            include_deleted_objects,
            mutation_types,
            object_name,
            parent_object_ids,
            records
        )