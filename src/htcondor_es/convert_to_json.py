#!/usr/bin/python

import os
import re
import json
import time
import classad
import logging
import datetime
import htcondor

string_vals = set([ \
  "Processor",
  "ChirpCMSSWCPUModels",
  "CPUModel",
  "CPUModelName",
  "ChirpCMSSWCPUModels",
  "CMSPrimaryPrimaryDataset",
  "CMSPrimaryProcessedDataset",
  "CMSPrimaryDataTier",
  "CRAB_JobType",
  "CRAB_JobSW",
  "CRAB_JobArch",
  "CRAB_ISB",
  "CRAB_Workflow",
  "CRAB_UserRole",
  "CMSGroups",
  "CRAB_UserHN",
  "CRAB_UserGroup",
  "CRAB_TaskWorker",
  "CRAB_SiteWhitelist",
  "CRAB_SiteBlacklist",
  "CRAB_PrimaryDataset",
  "Args",
  "AccountingGroup",
  "Cmd",
  "CMSGroups",
  "CMS_JobType",
  "DESIRED_Archs",
  "DESIRED_CMSDataLocations",
  "DESIRED_CMSDataset",
  "DESIRED_Sites",
  "ExtDESIRED_Sites",
  "GlobalJobId",
  "GlideinClient",
  "GlideinEntryName",
  "GlideinFactory",
  "GlideinFrontendName",
  "GlideinName",
  "GlobusRSL",
  "GridJobId",
  "LastRemoteHost",
  "MATCH_EXP_JOB_GLIDECLIENT_Name",
  "MATCH_EXP_JOB_GLIDEIN_ClusterId",
  "MATCH_EXP_JOB_GLIDEIN_CMSSite",
  "MATCH_EXP_JOB_GLIDEIN_Entry_Name",
  "MATCH_EXP_JOB_GLIDEIN_Factory",
  "MATCH_EXP_JOB_GLIDEIN_Name",
  "MATCH_EXP_JOB_GLIDEIN_Schedd",
  "MATCH_EXP_JOB_GLIDEIN_SEs",
  "MATCH_EXP_JOB_GLIDEIN_Site",
  "MATCH_EXP_JOB_GLIDEIN_SiteWMS",
  "MATCH_EXP_JOB_GLIDEIN_SiteWMS_JobId",
  "MATCH_EXP_JOB_GLIDEIN_SiteWMS_Queue",
  "MATCH_EXP_JOB_GLIDEIN_SiteWMS_Slot",
  "Owner",
  "RemoteHost",
  "REQUIRED_OS",
  "ShouldTransferFiles",
  "StartdIpAddr",
  "StartdPrincipal",
  "User",
  "WhenToTransferOutput",
  "WMAgent_AgentName",
  "WMAgent_RequestName",
  "WMAgent_SubTaskName",
  "x509UserProxyEmail",
  "x509UserProxyFirstFQAN",
  "x509UserProxyFQAN",
  "x509userproxysubject",
  "x509UserProxyVOName",
  "InputData",
  "Original_DESIRED_Sites",
  "WMAgent_TaskType",
  "NordugridRSL",
  "Campaign",
  "TaskType",
  "DataLocations",
  "Workflow",
  "Site",
  "Tier",
  "Country",
  "Status",
  "Universe",
  "ExitReason",
  "LastHoldReason",
  "RemoveReason",
  "DESIRED_Overflow_Region",
  "DESIRED_OpSysMajorVers",
  "DESIRED_CMSDataset",
  "DAGNodeName",
  "DAGParentNodeNames",
  "OverflowType",
  "ScheddName",
])

