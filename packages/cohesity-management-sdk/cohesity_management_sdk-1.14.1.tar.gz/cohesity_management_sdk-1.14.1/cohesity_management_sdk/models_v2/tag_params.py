# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.ebs_tag

class TagParams(object):

    """Implementation of the 'TagParams' model.

    Specifies the tag vectors used to exclude EBS volumes attached to
      EC2 instances at global and object level. Contains two vectors: exclusion and
      inclusion. E.g., {exclusionTagArray: [(K1, V1),  (K2, V2)], inclusionTagArray:
      [(K3, V3)]} => This will exclude a particular volume iff it has all the tags
      in exclusionTagArray((K1, V1),  (K2, V2)) and has none of the tags in the inclusionTagArray((K3,
      V3)).

    Attributes:
        exclusion_tag_array (list of EBSTag): Array which contains tags for AND exclusion. E.g., exclusionTagArray:
          [(K1, V1),  (K2, V2)] => This will exclude a particular volume iff it has
          both these tags.
        inclusion_tag_array (list of EBSTag): Array which contains tags for AND inclusion. E.g., inclusionTagArray:
          [(K3, V3),  (K4, V4)] => This will exclude a particular volume iff it does
          not have both these tags.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "exclusion_tag_array":'exclusionTagArray',
        "inclusion_tag_array":'inclusionTagArray'
    }

    def __init__(self,
                 exclusion_tag_array=None,
                 inclusion_tag_array=None):
        """Constructor for the TagParams class"""

        # Initialize members of the class
        self.exclusion_tag_array = exclusion_tag_array
        self.inclusion_tag_array = inclusion_tag_array


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
        exclusion_tag_array = None
        if dictionary.get("exclusionTagArray") is not None:
            exclusion_tag_array = list()
            for structure in dictionary.get('exclusionTagArray'):
                exclusion_tag_array.append(cohesity_management_sdk.models_v2.ebs_tag.EBSTag.from_dictionary(structure))
        inclusion_tag_array = None
        if dictionary.get("inclusionTagArray") is not None:
            inclusion_tag_array = list()
            for structure in dictionary.get('inclusionTagArray'):
                inclusion_tag_array.append(cohesity_management_sdk.models_v2.ebs_tag.EBSTag.from_dictionary(structure))

        # Return an object of this model
        return cls(exclusion_tag_array,
                   inclusion_tag_array)