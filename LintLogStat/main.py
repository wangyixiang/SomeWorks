import re
import os

ERROR_PATTERN = re.compile("Error (?P<Num>\d+):")
WARNING_PATTERN = re.compile("Warning (?P<Num>\d+):")
INFO_PATTERN = re.compile("Info (?P<Num>\d+):")
NOTE_PATTERN = re.compile("Note (?P<Num>\d+):")

MISRA_E_PATTERN = re.compile(r"Error (?P<Num>\d+):.*(?P<Misra>\[MISRA .*\])")
MISRA_W_PATTERN = re.compile(r"Warning (?P<Num>\d+):.*(?P<Misra>\[MISRA .*\])")
MISRA_I_PATTERN = re.compile(r"Info (?P<Num>\d+):.*(?P<Misra>\[MISRA .*\])")
MISRA_N_PATTERN = re.compile(r"Note (?P<Num>\d+):.*(?P<Misra>\[MISRA .*\])")

E_K = "Error"
W_K = "Warning"
I_K = "Info"
N_K = "Note"

LINT_E_RULES = {
}

#ComponentName{Error:{ErrorNum:Count}, Warning:{WarningNum:Count}, Info:{InfoNum:Count}}
def parse_lint_log_file(log_stat, log_filename):
    if not os.path.exists(log_filename):
        return False
    log_file = open(log_filename)
    log_lines = log_file.readlines()
    log_file.close()
    for log_line in log_lines:
        mo = ERROR_PATTERN.search(log_line)
        if (mo != None) and (len(mo.groups()) == 1):
            try:
                log_stat["Error"][mo.group("Num")] += 1
            except KeyError:
                log_stat["Error"][mo.group("Num")] = 1
            continue
        
        mo = WARNING_PATTERN.search(log_line)
        if (mo != None) and (len(mo.groups()) == 1):
            try:
                log_stat["Warning"][mo.group("Num")] += 1
            except KeyError:
                log_stat["Warning"][mo.group("Num")] = 1
            continue

        mo = INFO_PATTERN.search(log_line)
        if (mo != None) and (len(mo.groups()) == 1):
            try:
                log_stat["Info"][mo.group("Num")] += 1
            except KeyError:
                log_stat["Info"][mo.group("Num")] = 1
            continue

        mo = NOTE_PATTERN.search(log_line)
        if (mo != None) and (len(mo.groups()) == 1):
            try:
                log_stat["Note"][mo.group("Num")] += 1
            except KeyError:
                log_stat["Note"][mo.group("Num")] = 1
            continue
        
    i = len(log_lines) - 1
    MISRA_line = ""
    while i > 0:
        if MISRA_line == "":
            if log_lines[i].find("MISRA") != -1:
                MISRA_line = log_lines[i].strip()
            i -= 1
            continue
        else:
            moe = ERROR_PATTERN.search(log_lines[i])
            mow = WARNING_PATTERN.search(log_lines[i])
            moi = INFO_PATTERN.search(log_lines[i])
            mon = NOTE_PATTERN.search(log_lines[i])
            MISRA_line = log_lines[i].strip() + MISRA_line
            if moe != None:
                moem = MISRA_E_PATTERN.search(MISRA_line)
                if moem != None:
                    LINT_E_RULES[moem.group("Num")] = moem.group("Misra")
            elif mow != None:
                mowm = MISRA_W_PATTERN.search(MISRA_line)
                if mowm != None:
                    LINT_E_RULES[mowm.group("Num")] = mowm.group("Misra")
            elif moi != None:
                moim = MISRA_I_PATTERN.search(MISRA_line)
                if moim != None:
                    LINT_E_RULES[moim.group("Num")] = moim.group("Misra")
            elif mon != None:
                monm = MISRA_N_PATTERN.search(MISRA_line)
                if monm != None:
                    LINT_E_RULES[monm.group("Num")] = monm.group("Misra")
            else:
                i -= 1
                continue
            MISRA_line = ""
            i -= 1

    return True


def parse_lint_log_files(comp_dir, log_file_list):
    log_stat = {
        "Error":{},
        "Warning":{},
        "Info":{},
        "Note":{}
    }
    for log_file in log_file_list:
        if not parse_lint_log_file(log_stat, os.path.join(comp_dir, log_file)):
            print "Error on handling " + os.path.join(comp_dir, log_file)
    return log_stat


def output_csv(comp_name, log_stat):
    csv_filename = comp_name + ".csv"
    if os.path.exists(csv_filename):
        os.remove(csv_filename)
    csv_file = open(csv_filename, mode="w")
    csv_header = "Type,TypeNum,Count,MISRA\r"
    csv_file.write(csv_header)
    err_keys = sorted(log_stat["Error"].keys())
    warning_keys = sorted(log_stat["Warning"].keys())
    info_keys = sorted(log_stat["Info"].keys())
    note_keys = sorted(log_stat["Note"].keys())
    c = ","
    if len(err_keys) > 0 :
        for err_key in err_keys:
            csv_file.write("Error" + c + err_key + c + str(log_stat["Error"][err_key]))
            try:
                misra_rule = LINT_E_RULES[err_key]
            except KeyError:
                misra_rule = ""
            csv_file.write(c + misra_rule)
            csv_file.write("\r")
    if len(warning_keys) > 0:
        for warning_key in warning_keys:
            csv_file.write("Warning" + c + warning_key + c + str(log_stat["Warning"][warning_key]))
            try:
                misra_rule = LINT_E_RULES[warning_key]
            except KeyError:
                misra_rule = ""
            csv_file.write(c + misra_rule)
            csv_file.write("\r")
    if len(info_keys) > 0:
        for info_key in info_keys:
            csv_file.write("Info" + c + info_key + c + str(log_stat["Info"][info_key]))
            try:
                misra_rule = LINT_E_RULES[info_key]
            except KeyError:
                misra_rule = ""
            csv_file.write(c + misra_rule)
            csv_file.write("\r")
    if len(note_keys) > 0:
        for note_key in note_keys:
            csv_file.write("Note" + c + note_key + c + str(log_stat["Note"][note_key]))
            try:
                misra_rule = LINT_E_RULES[note_key]
            except KeyError:
                misra_rule = ""
                csv_file.write(c + misra_rule)
                csv_file.write("\r")    
    csv_file.close()

#ComponentNameList
C_M = {
    "arpresent":
    ["LibARPresent.txt"],
    
    "avn":
    ["avn.txt"],
    
    "avplayer":
    ["LibEMC.txt", 
     "LibPlaybackSDK_X86.txt", 
     "LibPlayer_X86.txt", 
     "LibUtility_x86.txt"],
    
    "demux":
    ["LibASFDemux.txt",
     "LibAVIDemux.txt",
     "LibCI_ID3Parser.txt",
     "LibFLVDemux.txt",
     "LibMP4Demux.txt",
     "liboggdemux.txt",
     "LibRMDemux.txt",
     "LibWavDemux.txt"
     ],
    
    "nav":
    ["nav.txt"]
}


def main():
    keys = C_M.keys()
    for key in keys:
        print "start handling " + key + " component lint log files."
        result = parse_lint_log_files(key, C_M[key])
        output_csv(key, result)
        print "finish handling " + key + " component lint log files."


if __name__ == "__main__":
    main()