int_vals = set([ \
  "CRAB_Id",
  "CRAB_Retry",
  "BytesRecvd",
  "BytesSent",
  "ClusterId",
  "CommittedSlotTime",
  "CumulativeSlotTime",
  "CumulativeSuspensionTime",
  "CurrentHosts",
  "DelegatedProxyExpiration",
  "DiskUsage_RAW",
  "ExecutableSize_RAW",
  "ExitStatus",
  "GlobusStatus",
  "ImageSize_RAW",
  "JobPrio",
  "JobRunCount",
  "JobStatus",
  "JobUniverse",
  "LastJobStatus",
  "LocalSysCpu",
  "LocalUserCpu",
  "MachineAttrCpus0",
  "MachineAttrSlotWeight0",
  "MATCH_EXP_JOB_GLIDEIN_Job_Max_Time",
  "MATCH_EXP_JOB_GLIDEIN_MaxMemMBs",
  "MATCH_EXP_JOB_GLIDEIN_Max_Walltime",
  "MATCH_EXP_JOB_GLIDEIN_Memory",
  "MATCH_EXP_JOB_GLIDEIN_ProcId",
  "MATCH_EXP_JOB_GLIDEIN_ToDie",
  "MATCH_EXP_JOB_GLIDEIN_ToRetire",
  "MaxHosts",
  "MaxWallTimeMins_RAW",
  "MemoryUsage",
  "MinHosts",
  "NumGlobusSubmits"
  "NumJobMatches",
  "NumJobStarts",
  "NumRestarts",
  "NumShadowStarts",
  "NumSystemHolds",
  "PostJobPrio1",
  "PostJobPrio2",
  "ProcId",
  "Rank",
  "RecentBlockReadKbytes",
  "RecentBlockReads",
  "RecentBlockWriteKbytes",
  "RecentBlockWrites",
  "RemoteSlotID",
  "RemoteSysCpu",
  "RemoteUserCpu",
  "RemoteWallClockTime",
  "RequestCpus",
  "RequestDisk_RAW",
  "RequestMemory_RAW",
  "ResidentSetSize_RAW",
  "StatsLifetimeStarter",
  "TotalSuspensions",
  "TransferInputSizeMB",
  "WallClockCheckpoint",
  "WMAgent_JobID",
  "DesiredSiteCount",
  "DataLocationsCount",
])

date_vals = set([ \
  "CompletionDate",
  "EnteredCurrentStatus",
  "JobCurrentStartDate",
  "JobCurrentStartExecutingDate",
  "JobCurrentStartTransferOutputDate",
  "JobLastStartDate",
  "JobStartDate",
  "LastMatchTime",
  "LastSuspensionTime",
  "LastVacateTime_RAW",
  "QDate",
  "ShadowBday",
  "StageInFinish",
  "StageInStart",
  "JobFinishedHookDone",
  "LastJobLeaseRenewal",
  "LastRemoteStatusUpdate",
  "GLIDEIN_ToDie",
  "GLIDEIN_ToRetire",
  "DataCollectionDate",
  "RecordTime",
  "ChirpCMSSWLastUpdate",
])

