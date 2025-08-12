# -*- coding: utf-8 -*-


class ExpirationAction(object):

    """Implementation of the 'ExpirationAction' model.

    Specifies the Lifecycle current version ExpirationAction. Note:
      All the three fields are mutually exclusive to each other.

    Attributes:
        date_in_usecs (long|int64): Specifies the Timestamp in Usecs for the
          date when the object is subject to the rule.
        days (long|int64): Specifies the Lifetime in days of the objects that are subject
          to the rule.
        expired_object_delete_marker (bool): Specifies whether Amazon S3 will remove
          a delete marker with no non-current versions.
          If set, the delete marker will be expired.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "date_in_usecs":'dateInUsecs',
        "days":'days',
        "expired_object_delete_marker":'expiredObjectDeleteMarker'
    }

    def __init__(self,
                 date_in_usecs=None,
                 days=None,
                 expired_object_delete_marker=None):
        """Constructor for the ExpirationAction class"""

        # Initialize members of the class
        self.date_in_usecs = date_in_usecs
        self.days = days
        self.expired_object_delete_marker = expired_object_delete_marker


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
        date_in_usecs = dictionary.get('dateInUsecs')
        days = dictionary.get('days')
        expired_object_delete_marker = dictionary.get('expiredObjectDeleteMarker')

        # Return an object of this model
        return cls(date_in_usecs,
                   days,
                   expired_object_delete_marker)