# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

class SfdcOrg(object):

    """Implementation of the 'SfdcOrg' model.

    Specifies an Object containing information about a Salesforce Org.


    Attributes:

        org_id (string): String id of the organization to which Sfdc user
            belongs.
        total_sf_licenses (int): Contains the total number of salesforce user licenses in the
          organization.
        used_sf_licenses (int): Contains the number of user salesforce user licenses in the organization.

    """


    # Create a mapping from Model property names to API property names
    _names = {
        "org_id":'orgId',
        "total_sf_licenses":'totalSfLicenses',
        "used_sf_licenses":'usedSfLicenses'
    }
    def __init__(self,
                 org_id=None,
                 total_sf_licenses=None,
                 used_sf_licenses=None

            ):

        """Constructor for the SfdcOrg class"""

        # Initialize members of the class
        self.org_id = org_id
        self.total_sf_licenses = total_sf_licenses
        self.used_sf_licenses = used_sf_licenses

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
        org_id = dictionary.get('orgId')
        total_sf_licenses = dictionary.get('totalSfLicenses')
        used_sf_licenses = dictionary.get('usedSfLicenses')

        # Return an object of this model
        return cls(
            org_id,
            total_sf_licenses,
            used_sf_licenses
)