ignore = set([
  "Arguments",
  "CmdHash",
  "CRAB_UserDN",
  "CRAB_Destination",
  "CRAB_DBSURL",
  "CRAB_ASOURL",
  "CRAB_ASODB",
  "CRAB_AdditionalOutputFiles",
  "CRAB_EDMOutputFiles",
  "CRAB_TFileOutputFiles",
  "CRAB_oneEventMode",
  "CRAB_NumAutomJobRetries",
  "CRAB_localOutputFiles",
  "CRAB_ASOTimeout",
  "CRAB_OutTempLFNDir",
  "CRAB_PublishDBSURL",
  "CRAB_PublishGroupName",
  "CRAB_RestURInoAPI",
  "CRAB_RestHost",
  "CRAB_ReqName",
  "CRAB_RetryOnASOFailures",
  "CRAB_StageoutPolicy",
  "SubmitEventNotes",
  "DAGManNodesMask",
  "DAGManNodesLog",
  "DAGManJobId",
  "accounting_group",
  "AcctGroup",
  "AcctGroupUser",
  "AllowOpportunistic",
  "AutoClusterAttrs",
  "AutoClusterId",
  "BufferBlockSize",
  "BufferSize",
  "CondorPlatform",
  "CondorVersion",
  "DiskUsage",
  "Err",
  "Environment",
  "EnvDelim",
  "Env",
  "ExecutableSize",
  "HasBeenRouted",
  "HasPrioCorrection",
  "GlideinCredentialIdentifier",
  "GlideinLogNr",
  "GlideinSecurityClass",
  "GlideinSlotsLayout",
  "GlideinWebBase",
  "GlideinWorkDir",
  "ImageSize",
  "In",
  "Iwd",
  "JobAdInformationAttrs",
  "job_ad_information_attrs",
  "JOB_GLIDECLIENT_Name",
  "JOB_GLIDEIN_ClusterId",
  "JOB_GLIDEIN_CMSSite",
  "JOBGLIDEIN_CMSSite",
  "JOB_GLIDEIN_Entry_Name",
  "JOB_GLIDEIN_Factory",
  "JOB_GLIDEIN_Job_Max_Time",
  "JOB_GLIDEIN_MaxMemMBs",
  "JOB_GLIDEIN_Max_Walltime",
  "JOB_GLIDEIN_Memory",
  "JOB_GLIDEIN_Name",
  "JOB_GLIDEIN_ProcId",
  "JOB_GLIDEIN_Schedd",
  "JOB_GLIDEIN_SEs",
  "JOB_GLIDEIN_Site",
  "JOB_GLIDEIN_SiteWMS",
  "JOB_GLIDEIN_SiteWMS_JobId",
  "JOB_GLIDEIN_SiteWMS_Queue",
  "JOB_GLIDEIN_SiteWMS_Slot",
  "JOB_GLIDEIN_ToDie",
  "JOB_GLIDEIN_ToRetire",
  "JobLeaseDuration",
  "JobNotification",
  "JOB_Site",
  "Managed",
  "MATCH_EXP_JOBGLIDEIN_CMSSite",
  "MATCH_EXP_JOB_Site",
  "MATCH_GLIDECLIENT_Name",
  "MATCH_GLIDEIN_ClusterId",
  "MATCH_GLIDEIN_CMSSite",
  "MATCH_GLIDEIN_Entry_Name",
  "MATCH_GLIDEIN_Factory",
  "MATCH_GLIDEIN_Job_Max_Time",
  "MATCH_GLIDEIN_MaxMemMBs",
  "MATCH_GLIDEIN_Max_Walltime",
  "MATCH_GLIDEIN_Name",
  "MATCH_GLIDEIN_ProcId",
  "MATCH_GLIDEIN_Schedd",
  "MATCH_GLIDEIN_SEs",
  "MATCH_GLIDEIN_Site",
  "MATCH_GLIDEIN_SiteWMS",
  "MATCH_GLIDEIN_SiteWMS_JobId",
  "MATCH_GLIDEIN_SiteWMS_Queue",
  "MATCH_GLIDEIN_SiteWMS_Slot",
  "MATCH_GLIDEIN_ToDie",
  "MATCH_GLIDEIN_ToRetire",
  "MATCH_Memory",
  "MyType",
  "NiceUser",
  "NumCkpts",
  "NumCkpts_RAW",
  "OnExitHold",
  "OnExitRemove",
  "OrigMaxHosts",
  "Out",
  "PeriodicHold",
  "PeriodicRelease",
  "PeriodicRemove",
  "Prev_DESIRED_Sites",
  "PublicClaimId",
  "RequestDisk",
  "RequestMemory",
  "ResidentSetSize",
  "REQUIRES_LOCAL_DATA",
  "RecentBlockReadKbytes",
  "RecentBlockReads",
  "RecentBlockWriteKbytes",
  "RecentBlockWrites",
  "RootDir",
  "ServerTime",
  "SpooledOutputFiles",
  "StreamErr",
  "StreamOut",
  "TargetType",
  "TransferIn",
  "TransferInput",
  "TransferOutput",
  "UserLog",
  "UserLogUseXML",
  "use_x509userproxy",
  "x509userproxy",
  "x509UserProxyExpiration",
  "WantCheckpoint",
  "WantRemoteIO",
  "WantRemoteSyscalls",
  "BlockReadKbytes",
  "BlockReads",
  "BlockWriteKbytes",
  "BlockWrites",
  "LocalSysCpu",
  "LeaveJobInQueue",
  "LocalUserCpu",
  "JobMachineAttrs",
  "LastRejMatchReason",
  "MachineAttrGLIDEIN_CMSSite0",
  "CMS_ALLOW_OVERFLOW",
  "LastPublicClaimId",
  "LastRemotePool",
  "Used_Gatekeeper",
  "DESIRED_OpSyses",
])

no_idx = set([
  "CRAB_OutLFNDir",
  "Args",
  "Cmd",
  "BytesRecvd",
  "CoreSize",
  "DelegatedProxyExpiration",
  "Environment",
  "RecentBlockReadKbytes",
  "RecentBlockReads",
  "RecentBlockWriteKbytes",
  "RecentBlockWrites",
  "RecentStatsLifetimeStarter",
  "CurrentHosts",
  "MachineAttrCpus0",
  "MachineAttrSlotWeight0",
  "LocalSysCpu",
  "LocalUserCpu",
  "MaxHosts",
  "MinHosts",
  "StartdIpAddr",
  "StartdPrincipal",
  "LastRemoteHost",
])

no_analysis = set([
  "CRAB_PublishName",
  "CRAB_PublishGroupName",
  "CondorPlatform",
  "CondorVersion",
  "CurrentHosts",
  "DESIRED_Archs",
  "ShouldTransferFiles",
  "TotalSuspensions",
  "REQUIRED_OS",
  "ShouldTransferFiles",
  "WhenToTransferOutput",
  "DAGParentNodeNames",
])

bool_vals = set([
  "CurrentStatusUnknown",
  "CRAB_Publish",
  "CRAB_SaveLogsFlag",
  "CRAB_TransferOutputs",
  "GlobusResubmit",
  "TransferQueued",
  "TransferringInput",
  "HasSingularity",
  "NiceUser",
  "ExitBySignal",
  "CMSSWDone",
])

