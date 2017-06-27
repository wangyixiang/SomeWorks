#! /usr/bin/python
#coding=utf-8

import sys

class Result:
    def __init__(self, query, register, score):
        self.query = query
        self.register = register
        self.score = score

def parse_query_filename(filename):
    '''
    Args:
        filename    query filename
    Returns:
        公民身份证号码 if filename is valid (210103********1561_李明_1); None otherwise
    Raises:
        None
    '''
    items = filename.split('_')
    if len(items) > 0:
        return items[0].upper()
    else:
        return None

def read_test_result(filepath):
    print('############################')
    print('reading test result...')
    linenum = 0
    total_linenum = 0
    threshold_step = 1.0 / 100000
    next_threshold = 1.0 / 100000
    FA_rate_thresholds = [1.0 / 100000, 1.0 / 10000, 1.0 / 1000, 1.0 / 100]
    passrate_list = [0, 0, 0, 0]
    score_list = [0, 0, 0, 0]
    todo_list = [True, True, True, True]
    test_data_list = []

    neg_count=0
    pos_count=0

    # sort
    with open(filepath, 'r') as fin:
        while True:
            line = fin.readline()
            if len(line) == 0:
                break
            total_linenum = total_linenum + 1
            items = line.strip().split(',')
            gmsfhm = items[1]
            if gmsfhm != None:
                data = Result(items[0], gmsfhm , float(items[2]))
                test_data_list.append(data)
                #print(gmsfhm)
                try:
                    gt = gt_map[data.query]
                    if gt == data.register:
                        pos_count = pos_count + 1
                    else:
                        neg_count = neg_count + 1
                except KeyError:
                    neg_count = neg_count + 1
                    pass

            else:
                print ('[WARNING] Line(%d) can\'t parse query filename' % (total_linenum))

    test_data_list.sort(key = lambda x: x.score, reverse = True)

    print('############################')
    print('reading test result finished')
    print('Total lines: %d' % total_linenum)
    print('Total valid data: %d' % len(test_data_list))

    correct = 0
    wrong = 0
    linenum = 0
    print("+++++++"+str(len(test_data_list)))
    for data in test_data_list:
        linenum = linenum + 1
        print(data.query)
        if not data.query in gt_map:
            print ('[WARNING] Line(%d) ground truth not found, key %s, skipped' % (linenum, data.query))
            continue
        gt = gt_map[data.query]
        #print ('[DEBUG] %s, %s, %f, %s -> %s' % (data.query, data.register, data.score, data.query, gt))
        if gt == data.register:
            correct = correct + 1
        else:
            wrong = wrong + 1

        FA_rate = float(wrong) / neg_count if neg_count != 0 else 0
        passrate = float(correct) / pos_count if pos_count != 0 else 0

        score = data.score
        if FA_rate > next_threshold:
            next_threshold = (int(FA_rate / threshold_step) + 1) * threshold_step
            print ('[INFO] FalseAlarm: %f, PassRate: %0.4f, Score: %0.4f' % (FA_rate, passrate, score))
        for i in range(len(FA_rate_thresholds)):
            FA_rate_threshold = FA_rate_thresholds[i]
            if FA_rate > FA_rate_threshold and todo_list[i]:
                passrate_list[i] = passrate
                score_list[i] = score
                todo_list[i] = False

        if FA_rate > 0.01:
            print ('[INFO] False Alarm rate larger than 0.01, finish')
            break

    print('Total lines: %d' % total_linenum)
    print('Total valid data: %d' % len(test_data_list))
    for i in range(len(FA_rate_thresholds)):
        print ('FA %f, PassRate: %f, score: %f' % (FA_rate_thresholds[i], passrate_list[i], score_list[i]))

gt_map = dict()
def read_ground_truth(filepath):
    print('############################')
    print('reading ground truth...')

    linenum = 0
    with open(filepath, 'r') as fin:
        while True:
            line = fin.readline()
            if len(line) == 0:
                break
            linenum = linenum + 1
            if linenum % 100000 == 0:
                print ('[Progress] %d' % linenum)
            items = line.strip().split(',')
            if len(items) != 2:
                print ('[WARNING] Line(%d) contains non-standard result, skipped: %s' % (linenum, line))
                continue
            query = items[0]
            if query in gt_map:
                print ('[WARNING] Line(%d) key duplicated, original %s -> %s, current value %s, skipped' % (linenum, query, gt_map[query] ,items[1]))
                continue
            gt_map[query] = items[1]
            # print(query + items[1])
    print('reading ground truth finished')
    print('############################')
    pass

def main():
    if len(sys.argv) != 3:
        print ('[USAGE] judge.py <test_filepath> <groundtruth_path>')
        sys.exit(1)
    test_filepath = sys.argv[1]
    groundtruth_path = sys.argv[2]
    read_ground_truth(groundtruth_path)
    read_test_result(test_filepath)

if __name__=='__main__':
    main()
