import os
import sys
import re
import concurrent.futures
import time
import fnmatch

# Path to the main package file
root_pkg_path = r"Logical\Libraries\Package.pkg"

# Hardcoded list of obsolete libraries with reasons
obsolete_dict = {
    "AsARCNET": "Supports SG3 only",
    "AsSGCIO": "Supports SGC only",
    "AsTPU": "Supports SG3 only",
    "C220man": "Supports SG3 only",
    "CANIO": "Supports SG3 only",
    "DM_Lib": "Supports SG3 and SGC only",
    "FDD_lib": "Supports SG3 and SGC only",
    "IF361": "Supports SG3 only",
    "IO_lib": "Supports SG3 only",
    "IOConfig": "Supports SG3 only",
    "IOCtrl": "Supports SG3 only",
    "PB_lib": "Supports SG3 only",
    "PBIXMAN": "Supports SG3 only",
    "RIO_lib": "Supports SG3 only",
    "SPSIOMAN": "Supports SG3 only",
    "TCPIPMGR": "Supports SG3 only",
    "AsMc": "Supports SG3 only",
    "AsNetX": "Supports SGC only",
    "Logging": "Has been replaced by library AsArProf",
    "AsIMA": "INA2000 based",
    "Commserv": "INA2000 based",
    "INAclnt": "INA2000 based",
    "AsKey": "Only supports Dallas dongles, which are no longer available for current AR versions",
    "AsSLIP": "SLIP is an obsolete protocol",
    "AsArLog": "Has been replaced by library ArEventLog",
    "AsSound": "Supports PP500 only. PP500 is discontinued",
    "AsErrTxt": "Reason for discontinuation not indicated",
    "AsPlkSup": "Supports SG3 only",
    "IF661": "Supports SG3 only",
    "ppdpr": "Only required for communication with SG3 PP",
    "printer": "Reason for discontinuation not indicated",
    "Spooler": "Only supports the 2005 hardware system",
    "SRAM200x": "Reason for discontinuation not indicated",
    "AsString": "Has been replaced by AsBrStr for IEC programming, libc for ANSI C programming",
    "AsMath": "Has been replaced by AsBrMath for IEC programming, libc for ANSI C programming",
    "AsCisMan": "Reason for discontinuation not indicated",
    "CONVERT": "Has been replaced by AsIecCon",
    "AsPciExt": "Reason for discontinuation not indicated",
    "AsWStr": "Has been replaced by AsBrWStr",
    "NET2000": "B&R proprietary protocol only available for RS485 and RS232 (CAN only for SG3)",
    "FB_lib": "The library is used to support the PROFIBUS DB master (X20IF1061) and PROFIBUS DP slave (X20IF1065) as well as LS050 and LS166.6, which are all marked as obsolete",
    "DPMaster": "The library is used to support the PROFIBUS DB master (X20IF1061) and PROFIBUS DP slave (X20IF1065) as well as LS050 and LS166.6, which are all marked as obsolete",
    "AsPROFIBUS": "The library is used to support the PROFIBUS DB master (X20IF1061) and PROFIBUS DP slave (X20IF1065) as well as LS050 and LS166.6, which are all marked as obsolete",
    "AsSafety": "The library is only for legacy safety. Legacy safety is not supported in AS 6 / AR 6",
    "LoopCont": "This library has been replaced by the mapp Temperature and mapp Control Tools libraries",
    "AsHydCon": "This library has been replaced by the mapp Hydraulics and mapp Control Tools libraries",
    "ArAutoId": "Reason for discontinuation not indicated",
    "MpWebXs": "The library is not supported in Automation Studio 6.1. Recommended replacement: mapp Cockpit",
    "MTTension": "The library is not supported in Automation Studio 6.1",
    "ArPubSubD": "Recommended replacement: FxPubSubD",
    "MpAlarm": "Recommended replacement: MpAlarmX",
    "MpUser": "Recommended replacement: MpUserX",
    "MTIdent": "Recommended replacement: mapp Control Tools"
}

# Libraries that must be deleted and re-added with a version >= 6.0
reinstall_libraries = {
    "MTAdvanced": "Must be deleted and re-added with a version >= 6.0",
    "MTHydGen": "Must be deleted and re-added with a version >= 6.0",
    "MTHydPump": "Must be deleted and re-added with a version >= 6.0",
    "MTHydValve": "Must be deleted and re-added with a version >= 6.0",
    "MTPrintHW": "Must be deleted and re-added with a version >= 6.0",
    "MTSystem": "Must be deleted and re-added with a version >= 6.0",
    "MTTemp": "Must be deleted and re-added with a version >= 6.0",
    "MTTypes": "Must be deleted and re-added with a version >= 6.0",
    "MTWinder": "Must be deleted and re-added with a version >= 6.0"
}

# Hardcoded list of obsolete function blocks with reasons
obsolete_function_blocks = {
    "AsIOAccWriteReg": "Supports SGC only",
    "AsIOAccReadReg": "Supports SGC only",
    "ARwinEthWinInfo": "Supports ARwin only",
    "ARwinWindowsInfo": "Supports ARwin only",
    "ZYKVLenable": "Supports SG3 only",
    "EXCInfo": "Supports SG3 only",
    "PMemGet": "Supports SG3 only",
    "PMemPut": "Supports SG3 only",
    "PMemSize": "Supports SG3 only",
    "SysconfInfo": "Has been replaced by function blocks / functions from library AsARCfg",
    "SysconfSet": "Has been replaced by function blocks / functions from library AsARCfg",
    "BatteryInfo": "Has been replaced by HwGetBatteryInfo() from library AsHw",
    "MEMInfo": "Has been replaced by MEMxInfo()",
    "HWInfo": "Has been replaced by function blocks / functions from library AsIODiag",
    "CANnode": "Supports SG3 only",
    "CANxnode": "Supports SG3 only",
    "GetNdNr": "Supports SG3 only",
    "SetNdNr": "Supports SG3 only",
    "ArUserExport": "Has been replaced by ArUserExportEx()",
    "ArUserImport": "Has been replaced by ArUserImportEx()",
    "ETHnode": "Supports SG3 only",
    "CfgSetBroadcastAddr": "Only works in AR versions < 4.00",
    "CfgSetSntpServer": "Has been replaced by CfgSetNtpServer()",
    "CfgSetSntpClient": "Has been replaced by CfgSetNtpClient()",
    "CfgGetSntpcData": "Has been replaced by CfgGetNtpcData()",
    "CfgGetSntpsData": "Has been replaced by CfgGetNtpsData()",
    "MpAlarmXConfigMapping": "No longer supported since version 6.0. Use MpComConfigManager or MpComConfigBasic/Advanced instead.",
    "MpAlarmXConfigAlarm": "No longer supported since version 6.0. Use MpComConfigManager or MpComConfigBasic/Advanced instead.",
    "MpAuditTrailConfig": "No longer supported since version 6.0. Use MpComConfigManager instead.",
    "MpDataRecorderConfig": "No longer supported since version 6.0. Use MpComConfigManager instead.",
    "MpUserXLoginConfig": "No longer supported since version 6.0. Use MpComConfigManager instead.",
    "MpUserXMappingConfig": "No longer supported since version 6.0. Use MpComConfigManager instead.",
    "MpUserXServerConfig": "No longer supported since version 6.0. Use MpComConfigManager instead.",
    "MpBackupCoreConfig": "No longer supported since version 6.0. Use MpComConfigManager instead.",
    "MpSequenceAxisConfig": "No longer supported since version 6.0. Use MpComConfigManager instead.",
    "MpSequenceCommandConfig": "No longer supported since version 6.0. Use MpComConfigManager instead.",
    "MpSequenceActuatorConfig": "No longer supported since version 6.0. Use MpComConfigManager instead.",
    "MpFileManagerConfig": "No longer supported since version 6.0. Use MpComConfigManager instead."
     # Add more function blocks as needed
}

