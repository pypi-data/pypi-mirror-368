# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.object_summary
import cohesity_management_sdk.models_v2.object_snapshot
import cohesity_management_sdk.models_v2.view

class CommonTdmRefreshTaskResponseParams(object):

    """Implementation of the 'CommonTdmRefreshTaskResponseParams' model.

    Specifies the common response params for a TDM refresh task.

    Attributes:
        environment (string): Specifies the environment of the TDM refresh
            task.
        parent (ObjectSummary): Specifies the details of the parent object of
            the clone.
        target (ObjectSummary): Specifies the details of the target, where the
            clone is created.
        snapshot (ObjectSnapshot): Specifies the details of the snapshot used
            for refresh.
        view (View): Specifies the details of the view, which is used for the
            clone.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "environment":'environment',
        "parent":'parent',
        "target":'target',
        "snapshot":'snapshot',
        "view":'view'
    }

    def __init__(self,
                 environment='kOracle',
                 parent=None,
                 target=None,
                 snapshot=None,
                 view=None):
        """Constructor for the CommonTdmRefreshTaskResponseParams class"""

        # Initialize members of the class
        self.environment = environment
        self.parent = parent
        self.target = target
        self.snapshot = snapshot
        self.view = view


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
        environment = dictionary.get("environment") if dictionary.get("environment") else 'kOracle'
        parent = cohesity_management_sdk.models_v2.object_summary.ObjectSummary.from_dictionary(dictionary.get('parent')) if dictionary.get('parent') else None
        target = cohesity_management_sdk.models_v2.object_summary.ObjectSummary.from_dictionary(dictionary.get('target')) if dictionary.get('target') else None
        snapshot = cohesity_management_sdk.models_v2.object_snapshot.ObjectSnapshot.from_dictionary(dictionary.get('snapshot')) if dictionary.get('snapshot') else None
        view = cohesity_management_sdk.models_v2.view.View.from_dictionary(dictionary.get('view')) if dictionary.get('view') else None

        # Return an object of this model
        return cls(environment,
                   parent,
                   target,
                   snapshot,
                   view)


