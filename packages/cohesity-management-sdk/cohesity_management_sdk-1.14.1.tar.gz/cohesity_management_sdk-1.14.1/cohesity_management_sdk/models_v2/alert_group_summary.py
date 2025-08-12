# -*- coding: utf-8 -*-


class AlertGroupSummary(object):

    """Implementation of the 'AlertGroupSummary' model.

    Specifies alerts summary grouped for an alert category.

    Attributes:
        category (CategoryEnum): Category of alerts by which summary is
            grouped.
        mtype (string): Type/bucket that this alert category belongs to.
        warning_count (long|int): Specifies count of warning alerts.
        critical_count (long|int): Specifies count of critical alerts.
        info_count (long|int): Specifies count of info alerts.
        total_count (long|int): Specifies count of total alerts.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "category":'category',
        "mtype":'type',
        "warning_count":'warningCount',
        "critical_count":'criticalCount',
        "info_count":'infoCount',
        "total_count":'totalCount'
    }

    def __init__(self,
                 category=None,
                 mtype=None,
                 warning_count=None,
                 critical_count=None,
                 info_count=None,
                 total_count=None):
        """Constructor for the AlertGroupSummary class"""

        # Initialize members of the class
        self.category = category
        self.mtype = mtype
        self.warning_count = warning_count
        self.critical_count = critical_count
        self.info_count = info_count
        self.total_count = total_count


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
        category = dictionary.get('category')
        mtype = dictionary.get('type')
        warning_count = dictionary.get('warningCount')
        critical_count = dictionary.get('criticalCount')
        info_count = dictionary.get('infoCount')
        total_count = dictionary.get('totalCount')

        # Return an object of this model
        return cls(category,
                   mtype,
                   warning_count,
                   critical_count,
                   info_count,
                   total_count)