# Hardcoded list of obsolete functions with reasons
obsolete_functions = {
    "SW_gettime": "Supports SG3 only",
    "SW_settime": "Supports SG3 only",
    "PV_ident": "Supports SG3 only",
    "PV_getadr": "Supports SG3 only",
    "PV_setval": "Supports SG3 only",
    "PV_getval": "Supports SG3 only",
    "PV_xsetval": "Supports SG3 only",
    "PV_xgetval": "Supports SG3 only",
    "PV_info": "Supports SG3 only",
    "PV_list": "Supports SG3 only",
    "MEM_alloc": "Supports SG3 only",
    "MEM_free": "Supports SG3 only",
    "ST_resume": "Supports SG3 only",
    "ST_suspend": "Supports SG3 only",
    "ERR_read": "Has been replaced by function blocks / functions from library ArEventLog",
    "ERRxread": "Has been replaced by function blocks / functions from library ArEventLog",
    "AVT_create": "Supports SG3 only",      # All functions starting with AVT_
    "AVT_cancel": "Supports SG3 only",     # All functions starting with AVT_
    "AVT_ident": "Supports SG3 only",      # All functions starting with AVT_
    "AVT_attach": "Supports SG3 only",     # All functions starting with AVT_
    "AVT_release": "Supports SG3 only",    # All functions starting with AVT_
    "AVT_info": "Supports SG3 only",       # All functions starting with AVT_
    "DA_create": "Supports SG3 only",   # All functions starting with DA_
    "DA_ident": "Supports SG3 only",   # All functions starting with DA_
    "DA_write": "Supports SG3 only",   # All functions starting with DA_
    "DA_read": "Supports SG3 only",   # All functions starting with DA_
    "DA_burn": "Supports SG3 only",   # All functions starting with DA_
    "DA_fix": "Supports SG3 only",   # All functions starting with DA_
    "DA_info": "Supports SG3 only",   # All functions starting with DA_
    "DA_delete": "Supports SG3 only",   # All functions starting with DA_
    "DA_store": "Supports SG3 only",   # All functions starting with DA_
    "DA_copy": "Supports SG3 only",   # All functions starting with DA_
    "DIS_clr": "Supports SG3 only",  # All functions starting with DIS_
    "DIS_chr": "Supports SG3 only",  # All functions starting with DIS_
    "DIS_str": "Supports SG3 only",  # All functions starting with DIS_
    "KEY_enadis": "Supports SG3 only",  # All functions starting with KEY_
    "KEY_read": "Supports SG3 only",  # All functions starting with KEY_
    "SM_create": "Supports SG3 only",   # All functions starting with SM_
    "SM_ident": "Supports SG3 only",   # All functions starting with SM_
    "SM_delete": "Supports SG3 only",   # All functions starting with SM_
    "SM_attach": "Supports SG3 only",   # All functions starting with SM_
    "SM_release": "Supports SG3 only",   # All functions starting with SM_
    "SYS_info": "Supports SG3 only",
    "SYSxinfo": "Supports SG3 only",
    "SYS_battery": "Supports SG3 only",
    "FORCE_info": "Supports SG3 only",
    "UT_ident": "Supports SG3 only",   # All functions starting with UT_
    "UT_suspend": "Supports SG3 only",   # All functions starting with UT_
    "UT_resume": "Supports SG3 only",   # All functions starting with UT_
    "UT_sleep": "Supports SG3 only",   # All functions starting with UT_
    "UT_exit": "Supports SG3 only",   # All functions starting with UT_
    "UT_sendmsg": "Supports SG3 only",   # All functions starting with UT_
    "UT_recmsg": "Supports SG3 only",   # All functions starting with UT_
    "UT_freemsg": "Supports SG3 only",   # All functions starting with UT_
     # Add more functions as needed
}

