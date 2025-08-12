# -*- coding: utf-8 -*-

class AccessInfoListEnum(object):

    """Implementation of the 'AccessInfoList' enum.

    Specifies the File Access Type. Following documentation was\
    \ taken from MSDN.\nhttps://msdn.microsoft.com/en-us/library/Cc246802.aspx\n\
    \n'FileReadData' indicates the right to read data from the file or named\n\
    \  pipe.\n'FileWriteData' indicates the right to write data into the file\
    \ or named\n  pipe beyond the end of the file.\n'FileAppendData' indicates\
    \ the right to append data into the file or named\n  pipe.\n'FileReadEa'\
    \ indicates the right to read the extended attributes of the\n  file or\
    \ named pipe.\n'FileWriteEa' indicates the right to write or change the\
    \ extended\n  attributes to the file or named pipe.\n'FileExecute' indicates\
    \ the right to delete entries within a directory.\n'FileDeleteChild' indicates\
    \ the right to execute the file.\n'FileReadAttributes' indicates the right\
    \ to read the attributes of the\n  file.\n'FileWriteAttributes' indicates\
    \ the right to change the attributes of the\n  file.\n'Delete' indicates\
    \ the right to delete the file.\n'ReadControl' indicates the right to read\
    \ the security descriptor for the\n  file or named pipe.\n'WriteDac' indicates\
    \ the right to change the discretionary access control\n  list (DACL) in\
    \ the security descriptor for the file or named pipe. For\n  the DACL data\
    \ structure, see ACL in [MS-DTYP].\n'WriteOwner' indicates the right to\
    \ change the owner in the security\n  descriptor for the file or named pipe.\n\
    'Synchronize' is used only by SMB2 clients.\n'AccessSystemSecurity' indicates\
    \ the right to read or change the system\n  access control list (SACL) in\
    \ the security descriptor for the file or\n  named pipe. For the SACL data\
    \ structure, see ACL in [MS-DTYP].<42>\n'MaximumAllowed' indicates that\
    \ the client is requesting an open to the\n  file with the highest level\
    \ of access the client has on this file.\n  If no access is granted for\
    \ the client on this file, the server MUST\n  fail the open with STATUS_ACCESS_DENIED.\n\
    'GenericAll' indicates a request for all the access flags that are\n  previously\
    \ listed except MaximumAllowed and AccessSystemSecurity.\n'GenericExecute'\
    \ indicates a request for the following combination of\n  access flags listed\
    \ above:\n  FileReadAttributes| FileExecute| Synchronize| ReadControl.\n\
    'GenericWrite' indicates a request for the following combination of\n  access\
    \ flags listed above:\n  FileWriteData| FileAppendData| FileWriteAttributes|\
    \ FileWriteEa|\n  Synchronize| ReadControl.\n'GenericRead' indicates a request\
    \ for the following combination of\n  access flags listed above:\n  FileReadData|\
    \ FileReadAttributes| FileReadEa| Synchronize|\n  ReadControl."

    Attributes:
        FILEREADDATA: TODO: type description here.
        FILEWRITEDATA: TODO: type description here.
        FILEAPPENDDATA: TODO: type description here.
        FILEREADEA: TODO: type description here.
        FILEWRITEEA: TODO: type description here.
        FILEEXECUTE: TODO: type description here.
        FILEDELETECHILD: TODO: type description here.
        FILEREADATTRIBUTES: TODO: type description here.
        FILEWRITEATTRIBUTES: TODO: type description here.
        DELETE: TODO: type description here.
        READCONTROL: TODO: type description here.
        WRITEDAC: TODO: type description here.
        WRITEOWNER: TODO: type description here.
        SYNCHRONIZE: TODO: type description here.
        ACCESSSYSTEMSECURITY: TODO: type description here.
        MAXIMUMALLOWED: TODO: type description here.
        GENERICALL: TODO: type description here.
        GENERICEXECUTE: TODO: type description here.
        GENERICWRITE: TODO: type description here.
        GENERICREAD: TODO: type description here.

    """

    FILEREADDATA = 'FileReadData'

    FILEWRITEDATA = 'FileWriteData'

    FILEAPPENDDATA = 'FileAppendData'

    FILEREADEA = 'FileReadEa'

    FILEWRITEEA = 'FileWriteEa'

    FILEEXECUTE = 'FileExecute'

    FILEDELETECHILD = 'FileDeleteChild'

    FILEREADATTRIBUTES = 'FileReadAttributes'

    FILEWRITEATTRIBUTES = 'FileWriteAttributes'

    DELETE = 'Delete'

    READCONTROL = 'ReadControl'

    WRITEDAC = 'WriteDac'

    WRITEOWNER = 'WriteOwner'

    SYNCHRONIZE = 'Synchronize'

    ACCESSSYSTEMSECURITY = 'AccessSystemSecurity'

    MAXIMUMALLOWED = 'MaximumAllowed'

    GENERICALL = 'GenericAll'

    GENERICEXECUTE = 'GenericExecute'

    GENERICWRITE = 'GenericWrite'

    GENERICREAD = 'GenericRead'