# Fields to be kept in docs concerning running jobs
running_fields = set([
  "BenchmarkJobDB12",
  "Campaign",
  "CMS_JobType",
  "CMSGroups",
  "CMSPrimaryDataTier",
  "CMSSWKLumis",
  "CMSSWWallHrs",
  "CommittedCoreHr",
  "CoreHr",
  "Country",
  "CpuBadput",
  "CpuEff",
  "CpuEventRate",
  "CpuTimeHr",
  "CpuTimePerEvent",
  "CRAB_AsyncDest",
  "CRAB_DataBlock",
  "CRAB_UserHN",
  "CRAB_Workflow",
  # "DataLocations",
  "DESIRED_CMSDataset",
  # "DESIRED_Sites",
  "EventRate",
  "GlobalJobId",
  "HasSingularity",
  "InputData",
  "InputGB",
  "KEvents",
  "MegaEvents",
  "MemoryMB",
  "OutputGB",
  "QueueHrs",
  "ReadTimeMins",
  "RecordTime",
  "RequestCpus",
  "RequestMemory",
  "ScheddName",
  "Site",
  "Status",
  "TaskType",
  "Tier",
  "TimePerEvent",
  "Type",
  "WallClockHr",
  "WMAgent_RequestName",
  "WMAgent_SubTaskName",
  "Workflow",
])

status = { \
  0: "Unexpanded",
  1: "Idle",
  2: "Running",
  3: "Removed",
  4: "Completed",
  5: "Held",
  6: "Error",
}

universe = { \
  1: "Standard",
  2: "Pipe",
  3: "Linda",
  4: "PVM",
  5: "Vanilla",
  6: "PVMD",
  7: "Scheduler",
  8: "MPI",
  9: "Grid",
 10: "Java",
 11: "Parallel",
 12: "Local",
}

_launch_time = int(time.time())
def get_data_collection_time():
    return _launch_time