unsupported_hardware = {
    "2003/2005/EC20 - No longer supported with AS 6.x": [
        "3AI350.6", "3AI375.6", "3AI775.6", "3AI780.6", "3AI961.6", "3AM050.6",
        "3AM051.6", "3AM055.6", "3AM374.6", "3AO350.6", "3AO360.60-1",
        "3AO775.6", "3AT350.6", "3AT450.6", "3AT652.6", "3AT660.6", "3BM150.9",
        "3BP150.4", "3BP151.4", "3BP152.4", "3BP155.4", "3CP260.60-1",
        "3CP320.60-1", "3CP340.60-1", "3CP340.60-2", "3CP360.60-1", "3CP360.60-2",
        "3CP380.60-1", "3CP382.60-1", "3DI175.6", "3DI450.60-9", "3DI475.6",
        "3DI476.6", "3DI477.6", "3DI486.6", "3DI575.6", "3DI695.6", "3DI875.6",
        "3DM455.60-2", "3DM476.6", "3DM486.6", "3DO479.6", "3DO480.6", "3DO486.6",
        "3DO487.6", "3DO650.6", "3DO690.6", "3DO750.6", "3DO760.6", "3EX282.6",
        "3EX350.6", "3EX450.26-1", "3EX450.66-1", "3EX450.66-2", "3EX450.71-1",
        "3EX450.72-1", "3EX450.76-1", "3EX450.77-1", "3IF050.6", "3IF060.6",
        "3IF260.60-1", "3IF613.9", "3IF621.9", "3IF622.9", "3IF648.95", "3IF661.9",
        "3IF671.9", "3IF672.9", "3IF681.86", "3IF681.95", "3IF681.96", "3IF686.9",
        "3IF722.9", "3IF761.9", "3IF762.9", "3IF762.9-1", "3IF766.9", "3IF771.9",
        "3IF772.9", "3IF779.9", "3IF781.9", "3IF782.9", "3IF782.9-1", "3IF786.9",
        "3IF786.9-1", "3IF787.9", "3IF787.9-1", "3IF789.9", "3IF789.9-1",
        "3IF789.9-11", "3IF791.9", "3IF792.9", "3IF797.9", "3IF797.9-1",
        "3IF7E3.9", "3IP161.60-1", "3NC150.6", "3NC352.6", "3NW150.60-1",
        "3PS465.9", "3PS477.9", "3PS692.9", "3PS694.9", "3PS792.9", "3PS794.9",
        "3UM161.6"
    ],
    "PANELWARE - No longer supported with AS 6.x": [
        "4B1270.00-390", "4B1270.00-490", "4C1000.01-010", "4C1000.01-510",
        "4C1000.02-510", "4C1300.01-510", "4C1300.02-510", "4D1022.00-090",
        "4D1042.00-090", "4D1044.00-090", "4D1084.00-090", "4D1164.00-090",
        "4D1164.00-590", "4D1165.00-490", "4D1166.00-490", "4D1167.00-490",
        "4D2022.00-090", "4D2024.00-090"
    ],
    "PP15/21/35/41/45/65 - No longer supported with AS 6.x": [
        "4EX101.00", "4EX101.01", "4IF370.7"
    ],
    "MP40/50/100/200 - No longer supported with AS 6.x": [
        "4MP181.0843-03", "4MP251.0571-12", "4MP281.0571-12", "4MP281.0843-13"
    ],
    "PP15/21/35/41/45/65 - No longer supported with AS 6.x": [
        "4P0420.00-490", "4P3040.00-490", "4PP015.0420-01", "4PP015.0420-36",
        "4PP015.C420-01", "4PP015.C420-36", "4PP015.E420-01", "4PP015.E420-101",
        "4PP015.E420-36", "4PP035.0300-01", "4PP035.0300-36", "4PP035.E300-01",
        "4PP035.E300-136", "4PP035.E300-36", "4PP045.0571-042", "4PP045.0571-062",
        "4PP045.0571-L42", "4PP045.IF10-1", "4PP045.IF23-1", "4PP045.IF24-1",
        "4PP045.IF33-1", "4PP065.0351-P74", "4PP065.0351-X74", "4PP065.0571-P74",
        "4PP065.0571-P74F", "4PP065.0571-X74", "4PP065.0571-X74F", "4PP065.1043-K01",
        "4PP065.IF10-1", "4PP065.IF23-1", "4PP065.IF24-1", "4PP065.IF33-1"
    ],
    "PP200/300/400/500 - No longer supported with AS 6.x": [
        "4PP320.0571-01", "4PP320.0571-35", "4PP320.1043-31", "4PP320.1505-31",
        "4PP351.0571-01", "4PP351.0571-35", "4PP352.0571-35", "4PP381.1043-31",
        "4PP420.0571-45", "4PP420.0571-65", "4PP420.0571-75", "4PP420.0571-85",
        "4PP420.0571-A5", "4PP420.0571-B5", "4PP420.0573-75", "4PP420.1043-75",
        "4PP420.1043-B5", "4PP420.1505-75", "4PP420.1505-B5", "4PP451.0571-45",
        "4PP451.0571-65", "4PP451.0571-75", "4PP451.0571-85", "4PP451.0571-B5",
        "4PP451.1043-75", "4PP451.1043-B5", "4PP452.0571-45", "4PP452.0571-65",
        "4PP452.0571-75", "4PP452.0571-B5", "4PP452.1043-75", "4PP480.1043-75",
        "4PP480.1505-75", "4PP480.1505-B5", "4PP481.1043-75", "4PP481.1043-B5",
        "4PP481.1505-75", "4PP482.1043-75", "5PP320.0573-39", "5PP320.0573-3B",
        "5PP320.1043-39", "5PP320.1214-39", "5PP320.1505-39", "5PP320.1505-3B",
        "5PP520.0573-00", "5PP520.0573-01", "5PP520.0573-B00", "5PP520.0573-B01",
        "5PP520.0573-B10", "5PP520.0573-B11", "5PP520.0702-00", "5PP520.0702-B00",
        "5PP520.0702-B10", "5PP520.1043-00", "5PP520.1043-B00", "5PP520.1043-B10",
        "5PP520.1043-B50", "5PP520.1214-00", "5PP520.1505-00", "5PP520.1505-B00",
        "5PP520.1505-B10", "5PP520.1505-B50", "5PP520.1505-B55", "5PP520.1505-B60",
        "5PP520.1505-B65", "5PP551.0573-00", "5PP552.0573-00", "5PP580.1043-00",
        "5PP580.1505-00", "5PP581.1043-00", "5PP581.1505-00", "5PP582.1043-00",
        "5PP5CP.US15-00", "5PP5CP.US15-01", "5PP5CP.US15-02", "5PP5IF.CETH-00",
        "5PP5IF.CHDA-00", "5PP5IF.FCAN-00", "5PP5IF.FETH-00", "5PP5IF.FPLM-00",
        "5PP5IF.FX2X-00", "5PP5IF.FXCM-00", "5PP5IO.GMAC-00", "5PP5IO.GNAC-00"
    ],
    "C30/50/70/80 - No longer supported with AS 6.x": [
        "4PPC70.0573-20B", "4PPC70.0573-20W", "4PPC70.0573-21B", "4PPC70.0573-21W",
        "4PPC70.0573-22B", "4PPC70.0573-22W", "4PPC70.0573-23B", "4PPC70.0573-23W",
        "4PPC70.057L-20B", "4PPC70.057L-20W", "4PPC70.057L-21B", "4PPC70.057L-21W",
        "4PPC70.057L-22B", "4PPC70.057L-22W", "4PPC70.057L-23B", "4PPC70.057L-23W",
        "4PPC70.0702-20B", "4PPC70.0702-20W", "4PPC70.0702-21B", "4PPC70.0702-21W",
        "4PPC70.0702-22B", "4PPC70.0702-22W", "4PPC70.0702-23B", "4PPC70.0702-23W",
        "4PPC70.070M-20B", "4PPC70.070M-20W", "4PPC70.070M-21B", "4PPC70.070M-21W",
        "4PPC70.070M-22B", "4PPC70.070M-22W", "4PPC70.070M-23B", "4PPC70.070M-23W",
        "4PPC70.101G-20B", "4PPC70.101G-20W", "4PPC70.101G-21B", "4PPC70.101G-21W",
        "4PPC70.101G-22B", "4PPC70.101G-22W", "4PPC70.101G-23B", "4PPC70.101G-23W",
        "4PPC70.101N-20B", "4PPC70.101N-20W", "4PPC70.101N-21B", "4PPC70.101N-21W",
        "4PPC70.101N-22B", "4PPC70.101N-22W", "4PPC70.101N-23B", "4PPC70.101N-23W"
    ],
    "PP15/21/35/41/45/65 - No longer supported with AS 6.x": [
        "4PW035.E300-01", "4PW035.E300-02"
    ],
    "Keypad modules - No longer supported with AS 6.x": [
        "4XP0000.00-K38"
    ],
    "APC510/620/810/820 - No longer supported with AS 6.x": [
        "5AC600.485I-00", "5AC600.CANI-00", "5AC600.HCFS-00", "5AC600.SDL0-00",
        "5AC600.SRAM-00", "5AC600.UPSI-00", "5AC800.CON1-00", "5AC800.CON2-00",
        "5AC800.EXT1-00", "5AC800.EXT2-00", "5AC800.EXT2-01", "5AC800.EXT3-00",
        "5AC800.EXT3-01", "5AC800.EXT3-02", "5AC800.EXT3-03", "5AC800.EXT3-04",
        "5AC800.EXT3-05", "5AC801.SDL0-00", "5AC803.BC01-00", "5AC803.BX01-00",
        "5AC803.BX01-01", "5AC803.BX02-00", "5PC800.B945-00", "5PC800.B945-01",
        "5PC800.B945-02", "5PC800.B945-03", "5PC800.B945-04", "5PC800.B945-05",
        "5PC800.B945-10", "5PC800.B945-11", "5PC800.B945-12", "5PC800.B945-13",
        "5PC800.B945-14", "5PC800.BM45-00", "5PC800.BM45-01", "5PC800.CCAX-00",
        "5PC810.BX01-00", "5PC810.BX01-01", "5PC810.BX02-00", "5PC810.BX02-01",
        "5PC810.BX03-00", "5PC810.BX05-00", "5PC810.BX05-01", "5PC810.BX05-02",
        "5PC810.SX01-00", "5PC810.SX02-00", "5PC810.SX03-00", "5PC810.SX05-00",
        "5PC820.1505-00", "5PC820.1906-00", "5PC820.SX01-00", "5PC820.SX01-01"
    ],
    "APC/PPC910 TS77 - No longer supported with AS 6.x": [
        "5PC900.TS77-00", "5PC900.TS77-01", "5PC900.TS77-02", "5PC900.TS77-03",
        "5PC900.TS77-04", "5PC900.TS77-05", "5PC900.TS77-06", "5PC900.TS77-07",
        "5PC900.TS77-08", "5PC900.TS77-09", "5PC900.TS77-10", "5PC901.TS77-00",
        "5PC901.TS77-01", "5PC901.TS77-02", "5PC901.TS77-03", "5PC901.TS77-04",
        "5PC901.TS77-05", "5PC901.TS77-06", "5PC901.TS77-07", "5PC901.TS77-08",
        "5PC901.TS77-09", "5PC901.TS77-10", "5ACPCC.MPL0-00"
    ],
    "AP800/920/950/980 - No longer supported with AS 6.x": [
        "5AP820.1505-00", "5AP880.1505-00", "5AP920.1043-01", "5AP920.1214-01",
        "5AP920.1505-01", "5AP920.1706-01", "5AP920.1906-01", "5AP920.2138-01",
        "5AP951.1043-01", "5AP951.1505-01", "5AP952.1043-01", "5AP980.1043-01",
        "5AP980.1505-01", "5AP981.1043-01", "5AP981.1505-01", "5AP982.1043-01",
        "5AP923.1215-I00", "5AP923.1505-I00"
    ],
    "AP9*D* - No longer supported with AS 6.x": [
        "5AP92D.1505-00", "5AP92D.1505-01", "5AP92D.1906-00", "5AP92D.1906-01",
        "5AP93D.156B-K06", "5AP93D.185B-00", "5AP93D.185B-01", "5AP93D.185B-B60",
        "5AP93D.215C-00", "5AP93D.215C-01", "5AP93D.240C-00", "5AP93D.240C-01",
        "5AP93D.240C-B60", "5AP99D.156B-B60", "5AP99D.185B-00", "5AP99D.185B-01",
        "5AP99D.185B-B60", "5AP99D.185B-K02", "5AP99D.215C-00", "5AP99D.215C-01",
        "5AP99D.215C-B60", "5AP99D.215I-00", "5AP99D.215I-01", "5AP99D.240C-00",
        "5AP99D.240C-01", "5DLSD3.1003-00", "5DLSDL.1002-00"
    ],
    "APC2100/PPC2100 - No longer supported with AS 6.x": [
        "5APC2100.BY01-000", "5APC2100.BY11-000", "5APC2100.BY22-000", "5APC2100.BY34-000",
        "5APC2100.BY44-000", "5APC2100.BY48-000", "5PPC2100.BY01-000", "5PPC2100.BY01-001",
        "5PPC2100.BY01-002", "5PPC2100.BY11-000", "5PPC2100.BY11-001", "5PPC2100.BY11-002",
        "5PPC2100.BY22-000", "5PPC2100.BY22-001", "5PPC2100.BY22-002", "5PPC2100.BY34-000",
        "5PPC2100.BY34-001", "5PPC2100.BY34-002", "5PPC2100.BY44-000", "5PPC2100.BY44-001",
        "5PPC2100.BY44-002", "5PPC2100.BY48-000", "5PPC2100.BY48-002"
    ],
    "LS050 - No longer supported with AS 6.x": [
        "5LS050.61-1", "5LS050.66-1", "5LS050.66-2", "5LS050.71-1",
        "5LS050.72-1", "5LS050.76-1", "5LS050.77-1"
    ],
    "MP40/50/100/200 - No longer supported with AS 6.x": [
        "5MP040.0381-01", "5MP040.0381-02", "5MP050.0653-01", "5MP050.0653-02",
        "5MP050.0653-03", "5MP050.0653-04"
    ],
    "PPC300/700/800 - No longer supported with AS 6.x": [
        "5PC310.L800-00", "5PC310.L800-01", "5PC720.1043-00", "5PC720.1043-01",
        "5PC720.1214-00", "5PC720.1214-01", "5PC720.1505-00", "5PC720.1505-01",
        "5PC720.1505-02", "5PC720.1706-00", "5PC720.1906-00", "5PC781.1043-00",
        "5PC781.1505-00", "5PC782.1043-00"
    ],
    "APC510/620/810/820 - No longer supported with AS 6.x": [
        "5PC510.SX01-00", "5PC511.SX01-00", "5PC600.E855-00", "5PC600.E855-01",
        "5PC600.E855-02", "5PC600.E855-03", "5PC600.E855-04", "5PC600.E855-05",
        "5PC600.E8xx-00.1", "5PC600.E8xx-00.2", "5PC600.E8xx-00.3", "5PC600.E8xx-00.4",
        "5PC600.SE00-00", "5PC600.SE00-01", "5PC600.SE00-02", "5PC600.SF03-00",
        "5PC600.SX01-00", "5PC600.SX02-00", "5PC600.SX02-01", "5PC600.SX05-00",
        "5PC600.SX05-01", "5PC600.X855-00", "5PC600.X855-01", "5PC600.X855-02",
        "5PC600.X855-03", "5PC600.X855-04", "5PC600.X855-05", "5PC600.X8xx-xx",
        "5PC600.X945-00"
    ],
    "MP7x00 - No longer supported with AS 6.x": [
        "5MP7120.034F-000", "5MP7121.034F-000", "5MP7140.070N-000",
        "5MP7150.101E-000", "5MP7151.101E-000"
    ],
    "APx000 - No longer supported with AS 6.x": [
        "5DLSD3.1000-00", "5DLSD3.1001-00", "5ACCKPS1.215C-000", "5ACCLI01.SDL3-000"
    ],
    "APC/PPC910 - No longer supported with AS 6.x": [
        "5AC901.LSD3-00"
    ],
    "2003/2005/EC20 - No longer supported with AS 6.x": [
        "7AF101.7", "7AF104.7", "7AI261.7", "7AI294.7", "7AI351.70", "7AI354.70",
        "7AI774.70", "7AI984.70", "7AM351.70", "7AO352.70", "7AT324.70", "7AT351.7",
        "7AT352.70", "7AT664.70", "7CI410.70-1", "7CM211.7", "7CM411.70-1",
        "7CP430.60-1", "7CP470.60-1", "7CP474.60-1", "7CP476.60-1", "7CP570.60-1",
        "7CP770.60-1", "7CP774.60-1", "7DI135.70", "7DI138.70", "7DI140.70", "7DI435.7",
        "7DI439.7", "7DI439.72", "7DI645.7", "7DM435.7", "7DM438.72", "7DM465.7",
        "7DO135.70", "7DO138.70", "7DO139.70", "7DO164.7", "7DO435.7", "7DO720.7",
        "7DO721.7", "7DO722.7", "7DO723.7", "7EC020.60-2", "7EC020.61-2", "7EC021.60-1",
        "7EC021.61-2", "7EX270.50-1", "7EX290.50-1", "7EX470.50-1", "7EX481.50-1",
        "7EX484.50-1", "7EX770.50-1", "7IF311.7", "7IF321.7", "7IF361.70-1", "7IF371.70-1",
        "7ME010.9", "7ME020.9", "7ME050.72-1", "7MM424.70-1", "MM432.70-1", "7NC161.7"
    ],
    "7CX/XX - No longer supported with AS 6.x": [
        "7CX404.50-1", "7CX408.50-1", "7CX436.50-1", "7XV116.50-21", "7XX408.50-1",
        "7XX410.50-1", "7XX412.50-1", "7XX415.50-K02", "7XX426.50-1", "7XX432.50-1",
        "7XX436.50-1"
    ],
    "CIS - No longer supported with AS 6.x": [
        "80CIS.PS0-2", "80CIS.PS0-5"
    ],
    "ACOPOS - No longer supported with AS 6.x": [
        "8AC110.60-2", "8AC110.60-3", "8AC112.60-1", "8AC122.60-2"
    ],
    "ACOPOSinverter - No longer supported with AS 6.x": [
        "8I44xxxxxxx.xxx-1", "8I64xxxxxxx.00x-1", "8I74xxxxxxx.01P-1",
        "8I84xxxxxxx.01P-1"
    ],
    "8LS motors - No longer supported with AS 6.x": [
        "8LSA25.E8060D000-0", "8LSA25.E8060D200-0", "8LSA25.E9060D000-0",
        "8LSA25.E9060D200-0", "8LSA25.R0060D000-0", "8LSA25.R0060D200-0",
        "8LSA35.EA030D000-0", "8LSA35.EA030D200-0", "8LSA35.EA060D000-0",
        "8LSA35.EA060D200-0", "8LSA35.EB030D000-0", "8LSA35.EB030D200-0",
        "8LSA35.EB060D000-0", "8LSA35.EB060D200-0", "8LSA44.EA030D000-0",
        "8LSA44.EA030D200-0", "8LSA44.EA060D000-0", "8LSA44.EA060D200-0",
        "8LSA44.EB030D000-0", "8LSA44.EB030D200-0", "8LSA44.EB060D000-0",
        "8LSA44.EB060D200-0", "8LSA55.EA030D000-1", "8LSA55.EA030D200-1",
        "8LSA55.EB030D000-1", "8LSA55.EB030D200-1", "8LSA65.EA030D000-1",
        "8LSA65.EA030D200-1", "8LSA65.EB030D000-1", "8LSA65.EB030D200-1"
    ],
    "X20 modules - No longer supported with AS 6.x": [
        "X20AI2632-1", "X20AO2632-1", "X20BB22", "X20BB27", "X20BB32",
        "X20BB37", "X20BB42", "X20BB47", "X20BC0087-10", "X20cCP1301",
        "X20cCP1382-RT", "X20cCP1584", "X20cCP1586", "X20cCP3584", "X20cCP3586",
        "X20CM1201", "X20CP0201", "X20CP0291", "X20CP0292", "X20CP1301",
        "X20CP1381", "X20CP1381-RT", "X20CP1382", "X20CP1382-RT", "X20CP1483",
        "X20CP1483-1", "X20CP1484", "X20CP1484-1", "X20CP1485", "X20CP1485-1",
        "X20CP1486", "X20CP1583", "X20CP1584", "X20CP1585", "X20CP1586",
        "X20CP3484", "X20CP3484-1", "X20CP3485", "X20CP3485-1", "X20CP3486",
        "X20CP3583", "X20CP3584", "X20CP3585", "X20CP3586", "X20cPS9500",
        "X20CS1011", "X20cSO2110", "X20DC1398", "X20DI2653", "X20DO2623",
        "X20DO4331", "X20DS4387", "X20IF1061", "X20IF1065", "X20IF1074",
        "X20MK0201", "X20MK0203", "X20PS9500", "X20PS9502", "X20SL8000",
        "X20SL8001", "X20SL8010", "X20SL8011", "X20XC0201", "X20XC0202",
        "X20XC0292"
    ],
    "X67 modules - No longer supported with AS 6.x": [
        "X67BCJ321", "X67DV1311.L12", "X67IF1121"
    ],
    "Logic scanners - No longer supported with AS 6.x": [
        "5LS166.6", "5LS172.6", "5LS172.61", "5LS187.6", "5LS187.61", "5LS189.6", "5LS189.61"
    ],
    "Remote maintenance modules - No longer supported with AS 6.x": [
        "0RMSM1135", "0RMSM1135.4G-CN", "0RMSM1135.4G-EU", "0RMSM1135.4G-JP", "0RMSM1135.4G-US"
    ],
    "USB hub - No longer supported with AS 6.x": [
        "usbhubAP900", "usbhubAPC", "usbhubPPC"
    ],
    "Accessories (Battery) - No longer supported with AS 6.x": [
        "0AC240.9"
    ],
    "Accessories (8Port industrial hub) - No longer supported with AS 6.x : Replace with 0AC808.9-1": [
        "0AC808.9"
    ]
}

