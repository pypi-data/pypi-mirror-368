# -*- coding: utf-8 -*-


class CommonCsrRequestParams(object):

    """Implementation of the 'CommonCsrRequestParams' model.

    Specifies the parameters of a CSR.

    Attributes:
        organization (string): Specifies the organization attribute, which is
            part of the distinguished name definition. It is used to specify
            the name of the company.
        organization_unit (string): Specifies the organization unit attribute,
            which is part of the distinguished name definition. It is used to
            identify the specific department or business unit in the company
            that is owning the Cluster.
        country_code (string): Specifies the country attribute, which is part
            of the distinguished name definition. It is used to identify the
            country where the state is located. It is specified as two letter
            code defined by the ISO standard.
        state (string): Specifies the state attribute, which is part of the
            distinguished name definition. It is used to identify the state
            where the city is located.
        city (string): Specifies the locality attribute, which is part of the
            distinguished name definition. It is used to identify the city
            where the company is located or the Cluster is installed.
        key_type (KeyTypeEnum): Specifies the algorithm to be used to generate
            the key pair. RSA is the default value.
        key_size_bits (long|int): Specifies the size of the keys in bits. The
            default is 2048 bits for the RSA keys and 256 bits for ECDSA.
        common_name (string): Specifies the common name attribute, which is
            part of the distinguished name definition. Common name is used to
            specify a context for the certificate, for example, the name of
            the Cluster to which the certificate is to be assigned. Default
            value is the name of the Cluster.
        dns_names (list of string): Specifies an alternative subject name
            component to be included in the certificate. It is used to
            identify the ways the Cluster will be accessed. It is given as a
            comma separated list of FQDNs. The default value is the Cluster's
            VIP hostname.
        host_ips (list of string): Specifies an alternative subject name
            component to be included in the certificate. It is used to
            identify the ways the Cluster will be accessed. It is given as a
            comma separated list of IP addresses. The default value is the
            Cluster's VIP addresses.
        email_address (string): Specifies an alternative subject name
            component to be included in the certificate. Format is a standard
            e-mail address, for example joe@company.com.
        service_name (ServiceNameEnum): Specifies the Cohesity service name
            for which the CSR is generated. Default service name is iris.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "organization":'organization',
        "organization_unit":'organizationUnit',
        "country_code":'countryCode',
        "state":'state',
        "city":'city',
        "key_type":'keyType',
        "key_size_bits":'keySizeBits',
        "common_name":'commonName',
        "dns_names":'dnsNames',
        "host_ips":'hostIps',
        "email_address":'emailAddress',
        "service_name":'serviceName'
    }

    def __init__(self,
                 organization=None,
                 organization_unit=None,
                 country_code=None,
                 state=None,
                 city=None,
                 key_type='rsa',
                 key_size_bits=None,
                 common_name=None,
                 dns_names=None,
                 host_ips=None,
                 email_address=None,
                 service_name='iris'):
        """Constructor for the CommonCsrRequestParams class"""

        # Initialize members of the class
        self.organization = organization
        self.organization_unit = organization_unit
        self.country_code = country_code
        self.state = state
        self.city = city
        self.key_type = key_type
        self.key_size_bits = key_size_bits
        self.common_name = common_name
        self.dns_names = dns_names
        self.host_ips = host_ips
        self.email_address = email_address
        self.service_name = service_name


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
        organization = dictionary.get('organization')
        organization_unit = dictionary.get('organizationUnit')
        country_code = dictionary.get('countryCode')
        state = dictionary.get('state')
        city = dictionary.get('city')
        key_type = dictionary.get("keyType") if dictionary.get("keyType") else 'rsa'
        key_size_bits = dictionary.get('keySizeBits')
        common_name = dictionary.get('commonName')
        dns_names = dictionary.get('dnsNames')
        host_ips = dictionary.get('hostIps')
        email_address = dictionary.get('emailAddress')
        service_name = dictionary.get("serviceName") if dictionary.get("serviceName") else 'iris'

        # Return an object of this model
        return cls(organization,
                   organization_unit,
                   country_code,
                   state,
                   city,
                   key_type,
                   key_size_bits,
                   common_name,
                   dns_names,
                   host_ips,
                   email_address,
                   service_name)


