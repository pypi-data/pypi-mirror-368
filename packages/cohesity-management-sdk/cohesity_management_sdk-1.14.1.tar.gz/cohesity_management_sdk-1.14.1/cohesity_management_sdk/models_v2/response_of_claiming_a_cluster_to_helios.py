# -*- coding: utf-8 -*-


class ResponseOfClaimingAClusterToHelios(object):

    """Implementation of the 'Response of claiming a cluster to Helios.' model.

    Specifies the response of claiming a cluster to Helios.

    Attributes:
        cluster_id (long|int): Specifies the cluster id.
        cluster_incarnation_id (long|int): Specifies the cluster incarnation
            id.
        cluster_name (string): Specifies the cluster name.
        sf_account_id (string): Specifies the Salesforce account id used to
            claim the cluster.
        cluster_certificate (string): Specifies the Cluster certificate.
        cluster_private_key (string): Specifies the Cluster private key.
        passphrase (string): Specifies the passphrase (if used) to encrypt the
            cluster private key.
        cluster_ca_chain (string): Specifies the CA chain that is used to sign
            the Cluster certificate.
        helios_certificate (string): Specifies the Helios certificate that can
            be used to authenticate api calls made from Helios to cluster.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cluster_id":'clusterId',
        "cluster_incarnation_id":'clusterIncarnationId',
        "cluster_name":'clusterName',
        "sf_account_id":'sfAccountId',
        "cluster_certificate":'clusterCertificate',
        "cluster_private_key":'clusterPrivateKey',
        "passphrase":'passphrase',
        "cluster_ca_chain":'clusterCaChain',
        "helios_certificate":'heliosCertificate'
    }

    def __init__(self,
                 cluster_id=None,
                 cluster_incarnation_id=None,
                 cluster_name=None,
                 sf_account_id=None,
                 cluster_certificate=None,
                 cluster_private_key=None,
                 passphrase=None,
                 cluster_ca_chain=None,
                 helios_certificate=None):
        """Constructor for the ResponseOfClaimingAClusterToHelios class"""

        # Initialize members of the class
        self.cluster_id = cluster_id
        self.cluster_incarnation_id = cluster_incarnation_id
        self.cluster_name = cluster_name
        self.sf_account_id = sf_account_id
        self.cluster_certificate = cluster_certificate
        self.cluster_private_key = cluster_private_key
        self.passphrase = passphrase
        self.cluster_ca_chain = cluster_ca_chain
        self.helios_certificate = helios_certificate


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
        cluster_id = dictionary.get('clusterId')
        cluster_incarnation_id = dictionary.get('clusterIncarnationId')
        cluster_name = dictionary.get('clusterName')
        sf_account_id = dictionary.get('sfAccountId')
        cluster_certificate = dictionary.get('clusterCertificate')
        cluster_private_key = dictionary.get('clusterPrivateKey')
        passphrase = dictionary.get('passphrase')
        cluster_ca_chain = dictionary.get('clusterCaChain')
        helios_certificate = dictionary.get('heliosCertificate')

        # Return an object of this model
        return cls(cluster_id,
                   cluster_incarnation_id,
                   cluster_name,
                   sf_account_id,
                   cluster_certificate,
                   cluster_private_key,
                   passphrase,
                   cluster_ca_chain,
                   helios_certificate)


