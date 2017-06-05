import os


def main():
    dir_name = ""
    label_dirs = os.listdir(dir_name)
    source_label_list_filename = dir_name + ".sll"
    source_label_list = []
    label_and_fullname = "%s %s"
    for label_dir in label_dirs:
        labels = os.listdir(os.path.join(dir_name, label_dir))
        for label in labels:
            source_label_list.append(label_and_fullname % (os.path.join(dir_name, label_dir, label), label_dir))
    sll_file = open(source_label_list_filename)
    sll_file.writelines(source_label_list)
    sll_file.close()

if __name__ == "__main__":
    main()