def display_progress(message):
    """
    Displays a progress message on the same line in the terminal.
    Ensures old text is cleared before writing new text.
    """
    sys.stdout.write('\r' + ' ' * 80)  # Clear line with space
    sys.stdout.write('\r' + message)  # Write new message
    sys.stdout.flush()

def process_stub(file_path, *args):
    """
    Stub process function for demonstration purposes.
    Simulates processing of files without actual logic.

    Args:
        file_path (str): The file path to process.
        *args: Additional arguments.

    Returns:
        list: An empty list for this stub function.
    """
    return []


def scan_files_parallel(root_dir, extensions, process_function, *args):
    """
    Scans files in a directory tree in parallel for specific content.

    Args:
        root_dir (str): The root directory to search in.
        extensions (list): File extensions to include.
        process_function (callable): The function to apply on each file.
        *args: Additional arguments to pass to the process_function.

    Returns:
        list: Aggregated results from all scanned files.
    """
    results = []
    file_paths = []

    for root, _, files in os.walk(root_dir):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_paths.append(os.path.join(root, file))

    total_files = len(file_paths)
    display_progress(f"Found {total_files} files to process...")
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_function, path, *args): path for path in file_paths}
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            display_progress(f"Processing file {i}/{total_files}...")
            results.extend(future.result())
    
    display_progress("Processing complete.".ljust(50))  # Clear line
    print()  # Move to next line
    return results

