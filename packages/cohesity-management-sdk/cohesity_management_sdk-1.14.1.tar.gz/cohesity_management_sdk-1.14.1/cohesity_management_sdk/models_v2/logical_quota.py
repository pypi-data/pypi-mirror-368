# -*- coding: utf-8 -*-


class LogicalQuota(object):

    """Implementation of the 'LogicalQuota' model.

    Specifies an optional logical quota limit (in bytes) for the usage
    allowed
    on this View.
    (Logical data is when the data is fully hydrated and expanded.)
    This limit overrides the limit inherited from the Storage Domain
    (View Box) (if set).
    If logicalQuota is nil, the limit is inherited from the
    Storage Domain (View Box) (if set).
    A new write is not allowed if the Storage Domain (View Box) will exceed
    the
    specified quota.
    However, it takes time for the Cohesity Cluster to calculate
    the usage across Nodes, so the limit may be exceeded by a small amount.
    In addition, if the limit is increased or data is removed,
    there may be a delay before the Cohesity Cluster allows more data
    to be written to the View, as the Cluster is calculating the usage
    across Nodes.

    Attributes:
        alert_limit_bytes (long|int): Specifies if an alert should be
            triggered when the usage of this resource exceeds this quota
            limit. This limit is optional and is specified in bytes. If no
            value is specified, there is no limit.
        alert_threshold_percentage (long|int): Supported only for user quota
            policy. Specifies when the usage goes above an alert threshold
            percentage which is: HardLimitBytes * AlertThresholdPercentage,
            eg: 80% of HardLimitBytes Can only be set if HardLimitBytes is
            set. Cannot be set if AlertLimitBytes is already set.
        hard_limit_bytes (long|int): Specifies an optional quota limit on the
            usage allowed for this resource. This limit is specified in bytes.
            If no value is specified, there is no limit.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "alert_limit_bytes":'alertLimitBytes',
        "alert_threshold_percentage":'alertThresholdPercentage',
        "hard_limit_bytes":'hardLimitBytes'
    }

    def __init__(self,
                 alert_limit_bytes=None,
                 alert_threshold_percentage=None,
                 hard_limit_bytes=None):
        """Constructor for the LogicalQuota class"""

        # Initialize members of the class
        self.alert_limit_bytes = alert_limit_bytes
        self.alert_threshold_percentage = alert_threshold_percentage
        self.hard_limit_bytes = hard_limit_bytes


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
        alert_limit_bytes = dictionary.get('alertLimitBytes')
        alert_threshold_percentage = dictionary.get('alertThresholdPercentage')
        hard_limit_bytes = dictionary.get('hardLimitBytes')

        # Return an object of this model
        return cls(alert_limit_bytes,
                   alert_threshold_percentage,
                   hard_limit_bytes)


