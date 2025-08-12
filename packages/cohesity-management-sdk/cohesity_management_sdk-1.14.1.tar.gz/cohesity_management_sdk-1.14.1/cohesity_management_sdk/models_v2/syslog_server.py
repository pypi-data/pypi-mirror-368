# -*- coding: utf-8 -*-


class SyslogServer(object):

    """Implementation of the 'Syslog Server.' model.

    Specifies information about syslog server.

    Attributes:
        id (int): The id of the syslog server.
        ip (string): Specifies the IP address or hostname of the syslog
            server.
        port (int): Specifies the port where the syslog server listens.
        protocol (string): Specifies the protocol used to send the logs.
        name (string): Specifies a unique name for the syslog server on the
            Cluster.
        enabled (bool): Specifies whether to enable the syslog server on the
            Cluster.
        facility_list (list of string): Send enabled syslog facilities related
            logs to logging server.
        program_name_list (list of string): Send programes related logs to
            logging server.
        msg_pattern_list (list of string): Send logs including the msg
            patterns to logging server.
        raw_msg_pattern_list (list of string): Send logs including the msg
            patterns to logging server.
        is_tls_enabled (bool): Specify whether to enable tls support.
        ca_certificate (string): Syslog server CA certificate.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "ip":'ip',
        "port":'port',
        "protocol":'protocol',
        "name":'name',
        "enabled":'enabled',
        "facility_list":'facilityList',
        "program_name_list":'programNameList',
        "msg_pattern_list":'msgPatternList',
        "raw_msg_pattern_list":'rawMsgPatternList',
        "is_tls_enabled":'isTlsEnabled',
        "ca_certificate":'caCertificate'
    }

    def __init__(self,
                 id=None,
                 ip=None,
                 port=None,
                 protocol=None,
                 name=None,
                 enabled=None,
                 facility_list=None,
                 program_name_list=None,
                 msg_pattern_list=None,
                 raw_msg_pattern_list=None,
                 is_tls_enabled=None,
                 ca_certificate=None):
        """Constructor for the SyslogServer class"""

        # Initialize members of the class
        self.id = id
        self.ip = ip
        self.port = port
        self.protocol = protocol
        self.name = name
        self.enabled = enabled
        self.facility_list = facility_list
        self.program_name_list = program_name_list
        self.msg_pattern_list = msg_pattern_list
        self.raw_msg_pattern_list = raw_msg_pattern_list
        self.is_tls_enabled = is_tls_enabled
        self.ca_certificate = ca_certificate


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
        id = dictionary.get('id')
        ip = dictionary.get('ip')
        port = dictionary.get('port')
        protocol = dictionary.get('protocol')
        name = dictionary.get('name')
        enabled = dictionary.get('enabled')
        facility_list = dictionary.get('facilityList')
        program_name_list = dictionary.get('programNameList')
        msg_pattern_list = dictionary.get('msgPatternList')
        raw_msg_pattern_list = dictionary.get('rawMsgPatternList')
        is_tls_enabled = dictionary.get('isTlsEnabled')
        ca_certificate = dictionary.get('caCertificate')

        # Return an object of this model
        return cls(id,
                   ip,
                   port,
                   protocol,
                   name,
                   enabled,
                   facility_list,
                   program_name_list,
                   msg_pattern_list,
                   raw_msg_pattern_list,
                   is_tls_enabled,
                   ca_certificate)