def process_pkg_file(file_path, patterns):
    """
    Processes a .pkg file to find matches for obsolete libraries.

    Args:
        file_path (str): Path to the .pkg file.
        patterns (dict): Patterns to match with reasons.

    Returns:
        list: Matches found in the file.
    """
    results = []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        # Regex for library names between > and <
        matches = re.findall(r'>([^<]+)<', content, re.IGNORECASE)
        for match in matches:
            for pattern, reason in patterns.items():
                if match.lower() == pattern.lower():
                    results.append((pattern, reason, file_path))
    return results

def process_var_file(file_path, patterns):
    """
    Processes a .var file to find matches for obsolete function blocks.

    Args:
        file_path (str): Path to the .var file.
        patterns (dict): Patterns to match with reasons.

    Returns:
        list: Matches found in the file.
    """
    results = []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        # Regex for function block declarations, e.g., : MpAlarmXConfigMapping;
        matches = re.findall(r':\s*([A-Za-z0-9_]+)\s*;', content)
        for match in matches:
            for pattern, reason in patterns.items():
                if match.lower() == pattern.lower():
                    results.append((pattern, reason, file_path))
    return results

def process_var_typ_file(file_path, patterns):
    """
    Processes a .var file to find matches for the given patterns.
    Ensures function block names in variable declarations are matched.

    Args:
        file_path (str): Path to the file.
        patterns (dict): Patterns to match with reasons.

    Returns:
        list: Matches found in the file.
    """
    results = []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        # Regex to match the format: name : FunctionBlockName;
        matches = re.findall(r':\s*([A-Za-z0-9_]+)\s*;', content)
        for match in matches:
            for pattern, reason in patterns.items():
                # Compare case-insensitively
                if match.lower() == pattern.lower():
                    results.append((pattern, reason, file_path))
    return results


