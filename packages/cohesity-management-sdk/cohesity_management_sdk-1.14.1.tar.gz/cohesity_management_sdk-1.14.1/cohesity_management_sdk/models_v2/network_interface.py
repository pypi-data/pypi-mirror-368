# -*- coding: utf-8 -*-


class NetworkInterface(object):

    """Implementation of the 'Network Interface' model.

    Specifies the parameters of a network interface.

    Attributes:
        name (string): Specifies the name of the network interface.
        mtype (Type10Enum): Specifies the type of the network interface.
        static_ip (string): Specifies the static IP of the network interface.
        virtual_ip (string): Specifies the virtual IP of the network
            interface.
        gateway (string): Specifies the gateway of the network interface.
        mtu (int): Specifies the MTU of the network interface.
        subnet (string): Specifies the subnet of the network interface.
        is_up (bool): Specifies whether or not the interface is up.
        group (string): Specifies the group to which this interface belongs.
        role (RoleEnum): Specifies the interface role.
        default_route (bool): Specifies whether or not this interface is the
            default route.
        bond_slave_names (list of string): Specifies the names of the bond
            slaves for this interface.
        bond_slave_slots (list of string): Specifies the slots of the bond
            slaves for this interface.
        bonding_mode (BondingModeEnum): Specifies the bonding mode of this
            interface.
        mac_address (string): Specifies the MAC address of this interface.
        is_connected (bool): Specifies whether or not this interface is
            connected.
        speed (SpeedEnum): Specifies the speed of this interface.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "mtype":'type',
        "static_ip":'staticIP',
        "virtual_ip":'virtualIP',
        "gateway":'gateway',
        "mtu":'mtu',
        "subnet":'subnet',
        "is_up":'isUp',
        "group":'group',
        "role":'role',
        "default_route":'defaultRoute',
        "bond_slave_names":'bondSlaveNames',
        "bond_slave_slots":'bondSlaveSlots',
        "bonding_mode":'bondingMode',
        "mac_address":'macAddress',
        "is_connected":'isConnected',
        "speed":'speed'
    }

    def __init__(self,
                 name=None,
                 mtype=None,
                 static_ip=None,
                 virtual_ip=None,
                 gateway=None,
                 mtu=None,
                 subnet=None,
                 is_up=None,
                 group=None,
                 role=None,
                 default_route=None,
                 bond_slave_names=None,
                 bond_slave_slots=None,
                 bonding_mode=None,
                 mac_address=None,
                 is_connected=None,
                 speed=None):
        """Constructor for the NetworkInterface class"""

        # Initialize members of the class
        self.name = name
        self.mtype = mtype
        self.static_ip = static_ip
        self.virtual_ip = virtual_ip
        self.gateway = gateway
        self.mtu = mtu
        self.subnet = subnet
        self.is_up = is_up
        self.group = group
        self.role = role
        self.default_route = default_route
        self.bond_slave_names = bond_slave_names
        self.bond_slave_slots = bond_slave_slots
        self.bonding_mode = bonding_mode
        self.mac_address = mac_address
        self.is_connected = is_connected
        self.speed = speed


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
        name = dictionary.get('name')
        mtype = dictionary.get('type')
        static_ip = dictionary.get('staticIP')
        virtual_ip = dictionary.get('virtualIP')
        gateway = dictionary.get('gateway')
        mtu = dictionary.get('mtu')
        subnet = dictionary.get('subnet')
        is_up = dictionary.get('isUp')
        group = dictionary.get('group')
        role = dictionary.get('role')
        default_route = dictionary.get('defaultRoute')
        bond_slave_names = dictionary.get('bondSlaveNames')
        bond_slave_slots = dictionary.get('bondSlaveSlots')
        bonding_mode = dictionary.get('bondingMode')
        mac_address = dictionary.get('macAddress')
        is_connected = dictionary.get('isConnected')
        speed = dictionary.get('speed')

        # Return an object of this model
        return cls(name,
                   mtype,
                   static_ip,
                   virtual_ip,
                   gateway,
                   mtu,
                   subnet,
                   is_up,
                   group,
                   role,
                   default_route,
                   bond_slave_names,
                   bond_slave_slots,
                   bonding_mode,
                   mac_address,
                   is_connected,
                   speed)


