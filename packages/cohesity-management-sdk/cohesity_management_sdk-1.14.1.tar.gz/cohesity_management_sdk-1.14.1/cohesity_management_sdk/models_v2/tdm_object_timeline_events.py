# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.tdm_object_timeline_event

class TdmObjectTimelineEvents(object):

    """Implementation of the 'TdmObjectTimelineEvents' model.

    Specifies a collection of TDM object's timeline events.

    Attributes:
        events (list of TdmObjectTimelineEvent): Specifies the collection of
            the timeline events, filtered by the specified criteria.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "events":'events'
    }

    def __init__(self,
                 events=None):
        """Constructor for the TdmObjectTimelineEvents class"""

        # Initialize members of the class
        self.events = events


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
        events = None
        if dictionary.get("events") is not None:
            events = list()
            for structure in dictionary.get('events'):
                events.append(cohesity_management_sdk.models_v2.tdm_object_timeline_event.TdmObjectTimelineEvent.from_dictionary(structure))

        # Return an object of this model
        return cls(events)


