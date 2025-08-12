# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.version_info
import cohesity_management_sdk.models.entity_identifiers


class StringEntityIds(object) :
    """Implementation of the 'StringEntityIds' model.

    This model also specifies the previous ids for a given entity.

    Attributes:
        latest_id (VersionInfo): Specifies the latest string entity id. This
          string id may or may not be same for a given entity across clusters.
          For version 0, the id is guaranteed to be unique across all clusters,
          but not same for the same entity across clusters."
        latest_source_generated_ids (list of EntityIdentifiers): Specifies the latest source-generated ID for an entity.
          It provides the most current identifier assigned by the primary source
          system.
        previous_ids (list of VersionInfo): Specifies all the StringIds previously assigned to this
          entity. Note that it doesn't contain the latest id.
        previous_source_generated_ids (list of EntityIdentifiers): Specifies a list of previously assigned source-generated IDs for
          an entity. It helps in tracking the historical identifiers that were
          assigned by the primary source system. This can be useful for audit
          trails, debugging, or migration purposes.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "latest_id" : 'latestId' ,
        "latest_source_generated_ids" : 'latestSourceGeneratedIds' ,
        "previous_ids" : 'previousIds' ,
        "previous_source_generated_ids" : 'previousSourceGeneratedIds'
    }

    def __init__(self ,
                 latest_id=None ,
                 latest_source_generated_ids=None ,
                 previous_ids=None ,
                 previous_source_generated_ids=None) :
        """Constructor for the StringEntityIds class"""

        # Initialize members of the class
        self.latest_id = latest_id
        self.latest_source_generated_ids = latest_source_generated_ids
        self.previous_ids = previous_ids
        self.previous_source_generated_ids = previous_source_generated_ids

    @classmethod
    def from_dictionary(cls ,
                        dictionary) :
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None :
            return None

        # Extract variables from the dictionary
        latest_id = cohesity_management_sdk.models.version_info.VersionInfo.from_dictionary(
            dictionary.get('latestId')) if dictionary.get('latestId') else None
        latest_source_generated_ids = None
        if dictionary.get("latestSourceGeneratedIds") is not None :
            latest_source_generated_ids = list()
            for structure in dictionary.get('latestSourceGeneratedIds') :
                latest_source_generated_ids.append(
                    cohesity_management_sdk.models.entity_identifiers.EntityIdentifiers.from_dictionary(
                        structure))
        previous_ids = None
        if dictionary.get("previousIds") is not None :
            previous_ids = list()
            for structure in dictionary.get('previousIds') :
                previous_ids.append(
                    cohesity_management_sdk.models.version_info.VersionInfo.from_dictionary(
                        structure))
        previous_source_generated_ids = None
        if dictionary.get("previousSourceGeneratedIds") is not None :
            previous_source_generated_ids = list()
            for structure in dictionary.get('previousSourceGeneratedIds') :
                previous_source_generated_ids.append(
                    cohesity_management_sdk.models.entity_identifiers.EntityIdentifiers.from_dictionary(
                        structure))

        # Return an object of this model
        return cls(latest_id ,
                   latest_source_generated_ids ,
                   previous_ids ,
                   previous_source_generated_ids)