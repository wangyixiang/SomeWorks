import pandas as pd
import os
import shutil


def name_it_with_label(name_label_pairs, query_dir, database_dir, file_ext):
    for nl_pair in name_label_pairs:
        name = nl_pair[0]
        label = nl_pair[1]
        query_item_name = os.path.join(query_dir, "%s.%s" % (name, file_ext))
        dataset_item_name = os.path.join(database_dir, "%s.%s" % (label, file_ext))
        if not os.path.exists(query_item_name):
            print("query item %s doesn't exist." % query_item_name)
            continue
        if not os.path.exists(dataset_item_name):
            print("dataset item %s doesn't exist." % dataset_item_name)
            continue
        try:
            os.rename(query_item_name, os.path.join(query_dir, "q_%s.%s" % (label, file_ext)))
            os.rename(dataset_item_name, os.path.join(database_dir, "d_%s.%s" % (label, file_ext)))
        except OSError as err:
            print("OS error: {0}".format(err))
            continue


def rename_folder_with_label(folder_name, database_dir, target_dir):
    database_filename_list = os.listdir(database_dir)
    database_label_list = [os.path.splitext(filename)[0] for filename in database_filename_list]
    subfolder_names = os.listdir(folder_name)

    for subfolder_name in subfolder_names:
        items = os.listdir(os.path.join(folder_name, subfolder_name))
        src_filename = items[0]
        should_label = str.split(items[0], '_')[0]
        if should_label in database_label_list:
            shutil.copyfile(os.path.join(folder_name, subfolder_name, src_filename), os.path.join(target_dir, src_filename))
        os.rename(os.path.join(folder_name, subfolder_name), os.path.join(folder_name, should_label))


def find_pair_in_database(query_path, database_path):
    q_files = os.listdir(query_path)
    d_files = os.listdir(database_path)
    for q_file in q_files:
        if q_file[2:] in d_files:
            os.rename(os.path.join(database_path, q_file[2:]), os.path.join(database_path, "d_" + q_file[2:]))
        else:
            print(q_file)


excel_file = r""
sheet = "answer"


def get_name_label_pairs_from_excel(excel_file, sheet_name):
    nl_pairs = []
    xlsx = pd.ExcelFile(excel_file)
    df = pd.read_excel(xlsx, sheet_name=sheet_name)

    return nl_pairs


csv_file = r"D:\datasets\xxxx_data\testphoto(simple)\newanswer.csv"


def get_name_label_pairs_from_csv(csv_file):
    nl_pairs = []
    df = pd.read_csv(csv_file, header=None)
    for i, r in df.iterrows():
        name = "%d" % r[0]
        label = r[1]
        nl_pairs.append([name, label])

    return nl_pairs


def main():
    pass


if __name__ == "__main__":
    main()