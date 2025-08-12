# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.view_1

class GetViewsResult(object):

    """Implementation of the 'Get Views Result.' model.

    Specifies the list of Views returned that matched the specified filter
    criteria.

    Attributes:
        views (list of View1): Array of Views. Specifies the list of Views
            returned in this response. The list is sorted by decreasing View
            ids.
        last_result (bool): If false, more Views are available to return. If
            the number of Views to return exceeds the number of Views
            specified in maxCount (default of 1000) of the original GET
            /public/views request, the first set of Views are returned and
            this field returns false. To get the next set of Views, in the
            next GET /public/views request send the last id from the previous
            viewList.
        count (long|int): Number of views returned. This will only be returned
            if ViewCountOnly is set in arguments. hidden: true

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "views":'views',
        "last_result":'lastResult',
        "count":'count'
    }

    def __init__(self,
                 views=None,
                 last_result=None,
                 count=None):
        """Constructor for the GetViewsResult class"""

        # Initialize members of the class
        self.views = views
        self.last_result = last_result
        self.count = count


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
        views = None
        if dictionary.get("views") is not None:
            views = list()
            for structure in dictionary.get('views'):
                views.append(cohesity_management_sdk.models_v2.view_1.View1.from_dictionary(structure))
        last_result = dictionary.get('lastResult')
        count = dictionary.get('count')

        # Return an object of this model
        return cls(views,
                   last_result,
                   count)