def process_st_c_file(file_path, patterns):
    """
    Processes a .st, .c, or .cpp file to find matches for the given patterns.

    Args:
        file_path (str): Path to the file.
        patterns (dict): Patterns to match with reasons.

    Returns:
        list: Matches found in the file.
    """
    results = []
    matched_files = set()  # To store file paths and ensure uniqueness

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

        # Check for other patterns if necessary
        for pattern, reason in patterns.items():
            if re.search(rf'\b{re.escape(pattern)}\b', content) and file_path not in matched_files:
                results.append((pattern, reason, file_path))
                matched_files.add(file_path)  # Ensure file is added only once
                
    return results

def check_deprecated_string_functions(root_dir, extensions, deprecated_functions):
    """
    Scans all .st files in the project directory for deprecated string functions.

    Returns:
        list: A list of file paths where deprecated string functions were found.
    """
    deprecated_files = []

    for root, _, files in os.walk(root_dir):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if any(re.search(rf'\b{func}\b', content) for func in deprecated_functions):
                        deprecated_files.append(file_path)

    return deprecated_files


def check_deprecated_math_functions(root_dir, extensions, deprecated_functions):
    """
    Scans files for deprecated math function calls.
    
    Args:
        root_dir (str): The root directory to search in.
        extensions (list): List of file extensions to check.
        deprecated_functions (set): Set of deprecated math functions.

    Returns:
        list: A list of file paths where deprecated math functions were found.
    """
    deprecated_files = []
    function_pattern = re.compile(r'\b(' + '|'.join(deprecated_functions) + r')\s*\(')  # Match function names only when followed by '('

    for root, _, files in os.walk(root_dir):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if function_pattern.search(content):  # Only matches function calls
                        deprecated_files.append(file_path)

    return deprecated_files

