# -*- coding: utf-8 -*-

class ObjectActionKeysEnum(object):

    """Implementation of the 'ObjectActionKeys' enum.

    Filter by ObjectActionKey, which uniquely represents protection
          of an object. An object can be protected in multiple ways but atmost once
          for a given combination of ObjectActionKey. When specified, only snapshots
          matching given action keys are returned for corresponding object.


    Attributes:
        KVMWARE: TODO: type description here.
        KHYPERV: TODO: type description here.
        KVCD: TODO: type description here.
        KAZURE: TODO: type description here.
        KKVM: TODO: type description here.
        KAWS: TODO: type description here.
        KACROPOLIS: TODO: type description here.
        KGCP: TODO: type description here.
        KAWSNATIVE: TODO: type description here.
        KAWSS3: TODO: type description here.
        KAWSSNAPSHOTMANAGER: TODO: type description here.
        KRDSSNAPSHOTMANAGER: TODO: type description here.
        KAURORASNAPSHOTMANAGER: TODO: type description here.
        KAWSRDSPOSTGRESBACKUP: TODO: type description here.
        KAZURENATIVE: TODO: type description here.
        KAZURESQL: TODO: type description here.
        KAZURESNAPSHOTMANAGER: TODO: type description here.
        KPHYSICAL: TODO: type description here.
        KPHYSICALFILES: TODO: type description here.
        KISILON: TODO: type description here.
        KNETAPP: TODO: type description here.
        KGENERICNAS: TODO: type description here.
        KFLASHBLADE: TODO: type description here.
        KELASTIFILE: TODO: type description here.
        KGPFS: TODO: type description here.
        KPURE: TODO: type description here.
        KIBMFLASHSYSTEM: TODO: type description here.
        KNIMBLE: TODO: type description here.
        KSQL: TODO: type description here.
        KORACLE: TODO: type description here.
        KEXCHANGE: TODO: type description here.
        KAD: TODO: type description here.
        KVIEW: TODO: type description here.
        KREMOTEADAPTOR: TODO: type description here.
        KO365: TODO: type description here.
        KO365PUBLICFOLDERS: TODO: type description here.
        KO365TEAMS: TODO: type description here.
        KO365GROUP: TODO: type description here.
        KO365EXCHANGE: TODO: type description here.
        KO365ONEDRIVE: TODO: type description here.
        KO365SHAREPOINT: TODO: type description here.
        KKUBERNETES: TODO: type description here.
        KCASSANDRA: TODO: type description here.
        KMONGODB: TODO: type description here.
        KCOUCHBASE: TODO: type description here.
        KHDFS: TODO: type description here.
        KHIVE: TODO: type description here.
        KHBASE: TODO: type description here.
        KUDA: TODO: type description here.
        KSFDC: TODO: type description here.
"""

    K_VMWARE = 'kVMware'

    K_HYPERV = 'kHyperV'

    KVCD = 'kVCD'

    KAZURE = 'kAzure'

    KGCP = 'kGCP'

    KKVM = 'kKVM'

    KAWS = 'kAWS'

    KACROPOLIS = 'kAcropolis'

    KAWSNATIVE = 'kAWSNative'

    KAWSS3 = 'kAwsS3'

    KAWSSNAPSHOTMANAGER = 'kAWSSnapshotManager'

    KRDSSNAPSHOTMANAGER = 'kRDSSnapshotManager'

    KAURORASNAPSHOTMANAGER = 'kAuroraSnapshotManager'

    KAWSRDSPOSTGRESBACKUP = 'kAwsRDSPostgresBackup'

    KAZURENATIVE = 'kAzureNative'

    KAZURESQL = 'kAzureSQL'

    KAZURESNAPSHOTMANAGER = 'kAzureSnapshotManager'

    KPHYSICAL = 'kPhysical'

    KPHYSICALFILES = 'kPhysicalFiles'

    KGPFS = 'kGPFS'

    KELASTICFILE = 'kElastifile'

    KNETAPP = 'kNetapp'

    KGENERICNAS = 'kGenericNas'

    KISILON = 'kIsilon'

    KFLASHBLADE = 'kFlashBlade'

    KELASTIFILE = 'kElastifile'

    KPURE = 'kPure'

    KIBMFLASHSYSTEM = 'kIbmFlashSystem'

    KNIMBLE = 'kNimble'

    KSQL = 'kSQL'

    KORACLE = 'kOracle'

    KEXCHANGE = 'kExchange'

    KAD = 'kAD'

    KVIEW = 'kView'

    KREMOTEADAPTOR = 'kRemoteAdapter'

    KO365 = 'kO365'

    KO365PUBLICFOLDERS = 'kO365PublicFolders'

    KO365TEAMS = 'kO365Teams'

    KO365GROUP = 'kO365Group'

    KO365EXCHANGE = 'kO365Exchange'

    KO365ONEDRIVE = 'kO365OneDrive'

    KO365SHAREPOINT = 'kO365Sharepoint'

    KKUBERNETES = 'kKubernetes'

    KCASSANDRA = 'kCassandra'

    KMONGODB = 'kMongoDB'

    KCOUCHBASE = 'kCouchbase'

    KHDFS = 'kHdfs'

    KHIVE = 'kHive'

    KHBASE = 'kHBase'

    KUDA = 'kUDA'

    KSFDC = 'kSfdc'