# -*- coding: utf-8 -*-


class CloudDownWaterFallParams(object):

    """Implementation of the 'CloudDownWaterFallParams' model.

    Specifies parameters for cloud down water fall thresholds.

    Attributes:
        threshold_percentage (long|int): Specifies the threshold percentage for cloud down water fall.
          This value indicates how full a storage domain is before cohesity cluster
          down water fall its data to cloud tier. This field is only appliciable if
          physicalQuota is set.
        threshold_secs (long_int): Specifes a time in seconds when cloud down water fall starts.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "threshold_percentage":'thresholdPercentage',
        "threshold_secs":'thresholdSecs'
    }

    def __init__(self,
                 threshold_percentage=None,
                 threshold_secs=None):
        """Constructor for the CloudDownWaterFallParams class"""

        # Initialize members of the class
        self.threshold_percentage = threshold_percentage
        self.threshold_secs = threshold_secs


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
        threshold_percentage = dictionary.get('thresholdPercentage')
        threshold_secs = dictionary.get('thresholdSecs')

        # Return an object of this model
        return cls(threshold_percentage,
                   threshold_secs)