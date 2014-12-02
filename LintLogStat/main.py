import re
import os

ERROR_PATTERN = re.compile("Error (?P<Num>\d+):")
WARNING_PATTERN = re.compile("Warning (?P<Num>\d+):")
INFO_PATTERN = re.compile("Info (?P<Num>\d+):")
NOTE_PATTERN = re.compile("Note (?P<Num>\d+):")

MISRA_E_PATTERN = re.compile(r"Error (?P<Num>\d+):(?P<Desc>.*)(?P<Misra>\[MISRA.*\])")
MISRA_W_PATTERN = re.compile(r"Warning (?P<Num>\d+):(?P<Desc>.*)(?P<Misra>\[MISRA.*\])")
MISRA_I_PATTERN = re.compile(r"Info (?P<Num>\d+):(?P<Desc>.*)(?P<Misra>\[MISRA.*\])")
MISRA_N_PATTERN = re.compile(r"Note (?P<Num>\d+):(?P<Desc>.*)(?P<Misra>\[MISRA.*\])")

E_K = "Error"
W_K = "Warning"
I_K = "Info"
N_K = "Note"

LINT_E_RULES = {
}

def process_desc(desc):
    desc = desc.strip()
    left_quote_pos = desc.find("'")
    right_parenthesis_pos = desc.rfind(")")
    if left_quote_pos != -1 and right_parenthesis_pos != -1:
            return desc[:left_quote_pos] + desc[right_parenthesis_pos + 1:]
    elif left_quote_pos != -1:
        right_quote_pos = desc.rfind("'")
        return desc[:left_quote_pos] + desc[right_quote_pos + 1:]
    return desc

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
                log_stat[E_K][mo.group("Num")] += 1
            except KeyError:
                log_stat[E_K][mo.group("Num")] = 1
            continue
        
        mo = WARNING_PATTERN.search(log_line)
        if (mo != None) and (len(mo.groups()) == 1):
            try:
                log_stat[W_K][mo.group("Num")] += 1
            except KeyError:
                log_stat[W_K][mo.group("Num")] = 1
            continue

        mo = INFO_PATTERN.search(log_line)
        if (mo != None) and (len(mo.groups()) == 1):
            try:
                log_stat[I_K][mo.group("Num")] += 1
            except KeyError:
                log_stat[I_K][mo.group("Num")] = 1
            continue

        mo = NOTE_PATTERN.search(log_line)
        if (mo != None) and (len(mo.groups()) == 1):
            try:
                log_stat[N_K][mo.group("Num")] += 1
            except KeyError:
                log_stat[N_K][mo.group("Num")] = 1
            continue
        
    i = len(log_lines) - 1
    MISRA_line = ""
    while i > 0:
        if MISRA_line == "":
            if log_lines[i].find("MISRA") != -1:
                if i == len(log_lines) - 1:
                    MISRA_line = log_lines[i].strip()
                else:
                    MISRA_line = log_lines[i].strip() + ' ' + log_lines[i + 1].strip()
            i -= 1
            continue
        else:
            moe = ERROR_PATTERN.search(log_lines[i])
            mow = WARNING_PATTERN.search(log_lines[i])
            moi = INFO_PATTERN.search(log_lines[i])
            mon = NOTE_PATTERN.search(log_lines[i])
            MISRA_line = log_lines[i].strip() + ' ' + MISRA_line
            if moe != None:
                moem = MISRA_E_PATTERN.search(MISRA_line)
                if moem != None:
                    LINT_E_RULES[moem.group("Num")] = [moem.group("Misra"), process_desc(moem.group("Desc").strip())]
            elif mow != None:
                mowm = MISRA_W_PATTERN.search(MISRA_line)
                if mowm != None:
                    LINT_E_RULES[mowm.group("Num")] = [mowm.group("Misra"), process_desc(mowm.group("Desc").strip())]
            elif moi != None:
                moim = MISRA_I_PATTERN.search(MISRA_line)
                if moim != None:
                    LINT_E_RULES[moim.group("Num")] = [moim.group("Misra"), process_desc(moim.group("Desc").strip())]
            elif mon != None:
                monm = MISRA_N_PATTERN.search(MISRA_line)
                if monm != None:
                    LINT_E_RULES[monm.group("Num")] = [monm.group("Misra"), process_desc(monm.group("Desc").strip())]
            else:
                i -= 1
                continue
            MISRA_line = ""
            i -= 1

    return True


def parse_lint_log_files(comp_dir, log_file_list):
    log_stat = {
        E_K:{},
        W_K:{},
        I_K:{},
        N_K:{}
    }
    for log_file in log_file_list:
        if not parse_lint_log_file(log_stat, os.path.join(comp_dir, log_file)):
            print "Error on handling " + os.path.join(comp_dir, log_file)
    return log_stat

def output_issue(type_name, log_stat, keys, csv_file):
    c = ","
    if len(keys) > 0 :
        for key in keys:
            csv_file.write(type_name + c + key + c + str(log_stat[type_name][key]))
            try:
                misra_rule = LINT_E_RULES[key]
                csv_file.write(c + misra_rule[0] + c + misra_rule[1])   
            except KeyError:
                misra_rule = ""
            csv_file.write("\r")
    
def output_csv(comp_name, log_stat):
    csv_filename = comp_name + ".csv"
    if os.path.exists(csv_filename):
        os.remove(csv_filename)
    csv_file = open(csv_filename, mode="w")
    csv_header = "Type,TypeNum,Count,MISRA,Description\r"
    csv_file.write(csv_header)

    err_keys = sorted(log_stat[E_K].keys())
    output_issue(E_K, log_stat, err_keys, csv_file)

    warning_keys = sorted(log_stat[W_K].keys())
    output_issue(W_K, log_stat, warning_keys, csv_file)

    info_keys = sorted(log_stat[I_K].keys())
    output_issue(I_K, log_stat, info_keys, csv_file)
   
    note_keys = sorted(log_stat[N_K].keys())
    output_issue(N_K, log_stat, note_keys, csv_file)

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