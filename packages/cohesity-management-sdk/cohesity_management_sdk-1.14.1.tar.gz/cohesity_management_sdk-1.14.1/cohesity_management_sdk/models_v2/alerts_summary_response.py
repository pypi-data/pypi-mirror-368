# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.alert_group_summary

class AlertsSummaryResponse(object):

    """Implementation of the 'AlertsSummaryResponse' model.

    Specifies the response of alerts summary.

    Attributes:
        alerts_summary (list of AlertGroupSummary): Specifies a list of alerts
            summary grouped by category.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "alerts_summary":'alertsSummary'
    }

    def __init__(self,
                 alerts_summary=None):
        """Constructor for the AlertsSummaryResponse class"""

        # Initialize members of the class
        self.alerts_summary = alerts_summary


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
        alerts_summary = None
        if dictionary.get("alertsSummary") is not None:
            alerts_summary = list()
            for structure in dictionary.get('alertsSummary'):
                alerts_summary.append(cohesity_management_sdk.models_v2.alert_group_summary.AlertGroupSummary.from_dictionary(structure))

        # Return an object of this model
        return cls(alerts_summary)