def process_hw_file(file_path, hardware_dict):
    """
    Processes a .hw file to find unsupported hardware matches.

    Args:
        file_path (str): Path to the .hw file.
        hardware_dict (dict): Dictionary of unsupported hardware and their reasons.

    Returns:
        list: Unique matches found in the file.
    """
    results = set()  # Use a set to store unique matches
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        # Regex to extract the Type value from the <Module> elements
        matches = re.findall(r'<Module [^>]*Type="([^"]+)"', content)
        for hw_type in matches:
            for reason, items in hardware_dict.items():
                if hw_type in items:
                    results.add((hw_type, reason, file_path))  # Add as a tuple to ensure uniqueness
    return list(results)  # Convert back to a list for consistency


def process_lby_file(file_path, patterns):
    """
    Processes a .lby file to find obsolete dependencies.

    Args:
        file_path (str): Path to the .lby file.
        patterns (dict): Patterns of obsolete dependencies with reasons.

    Returns:
        list: Matches found in the file in the format (library_name, dependency, reason, file_path).
    """
    results = []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        # Extract library name (directory name as identifier)
        library_name = os.path.basename(os.path.dirname(file_path))
        # Extract dependencies from the XML content
        dependencies = re.findall(r'<Dependency ObjectName="([^"]+)"', content, re.IGNORECASE)
        for dependency in dependencies:
            for pattern, reason in patterns.items():
                # Compare case-insensitively
                if dependency.lower() == pattern.lower():
                    results.append((library_name, dependency, reason, file_path))
    return results

# Function to process libraries requiring reinstallation
def process_reinstall_libraries(file_path, patterns):
    """
    Processes a .pkg or .lby file to find libraries that need reinstallation.

    Args:
        file_path (str): Path to the file.
        patterns (dict): Libraries to be checked for reinstallation.

    Returns:
        list: Matches found in the file.
    """
    results = []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        matches = re.findall(r'>([^<]+)<', content, re.IGNORECASE)
        for match in matches:
            for library, action in patterns.items():
                if match.lower() == library.lower():
                    results.append((library, action, file_path))
    return results

def check_uad_files(root_dir):
    """
    Checks if .uad files are located in any directory ending with Connectivity/OpcUA.
    Returns a list of misplaced .uad files.

    Args:
        root_dir (str): Root directory of the project.

    Returns:
        list: List of misplaced .uad file paths.
    """
    required_suffix = os.path.normpath(os.path.join("Connectivity", "OpcUA"))
    misplaced_files = []

    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".uad"):
                current_dir = os.path.normpath(root)  # Normalize the directory path
                # Check if the directory ends with the required suffix
                if not current_dir.endswith(required_suffix):
                    misplaced_files.append(os.path.join(root, file))

    return misplaced_files

def check_files_for_compatibility(directory, file_patterns):
    """
    Checks the compatibility of .apj and .hw files within a directory.
    Validates that files have a minimum required version.

    Args:
        directory (str): Path to the directory to scan.
        file_patterns (list): Patterns of files to check, e.g., ['*.apj', '*.hw'].

    Returns:
        list: Results for incompatible files in the format (file_path, issue).
    """
    incompatible_files = []
    required_version_prefix = "4.12"

    for root, _, files in os.walk(directory):
        for file in files:
            if any(fnmatch.fnmatch(file, pattern) for pattern in file_patterns):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Extract version info from the file header
                    version_match = re.search(r'AutomationStudio Version="?([\d.]+)', content)
                    if version_match:
                        version = version_match.group(1)
                        if not version.startswith(required_version_prefix):
                            incompatible_files.append((file_path, f"Version {version}"))
                    else:
                        incompatible_files.append((file_path, "Version Unknown"))

                except Exception as e:
                    incompatible_files.append((file_path, f"Error reading file: {e}"))

    return incompatible_files

