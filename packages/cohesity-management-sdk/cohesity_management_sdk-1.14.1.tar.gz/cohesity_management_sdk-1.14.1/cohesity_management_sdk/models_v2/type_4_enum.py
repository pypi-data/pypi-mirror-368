# -*- coding: utf-8 -*-

class Type4Enum(object):

    """Implementation of the 'Type4' enum.

    Specifies the type of the Protection Group such as View or Puppeteer.
    'Puppeteer' refers to a Remote Adapter Group.
    Supported environment types such as 'View', 'SQL', 'VMware', etc.
    NOTE: 'Puppeteer' refers to Cohesity's Remote Adapter.
    'VMware' indicates the VMware Protection Source environment.
    'HyperV' indicates the HyperV Protection Source environment.
    'SQL' indicates the SQL Protection Source environment.
    'View' indicates the View Protection Source environment.
    'Puppeteer' indicates the Cohesity's Remote Adapter.
    'Physical' indicates the physical Protection Source environment.
    'Pure' indicates the Pure Storage Protection Source environment.
    'Nimble' indicates the Nimble Storage Protection Source environment.
    'Azure' indicates the Microsoft's Azure Protection Source environment.
    'Netapp' indicates the Netapp Protection Source environment.
    'Agent' indicates the Agent Protection Source environment.
    'GenericNas' indicates the Generic Network Attached Storage Protection
    Source environment.
    'Acropolis' indicates the Acropolis Protection Source environment.
    'PhsicalFiles' indicates the Physical Files Protection Source
    environment.
    'Isilon' indicates the Dell EMC's Isilon Protection Source environment.
    'GPFS' indicates IBM's GPFS Protection Source environment.
    'KVM' indicates the KVM Protection Source environment.
    'AWS' indicates the AWS Protection Source environment.
    'Exchange' indicates the Exchange Protection Source environment.
    'HyperVVSS' indicates the HyperV VSS Protection Source
    environment.
    'Oracle' indicates the Oracle Protection Source environment.
    'GCP' indicates the Google Cloud Platform Protection Source environment.
    'FlashBlade' indicates the Flash Blade Protection Source environment.
    'AWSNative' indicates the AWS Native Protection Source environment.
    'O365' indicates the Office 365 Protection Source environment.
    'O365Outlook' indicates Office 365 outlook Protection Source environment.
    'HyperFlex' indicates the Hyper Flex Protection Source environment.
    'GCPNative' indicates the GCP Native Protection Source environment.
    'AzureNative' indicates the Azure Native Protection Source environment.
    'Kubernetes' indicates a Kubernetes Protection Source environment.
    'Elastifile' indicates Elastifile Protection Source environment.
    'AD' indicates Active Directory Protection Source environment.

    Attributes:
        KVMWARE: TODO: type description here.
        KHYPERV: TODO: type description here.
        KVCD: TODO: type description here.
        KSQL: TODO: type description here.
        KVIEW: TODO: type description here.
        KREMOTEADAPTER: TODO: type description here.
        KPHYSICAL: TODO: type description here.
        KPURE: TODO: type description here.
        KIBMFLASHSYSTEM: TODO: type description here.
        KAZURE: TODO: type description here.
        KNETAPP: TODO: type description here.
        KGENERICNAS: TODO: type description here.
        KACROPOLIS: TODO: type description here.
        KISILON: TODO: type description here.
        KKVM: TODO: type description here.
        KAWS: TODO: type description here.
        KAWSNATIVE: TODO: type description here.
        KAWSS3: TODO: type description here.
        KAWSSNAPSHOTMANAGER: TODO: type description here.
        KRDSSNAPSHOTMANAGER: TODO: type description here.
        KAURORASNAPSHOTMANAGER: TODO: type description here.
        KAWSRDSPOSTGRESBACKUP: TODO: type description here.
        KAZURENATIVE: TODO: type description here.
        KAZURESQL: TODO: type description here.
        KAZURESNAPSHOTMANAGER: TODO: type description here.
        KEXCHANGE: TODO: type description here.
        KORACLE: TODO: type description here.
        KGCP: TODO: type description here.
        KFLASHBLADE: TODO: type description here.
        KO365: TODO: type description here.
        KHYPERFLEX: TODO: type description here.
        KAD: TODO: type description here.
        KGPFS: TODO: type description here.
        KKUBERNETES: TODO: type description here.
        KNIMBLE: TODO: type description here.
        KELASTIFILE: TODO: type description here.
        KCASSANDRA: TODO: type description here.
        KMONGODB: TODO: type description here.
        KCOUCHBASE: TODO: type description here.
        KHDFS: TODO: type description here.
        KHIVE: TODO: type description here.
        KHBASE: TODO: type description here.
        KUDA: TODO: type description here.
        KO365SHAREPOINT: TODO: type description here.
        KO365PUBLICFOLDERS: TODO: type description here.
        KO365TEAMS: TODO: type description here.
        KO365GROUP: TODO: type description here.
        KO365EXCHANGE: TODO: type description here.
        KO365ONEDRIVE: TODO: type description here.
        KSFDC: TODO: type description here.
        KEWSEXCHANGE: TODO: type description here.

    """

    K_VMWARE = 'kVMware'

    K_HYPERV = 'kHyperV'

    KVCD = 'kVCD'

    KSQL = 'kSQL'

    KVIEW = 'kView'

    KREMOTEADAPTER = 'kRemoteAdapter'

    KPHYSICAL = 'kPhysical'

    KPURE = 'kPure'

    KIBMFLASHSYSTEM = 'kIbmFlashSystem'

    KAZURE = 'kAzure'

    KNETAPP = 'kNetapp'

    KGENERICNAS = 'kGenericNas'

    KACROPOLIS = 'kAcropolis'

    KISILON = 'kIsilon'

    KKVM = 'kKVM'

    KAWS = 'kAWS'

    KAWSNATIVE = 'kAWSNative'

    KAWSS3 = 'kAwsS3'

    KAWSSNAPSHOTMANAGER = 'kAWSSnapshotManager'

    KRDSSNAPSHOTMANAGER = 'kRDSSnapshotManager'

    KAURORASNAPSHOTMANAGER = 'kAuroraSnapshotManager'

    KAWSRDSPOSTGRESBACKUP = 'kAwsRDSPostgresBackup'

    KAZURENATIVE = 'kAzureNative'

    KAZURESQL = 'kAzureSQL'

    KAZURESNAPSHOTMANAGER = 'kAzureSnapshotManager'

    KEXCHANGE = 'kExchange'

    KORACLE = 'kOracle'

    KGCP = 'kGCP'

    KFLASHBLADE = 'kFlashBlade'

    KO365 = 'kO365'

    KHYPERFLEX = 'kHyperFlex'

    KAD = 'kAD'

    KGPFS = 'kGPFS'

    KKUBERNETES = 'kKubernetes'

    KNIMBLE = 'kNimble'

    KELASTIFILE = 'kElastifile'

    KCASSANDRA = 'kCassandra'

    KMONGODB = 'kMongoDB'

    KCOUCHBASE = 'kCouchbase'

    KHDFS = 'kHdfs'

    KHIVE = 'kHive'

    KHBASE = 'kHBase'

    KUDA = 'kUDA'

    KO365SHAREPOINT = 'kO365Sharepoint'

    KO365PUBLICFOLDERS = 'kO365PublicFolders'

    KO365TEAMS = 'kO365Teams'

    KO365GROUP = 'kO365Group'

    KO365EXCHANGE = 'kO365Exchange'

    KO365ONEDRIVE = 'kO365OneDrive'

    KSFDC = 'kSfdc'

    KEWSEXCHANGE = 'kEwsExchange'