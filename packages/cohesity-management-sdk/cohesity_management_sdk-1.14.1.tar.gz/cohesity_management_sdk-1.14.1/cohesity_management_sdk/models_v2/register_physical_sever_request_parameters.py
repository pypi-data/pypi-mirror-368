# -*- coding: utf-8 -*-


class RegisterPhysicalSeverRequestParameters(object):

    """Implementation of the 'Register physical sever request parameters.' model.

    Specifies parameters to register physical server.

    Attributes:
        applications (ApplicationsEnum): Specifies the list of applications to be registered with Physical
          Source.
        endpoint (string): Specifies the endpoint IPaddress, URL or hostname
            of the physical host.
        force_register (bool): The agent running on a physical host will fail
            the registration if it is already registered as part of another
            cluster. By setting this option to true, agent can be forced to
            register with the current cluster.
        host_type (HostTypeEnum): Specifies the type of host.
        physical_type (PhysicalTypeEnum): Specifies the type of physical server.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "applications":'applications',
        "endpoint":'endpoint',
        "force_register":'forceRegister',
        "host_type":'hostType',
        "physical_type":'physicalType'
    }

    def __init__(self,
                 applications=None,
                 endpoint=None,
                 force_register=None,
                 host_type=None,
                 physical_type=None):
        """Constructor for the RegisterPhysicalSeverRequestParameters class"""

        # Initialize members of the class
        self.applications = applications
        self.endpoint = endpoint
        self.force_register = force_register
        self.host_type = host_type
        self.physical_type = physical_type


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
        applications = dictionary.get('applications')
        endpoint = dictionary.get('endpoint')
        force_register = dictionary.get('forceRegister')
        host_type = dictionary.get('hostType')
        physical_type = dictionary.get('physicalType')


        # Return an object of this model
        return cls(applications,
                   endpoint,
                   force_register,
                   host_type,
                   physical_type)