# Update main function to handle project directory input and optional debug flag
def main():
    """
    Main function to scan for obsolete libraries, function blocks, functions, and unsupported hardware.
    Outputs the results to a file as well as the console.
    """
    # Check if debug flag is provided
    debug_mode = "--debug" in sys.argv

    # Check if a project path is provided
    project_path = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.getcwd()

    # Check if valid project path
    if not os.path.exists(project_path):
        print(f"Error: The provided project path does not exist: {project_path}")
        print("\nEnsure the path is correct and the project folder exists.")
        print("\nIf the path contains spaces, make sure to wrap it in quotes, like this:")
        print('   python AS6_migration.py "C:\\path\\to\\your\\project"')
        sys.exit(1)

    # Check if .apj file exists in the provided path
    apj_files = [file for file in os.listdir(project_path) if file.endswith(".apj")]
    if not apj_files:
        print(f"Error: No .apj file found in the provided path: {project_path}")
        print("\nPlease specify a valid Automation Studio 4 project path.")
        print("\nExample usage:")
        print("1. To scan a specific Automation Studio 4 project directory:")
        print(r"   python AS6_migration.py C:\path\to\your\AutomationStudioProject")
        print("\n2. To scan the current directory where the script is located:")
        print("   python AS6_migration.py")
        sys.exit(1)

    print(f"Project path validated: {project_path}")
    print(f"Using project file: {apj_files[0]}")

    output_file = os.path.join(project_path, "AS6_migration_result.txt")
    with open(output_file, "w", encoding="utf-8") as file:
        try:
            def log(message, log_file=file):
                print(message)  # Print to console
                log_file.write(message + "\n")  # Write to file
                log_file.flush()  # Ensure data is written immediately

            log("Scanning started... Please wait while the script analyzes your project files.\n", file)

            start_time = time.time()

            # Use project_path as the root directory for scanning
            invalid_pkg_files = scan_files_parallel(
                os.path.join(project_path, "Logical", "Libraries"), [".pkg"], process_pkg_file, obsolete_dict
            )

            invalid_var_typ_files = scan_files_parallel(
                os.path.join(project_path, "Logical"), [".var", ".typ"], process_var_file, obsolete_function_blocks
            )

            invalid_st_c_files = scan_files_parallel(
                os.path.join(project_path, "Logical"), [".st", ".c", ".cpp"], process_st_c_file, obsolete_functions
            )

            hardware_results = scan_files_parallel(
                os.path.join(project_path, "Physical"), [".hw"], process_hw_file, unsupported_hardware
            )

            lby_dependency_results = scan_files_parallel(
                os.path.join(project_path, "Logical", "Libraries"), [".lby"], process_lby_file, obsolete_dict
            )

            # Store the list of files containing deprecated string functions
            deprecated_string_files = check_deprecated_string_functions(
                os.path.join(project_path, "Logical"),
                [".st"],
                {"ftoa", "atof", "itoa", "atoi", "memset", "memcpy", "memmove", "memcmp",
                "strcat", "strlen", "strcpy", "strcmp", "wcscat", "wcschr", "wcscmp",
                "wcsconv", "wcscpy", "wcslen", "wcsncat", "wcsncmp", "wcsncpy", "wcsrchr", "wcsset"}
            )

            # Ensure we have a valid list, even if no deprecated functions are found
            if not isinstance(deprecated_string_files, list):
                deprecated_string_files = []  # Fallback to an empty list

            # Boolean flag to indicate whether deprecated string functions were found
            found_deprecated_string = bool(deprecated_string_files)


            # Store the list of files containing deprecated math functions
            deprecated_math_files = check_deprecated_math_functions(
                os.path.join(project_path, "Logical"),
                [".st"],
                {"atan2", "ceil", "cosh", "floor", "fmod", "frexp", "ldexp", "modf",
                "pow", "sinh", "tanh"}
            )

            # Ensure we have a valid list, even if no deprecated functions are found
            if not isinstance(deprecated_math_files, list):
                deprecated_math_files = []  # Fallback to an empty list

            # Boolean flag to indicate whether deprecated math functions were found
            found_deprecated_math = bool(deprecated_math_files)

            log("\n\nChecking project and hardware files for compatibility...")
            file_patterns = ["*.apj", "*.hw"]
            compatibility_results = check_files_for_compatibility(project_path, file_patterns)
            if compatibility_results:
                for file_path, issue in compatibility_results:
                    log(f"- {file_path}: {issue}")
                log("\nPlease ensure these files are saved at least once with Automation Studio 4.12.")
            else:
                log("- All project and hardware files are valid.")

            log("\n\nChecking for misplaced .uad files...")
            uad_results = check_uad_files(os.path.join(project_path, "Physical"))
            if uad_results:
                log("The following .uad files are not located in the required Connectivity/OpcUA directory:")
                for file_path in uad_results:
                    log(f"- {file_path}")
                log("\nPlease create (via AS412) and move these files to the required directory: Connectivity/OpcUA.")
            else:
                log("- All .uad files are in the correct location.")

            log("\n\nThe following unsupported hardware were found:")
            if hardware_results:
                grouped_results = {}
                for hardware_id, reason, file_path in hardware_results:
                    config_name = os.path.basename(os.path.dirname(file_path))
                    grouped_results.setdefault(config_name, set()).add((hardware_id, reason))

                for config_name, entries in grouped_results.items():
                    log(f"\nHardware configuration: {config_name}")
                    for hardware_id, reason in sorted(entries):
                        log(f"- {hardware_id}: {reason}")
            else:
                log("- None")

            log("\n\nThe following invalid libraries were found in .pkg files:")
            if invalid_pkg_files:
                for library, reason, file_path in invalid_pkg_files:
                    log(f"- {library}: {reason} (Found in: {file_path})")
            else:
                log("- None")

            log("\n\nThe following obsolete dependencies were found in .lby files:")
            if lby_dependency_results:
                for library_name, dependency, reason, file_path in lby_dependency_results:
                    log(f"- {library_name}: Has dependency to {dependency} ({reason}) (Found in: {file_path})")
            else:
                log("- None")

            log("\n\nThe following invalid function blocks were found in .var and .typ files:")
            if invalid_var_typ_files:
                for block, reason, file_path in invalid_var_typ_files:
                    log(f"- {block}: {reason} (Found in: {file_path})")
            else:
                log("- None")

            log("\n\nThe following invalid functions were found in .st, .c and .cpp files:")
            found_any_invalid_functions = False

            if invalid_st_c_files:
                for function, reason, file_path in invalid_st_c_files:
                    log(f"- {function}: {reason} (Found in: {file_path})")
                found_any_invalid_functions = True

            if found_deprecated_string:
                log("- Deprecated AsString functions detected in the project: Consider using AsStringToAsBrStr.py to replace them.")
                found_any_invalid_functions = True

                # Debug: Print where the deprecated string functions were found only if --debug is enabled
                if debug_mode and deprecated_string_files:
                    print("\n[DEBUG] Deprecated AsString functions detected in the following files:")
                    for file in deprecated_string_files:
                        print(f"[DEBUG] - {file}")


            if found_deprecated_math:
                log("- Deprecated AsMath functions detected in the project: Consider using AsMathToAsBrMath.py to replace them.")
                found_any_invalid_functions = True

                # Debug: Print where the deprecated math functions were found only if --debug is enabled
                if debug_mode and found_deprecated_math:
                    print("\n[DEBUG] Deprecated AsMath functions detected in the following files:")
                    for file in deprecated_math_files:
                        print(f"[DEBUG] - {file}")


            if not found_any_invalid_functions:
                log("- None")

            end_time = time.time()
            log(f"\n\nScanning completed successfully in {end_time - start_time:.2f} seconds.")

        except Exception as e:
            error_message = f"\n[ERROR] An unexpected error occurred: {str(e)}"

            # Print error to console
            print(error_message)

            # Ensure log file is open before writing
            try:
                with open(output_file, "a", encoding="utf-8") as error_log:
                    error_log.write(error_message + "\n")
            except Exception as log_error:
                print(f"[ERROR] Failed to write error to log file: {log_error}")



    print(f"\nResults have been saved to {output_file}\n")

if __name__ == "__main__":
    main()