_cream_re = re.compile("CPUNumber = (\d+)")
_nordugrid_re = re.compile("\(count=(\d+)\)")
_camp_re = re.compile("[A-Za-z0-9_]+_[A-Z0-9]+-([A-Za-z0-9]+)-")
_prep_re = re.compile("[A-Za-z0-9_]+_([A-Z]+-([A-Za-z0-9]+)-[0-9]+)")
_rval_re = re.compile("[A-Za-z0-9]+_(RVCMSSW_[0-9]+_[0-9]+_[0-9]+)")
_prep_prompt_re = re.compile("(PromptReco|Repack|Express)_[A-Za-z0-9]+_([A-Za-z0-9]+)")
# 2016 reRECO; of the form cerminar_Run2016B-v2-JetHT-23Sep2016_8020_160923_164036_4747
_rereco_re = re.compile("[A-Za-z0-9_]+_Run20[A-Za-z0-9-_]+-([A-Za-z0-9]+)")
_split_re = re.compile("\s*,?\s*")
_generic_site = re.compile("^[A-Za-z0-9]+_[A-Za-z0-9]+_(.*)_")
_cms_site = re.compile("CMS[A-Za-z]*_(.*)_")
_cmssw_version = re.compile("CMSSW_((\d*)_(\d*)_.*)")
def convert_to_json(ad, cms=True, return_dict=False, reduce_data=False):
    analysis = ("CRAB_Id" in ad) or (ad.get("AccountingGroup", "").startswith("analysis."))
    if ad.get("TaskType") == "ROOT":
        return None
    result = {}
    result['DataCollection'] = ad.get("CompletionDate", 0)
    result['RecordTime'] = ad.get("CompletionDate", 0)
    if not result['DataCollection']:
        result['DataCollection'] = _launch_time
    if not result['RecordTime']:
        result['RecordTime'] = _launch_time
    result['DataCollectionDate'] = result['RecordTime']
    result['ScheddName'] = ad.get("GlobalJobId", "UNKNOWN").split("#")[0]
    if cms and analysis:
        result["Type"] = "analysis"
    elif cms:
        result["Type"] = "production"
    if cms:
        ad.setdefault("MATCH_EXP_JOB_GLIDEIN_CMSSite", ad.get("MATCH_EXP_JOBGLIDEIN_CMSSite", "Unknown"))
    for key in ad.keys():
        if key in ignore or key.startswith("HasBeen"):
            continue
        if key == "DESIRED_SITES":
            key = "DESIRED_Sites"
        try:
            value = ad.eval(key)
        except:
            continue
        if isinstance(value, classad.Value):
            if value == classad.Value.Error:
                continue
            else:
                value = None
        elif key in bool_vals:
            value = bool(value)
        elif key in int_vals:
            try:
                value = int(value)
            except ValueError:
                if value == "Unknown":
                    value = None
                else:
                    logging.info("Failed to convert key %s with value %s to int" % (key, repr(value)))
                    value = str(value)
        elif key in string_vals:
            value = str(value)
        elif key in date_vals:
            if value == 0:
                value = None
            else:
                value = int(value)
        #elif key in date_vals:
        #    value = datetime.datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M:%S")
        if key.startswith("MATCH_EXP_JOB_"):
            key = key[len("MATCH_EXP_JOB_"):]
        if key.endswith("_RAW"):
            key = key[:-len("_RAW")]
        result[key] = value
    if cms:
        ttype = ad.get("WMAgent_SubTaskName", "/UNKNOWN").rsplit("/", 1)[-1]

        # Guess the campaign from the request name.
        camp = ad.get("WMAgent_RequestName", "UNKNOWN")
        m = _camp_re.match(camp)
        if analysis:
            camp = "crab_" + ad.get("CRAB_UserHN", "UNKNOWN")
        elif camp.startswith("PromptReco"):
            camp = "PromptReco"
        elif camp.startswith("Repack"):
            camp = "Repack"
        elif camp.startswith("Express"):
            camp = "Express"
        elif "RVCMSSW" in camp:
            camp = "RelVal"
        elif m:
            camp = m.groups()[0]
        else:
            m = _rereco_re.match(camp)
            if m and ('DataProcessing' in ad.get("WMAgent_SubTaskName", "")):
                camp = m.groups()[0] + "Reprocessing"
        result["Campaign"] = camp

        # Guess an alternate campaign name from the subtask
        camp2_info = ttype.split("-")
        if len(camp2_info) > 1:
            camp2 = camp2_info[1]
        else:
            camp2 = ttype

        result['CMS_JobType'] = str(ad.get('CMS_JobType', 'Analysis' if analysis else 'Unknown'))
        result['CRAB_AsyncDest'] = str(ad.get('CRAB_AsyncDest', 'Unknown'))

        result["WMAgent_TaskType"] = ttype
        if analysis:
            ttype = "Analysis"
        elif "CleanupUnmerged" in ttype:
            ttype = "Cleanup"
        elif "Merge" in ttype:
            ttype = "Merge"
        elif "LogCollect" in ttype:
            ttype = "LogCollect"
        elif ("MiniAOD" in ad.get("WMAgent_RequestName", "UNKNOWN")) and (ttype == "StepOneProc"):
            ttype = "MINIAOD"
        elif ttype == "StepOneProc" and (("15DR" in camp2) or ("16DR" in camp2) or ("17DR" in camp2)):
            ttype = "DIGIRECO"
        elif "MiniAOD" in ttype:
            ttype = "MINIAOD"
        elif (("15GS" in camp2) or ("16GS" in camp2) or ("17GS" in camp2)) and ttype.endswith("_0"):
            ttype = "GENSIM"
        elif ttype.endswith("_0"):
            ttype = "DIGI"
        elif ttype.endswith("_1"):
            ttype = "RECO"
        elif ttype == "MonteCarloFromGEN":
            ttype = "GENSIM"
        result["TaskType"] = ttype
        prep = ad.get("WMAgent_RequestName", "UNKNOWN")
        m = _prep_re.match(prep)
        if analysis:
            prep = ad.get("CRAB_Workflow", "UNKNOWN").split(":", 1)[-1]
        elif m:
            prep = m.groups()[0]
        else:
            m = _prep_prompt_re.match(prep)
            if m:
                prep = m.groups()[0] + "_" + m.groups()[1]
            else:
                m = _rval_re.match(prep)
                if m:
                    prep = m.groups()[0]
        result["Workflow"] = prep
    now = time.time()
    if ad.get("JobStatus") == 2 and (ad.get("EnteredCurrentStatus", now+1) < now):
        ad["RemoteWallClockTime"] = int(now - ad["EnteredCurrentStatus"])
        ad["CommittedTime"] = ad["RemoteWallClockTime"]
    result["WallClockHr"] = ad.get("RemoteWallClockTime", 0)/3600.
    if 'RequestCpus' not in ad:
        m = _cream_re.search(ad.get("CreamAttributes", ""))
        m2 = _nordugrid_re.search(ad.get("NordugridRSL"))
        if m:
            try:
                ad['RequestCpus'] = int(m.groups()[0])
            except:
                pass
        elif m2:
            try:
                ad['RequestCpus'] = int(m2.groups()[0])
            except:
                pass
        elif 'xcount' in ad:
            ad['RequestCpus'] = ad['xcount']
    ad.setdefault('RequestCpus', 1)
    try:
        ad["RequestCpus"] = int(ad.eval('RequestCpus'))
    except:
        ad["RequestCpus"] = 1.0
    result["CoreHr"] = ad.get("RequestCpus", 1.0)*int(ad.get("RemoteWallClockTime", 0))/3600.
    result["CommittedCoreHr"] = ad.get("RequestCpus", 1.0)*ad.get("CommittedTime", 0)/3600.
    result["CommittedWallClockHr"] = ad.get("CommittedTime", 0)/3600.
    result["CpuTimeHr"] = (ad.get("RemoteSysCpu", 0)+ad.get("RemoteUserCpu", 0))/3600.
    result["DiskUsageGB"] = ad.get("DiskUsage_RAW", 0)/1000000.
    result["MemoryMB"] = ad.get("ResidentSetSize_RAW", 0)/1024.
    result["DataLocations"] = _split_re.split(ad.get("DESIRED_CMSDataLocations", "UNKNOWN"))
    result["DESIRED_Sites"] = _split_re.split(ad.get("DESIRED_Sites", "UNKNOWN"))
    result["DesiredSiteCount"] = len(result["DESIRED_Sites"])
    result["DataLocationsCount"] = len(result["DataLocations"])
    result["Original_DESIRED_Sites"] = _split_re.split(ad.get("ExtDESIRED_Sites", "UNKNOWN"))

    result['CMSPrimaryPrimaryDataset'] = 'Unknown'
    result['CMSPrimaryProcessedDataset'] = 'Unknown'
    result['CMSPrimaryDataTier'] = 'Unknown'
    if 'DESIRED_CMSDataset' in result:
        info = str(result['DESIRED_CMSDataset']).split('/')
        if len(info) > 3:
            result['CMSPrimaryPrimaryDataset'] = info[1]
            result['CMSPrimaryProcessedDataset'] = info[2]
            result['CMSPrimaryDataTier'] = info[-1]

    if cms and analysis:
        result["CMSGroups"] = _split_re.split(ad.get("CMSGroups", "UNKNOWN"))
        result["OutputFiles"] = len(ad.get("CRAB_AdditionalOutputFiles", [])) + len(ad.get("CRAB_TFileOutputFiles", [])) + len(ad.get("CRAB_EDMOutputFiles", [])) + ad.get("CRAB_SaveLogsFlag", 0)
    if "x509UserProxyFQAN" in ad:
        result["x509UserProxyFQAN"] = str(ad["x509UserProxyFQAN"]).split(",")
    if "x509UserProxyVOName" in ad:
        result["VO"] = str(ad["x509UserProxyVOName"])
    if cms:
        result["Site"] = ad.get("MATCH_EXP_JOB_GLIDEIN_CMSSite", "UNKNOWN")
    elif ('GlideinEntryName' in ad) and ("MATCH_EXP_JOBGLIDEIN_ResourceName" not in ad):
        m = _generic_site.match(ad['GlideinEntryName'])
        m2 = _cms_site.match(ad['GlideinEntryName'])
        if m2:
            result['Site'] = m2.groups()[0]
            info = result["Site"].split("_", 2)
            if len(info) == 3:
                result["Tier"] = info[0]
                result["Country"] = info[1]
            else:
                result["Tier"] = "Unknown"
                result["Country"] = "Unknown"
        elif m:
            result['Site'] = m.groups()[0]
        else:
            result['Site'] = 'UNKNOWN'
    else:
        result["Site"] = ad.get("MATCH_EXP_JOBGLIDEIN_ResourceName", "UNKNOWN")
    if cms:
        info = result["Site"].split("_", 2)
        if len(info) == 3:
            result["Tier"] = info[0]
            result["Country"] = info[1]
        else:
            result["Tier"] = "Unknown"
            result["Country"] = "Unknown"
        if "Site" not in result or "DESIRED_Sites" not in result:
            result["InputData"] = "Unknown"
        elif 'DESIRED_CMSDataLocations' not in result:  # CRAB2 case.
            result['InputData'] = 'Onsite'
        elif result["Site"] in result["DESIRED_CMSDataLocations"]:
            result["InputData"] = "Onsite"
        elif (result["Site"] != "UNKNOWN") and (ad.get("JobStatus") != 1):
            result["InputData"] = "Offsite"
            if analysis:
                if result["Site"] not in result["DESIRED_Sites"]:
                    result["OverflowType"] = "FrontendOverflow"
                else:
                    result["OverflowType"] = "IgnoreLocality"
            else:
                result["OverflowType"] = "Unified"
    if result["WallClockHr"] == 0:
        result["CpuEff"] = 0
    else:
        result["CpuEff"] = 100*result["CpuTimeHr"] / result["WallClockHr"] / float(ad.get("RequestCpus", 1.0))
    result["Status"] = status.get(ad.get("JobStatus"), "Unknown")
    result["Universe"] = universe.get(ad.get("JobUniverse"), "Unknown")
    result["QueueHrs"] = (ad.get("JobCurrentStartDate", time.time()) - ad["QDate"])/3600.
    result["Badput"] = max(result["CoreHr"] - result["CommittedCoreHr"], 0.0)
    result["CpuBadput"] = max(result["CoreHr"] - result["CpuTimeHr"], 0.0)

    # Parse Chirp statistics from CMSSW_8_0_0 and later.
    for key, val in result.items():
        if key.startswith('ChirpCMSSW_'):
            cmssw_key = 'ChirpCMSSW' + key.split('_', 2)[-1]
            if cmssw_key not in result:
                result[cmssw_key] = val
            elif cmssw_key.endswith('LastUpdate') or cmssw_key.endswith('Events') or cmssw_key.endswith('MaxLumis') or cmssw_key.endswith('MaxFiles'):
                result[cmssw_key] = max(result[cmssw_key], val)
            else:
                result[cmssw_key] += val
    if 'ChirpCMSSWFiles' in result:
        result['CompletedFiles'] = result['ChirpCMSSWFiles']
    if result.get('ChirpCMSSWMaxFiles', -1) > 0:
        result['MaxFiles'] = result['ChirpCMSSWMaxFiles']
    if 'ChirpCMSSWDone' in result:
        result['CMSSWDone'] = bool(result['ChirpCMSSWDone'])
        result['ChirpCMSSWDone'] = int(result['ChirpCMSSWDone'])
    if 'ChirpCMSSWElapsed' in result:
        result['CMSSWWallHrs'] = result['ChirpCMSSWElapsed']/3600.
    if 'ChirpCMSSWEvents' in result:
        result['KEvents'] = result['ChirpCMSSWEvents']/1000.
        result['MegaEvents'] = result['ChirpCMSSWEvents']/1e6
    if 'ChirpCMSSWLastUpdate' in result:
        # Report time since last update - this is likely stageout time for completed jobs
        result['SinceLastCMSSWUpdateHrs'] = max(result['RecordTime'] - result['ChirpCMSSWLastUpdate'], 0)/3600.
        if result['Status'] == 'Completed':
            result['StageOutHrs'] = result['SinceLastCMSSWUpdateHrs']
    if 'ChirpCMSSWLumis' in result:
        result['CMSSWKLumis'] = result['ChirpCMSSWLumis']/1000.
    if 'ChirpCMSSWReadBytes' in result:
        result['InputGB'] = result['ChirpCMSSWReadBytes']/1e9
    if 'ChirpCMSSWReadTimeMsecs' in result:
        result['ReadTimeHrs'] = result['ChirpCMSSWReadTimeMsecs'] / 3600000.0
        result['ReadTimeMins'] = result['ChirpCMSSWReadTimeMsecs'] / 60000.0
    if 'ChirpCMSSWWriteBytes' in result:
        result['OutputGB'] = result['ChirpCMSSWWriteBytes']/1e9
    if 'ChirpCMSSWWriteTimeMsecs' in result:
        result['WriteTimeHrs'] = result['ChirpCMSSWWriteTimeMsecs'] / 3600000.0
        result['WriteTimeMins'] = result['ChirpCMSSWWriteTimeMsecs'] / 60000.0
    if result.get('CMSSWDone') and (result.get('ChirpCMSSWElapsed', 0) > 0):
        result['CMSSWEventRate'] = result.get('ChirpCMSSWEvents', 0) / float(result['ChirpCMSSWElapsed']*ad.get("RequestCpus", 1.0))
        if result['CMSSWEventRate'] > 0:
            result['CMSSWTimePerEvent'] = 1.0 / result['CMSSWEventRate']
    if result['CpuTimeHr'] > 0:
        result['CpuEventRate'] = result.get('ChirpCMSSWEvents', 0) / float(result['CpuTimeHr']*3600.)
        if result['CpuEventRate'] > 0:
            result['CpuTimePerEvent'] = 1.0 / result['CpuEventRate']
    if result['CoreHr'] > 0:
        result['EventRate'] = result.get('ChirpCMSSWEvents', 0) / float(result['CoreHr']*3600.)
        if result['EventRate'] > 0:
            result['TimePerEvent'] = 1.0 / result['EventRate']
    if ('ChirpCMSSWReadOps' in result) and ('ChirpCMSSWReadSegments' in result):
        ops = result['ChirpCMSSWReadSegments'] + result['ChirpCMSSWReadOps']
        if ops:
            result['ReadOpSegmentPercent'] = result['ChirpCMSSWReadOps'] / float(ops)*100
    if ('ChirpCMSSWReadOps' in result) and ('ChirpCMSSWReadVOps' in result):
        ops = result['ChirpCMSSWReadOps'] + result['ChirpCMSSWReadVOps']
        if ops:
            result['ReadOpsPercent'] = result['ChirpCMSSWReadOps'] / float(ops)*100
    if ('Chirp_WMCore_cmsRun_ExitCode' in result) and (result.get('ExitCode', 0) == 0):
        result['ExitCode'] = result['Chirp_WMCore_cmsRun_ExitCode']

    # Parse CRAB3 information on CMSSW version
    result['CMSSWVersion'] = 'Unknown'
    result['CMSSWSubVersion'] = 'Unknown'
    result['CMSSWSubSubVersion'] = 'Unknown'
    if 'CRAB_JobSW' in result:
        match = _cmssw_version.match(result['CRAB_JobSW'])
        if match:
            result['CMSSWVersion'] = match.group(1)
            subv, ssubv = int(match.group(2)), int(match.group(3))
            result['CMSSWSubVersion'] = '%d_X_X' % (subv)
            result['CMSSWSubSubVersion'] = '%d_%d_X' % (subv, ssubv)

    # Parse new machine statistics.
    try:
        cpus = float(result['GLIDEIN_Cpus'])
        result['BenchmarkJobHS06'] = float(ad['MachineAttrMJF_JOB_HS06_JOB0'])/cpus
        if result.get('EventRate', 0) > 0:
            result['HS06EventRate'] = result['EventRate'] / result['BenchmarkJobHS06']
        if result.get('CpuEventRate', 0) > 0:
            result['HS06CpuEventRate'] = result['CpuEventRate'] / result['BenchmarkJobHS06']
        if result.get('CpuTimePerEvent', 0) > 0:
            result['HS06CpuTimePerEvent'] = result['CpuTimePerEvent'] * result['BenchmarkJobHS06']
        if result.get('TimePerEvent', 0) > 0:
            result['HS06TimePerEvent'] = result['TimePerEvent'] * result['BenchmarkJobDB12']
        result['HS06CoreHr'] = result['CoreHr'] * result['BenchmarkJobHS06']
        result["HS06CommittedCoreHr"] = result['CommittedCoreHr'] * result['BenchmarkJobHS06']
        result['HS06CpuTimeHr'] = result['CpuTimeHr'] * result['BenchmarkJobHS06']
    except:
        result.pop('MachineAttrMJF_JOB_HS06_JOB0', None)
    if ('MachineAttrDIRACBenchmark0' in ad) and classad.ExprTree('MachineAttrDIRACBenchmark0 isnt undefined').eval(ad):
        result['BenchmarkJobDB12'] = float(ad['MachineAttrDIRACBenchmark0'])
        if result.get('EventRate', 0) > 0:
            result['DB12EventRate'] = result['EventRate'] / result['BenchmarkJobDB12']
        if result.get('CpuEventRate', 0) > 0:
            result['DB12CpuEventRate'] = result['CpuEventRate'] / result['BenchmarkJobDB12']
        if result.get('CpuTimePerEvent', 0) > 0:
            result['DB12CpuTimePerEvent'] = result['CpuTimePerEvent'] * result['BenchmarkJobDB12']
        if result.get('TimePerEvent', 0) > 0:
            result['DB12TimePerEvent'] = result['TimePerEvent'] * result['BenchmarkJobDB12']
        result['DB12CoreHr'] = result['CoreHr'] * result['BenchmarkJobDB12']
        result["DB12CommittedCoreHr"] = result['CommittedCoreHr'] * result['BenchmarkJobDB12']
        result['DB12CpuTimeHr'] = result['CpuTimeHr'] * result['BenchmarkJobDB12']

    result['HasSingularity'] = classad.ExprTree('MachineAttrHAS_SINGULARITY0 is true').eval(ad)
    if 'ChirpCMSSWCPUModels' in ad and not isinstance(ad['ChirpCMSSWCPUModels'], classad.ExprTree):
        result['CPUModel'] = str(ad['ChirpCMSSWCPUModels'])
        result['CPUModelName'] = str(ad['ChirpCMSSWCPUModels'])
        result['Processor'] = str(ad['ChirpCMSSWCPUModels'])
    elif 'MachineAttrCPUModel0' in ad:
        result['CPUModel'] = str(ad['MachineAttrCPUModel0'])
        result['CPUModelName'] = str(ad['MachineAttrCPUModel0'])
        result['Processor'] = str(ad['MachineAttrCPUModel0'])

    if reduce_data:
        result = drop_fields_for_running_jobs(result)

    if return_dict:
        return result
    else:
        return json.dumps(result)

def convert_dates_to_millisecs(record):
    for date_field in date_vals:
        try:
            record[date_field] *= 1000
        except (KeyError, TypeError): continue

    return record

def drop_fields_for_running_jobs(record):
    skimmed_record = {}
    for field in running_fields:
        try:
            skimmed_record[field] = record[field]
        except KeyError: continue

    return skimmed_record
