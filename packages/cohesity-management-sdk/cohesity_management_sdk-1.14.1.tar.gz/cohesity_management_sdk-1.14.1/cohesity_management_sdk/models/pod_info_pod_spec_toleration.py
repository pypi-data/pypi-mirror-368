# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class PodInfo_PodSpec_Toleration(object):

    """Implementation of the 'PodInfo_PodSpec_Toleration' model.

    Specifies an Object representing Universal Data Adapter.

    Attributes:
        effect (string): Effect indicates the taint effect to match. Empty
            all  means match taint effects. When specified, allowed values are
            NoSchedule, PreferNoSchedule and NoExecute
        key (string): Key is the taint key that the toleration applies to.
            Empty means match  all taint keys. If the key is empty, operator
            must be Exists; this combination means to match all values and all
            keys.
        operator (string): Operator represents a key's relationship to the
            value. Valid operators are Exists and Equal. Defaults to Equal.
            Exists is equivalent to wildcard for value, so that a pod can
            tolerate all taints of a particular category
        toleration_seconds (long|int): TolerationSeconds represents the period
            of time the toleration
            (which must be of effect NoExecute, otherwise this field is ignored)
            tolerates the taint. By default, it is not set, which means tolerate
            the taint forever (do not evict). Zero and negative values will be
            treated as 0 (evict immediately) by the system.
        value (string): Value is the taint value the toleration matches to.
          If the operator is Exists, the value should be empty, otherwise just a
          regular string.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "effect":'effect',
        "key":'key',
        "operator":'operator',
        "toleration_seconds":'tolerationSeconds',
        "value":'value'
    }

    def __init__(self,
                 effect=None,
                 key=None,
                 operator=None,
                 toleration_seconds=None,
                 value=None):
        """Constructor for the PodInfo_PodSpec_Toleration class"""

        # Initialize members of the class
        self.effect = effect
        self.key = key
        self.operator = operator
        self.toleration_seconds = toleration_seconds
        self.value = value


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
        effect =  dictionary.get('effect')
        key = dictionary.get('key')
        operator =dictionary.get('operator')
        toleration_seconds = dictionary.get('tolerationSeconds')
        value = dictionary.get('value')

        # Return an object of this model
        return cls(effect,
                   key,
                   operator,
                   toleration_seconds,
                   value)


