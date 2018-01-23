import os
import shutil

ms_root = r""
target_dir = r""
label_root = r""
num_threshold = 15

label_dirs = os.listdir(label_root)

for l_d in label_dirs:
    label_path = os.path.join(label_root, l_d)
    label_files = os.listdir(label_path)
    for l_f in label_files:
        with open(os.path.join(label_path, l_f)) as f:
            lines = f.readlines()
            if len(lines) < num_threshold:
                continue
            for line in lines:
                filename = os.path.basename(line.strip())
                m_d = os.path.basename(os.path.dirname(line.strip()))
                if not os.path.exists(os.path.join(target_dir, m_d)):
                    os.makedirs(os.path.join(target_dir, m_d))
                if not os.path.exists(os.path.join(ms_root, m_d, filename)):
                    print(os.path.join(ms_root, m_d, filename))
                    continue
                shutil.copy(os.path.join(ms_root, m_d, filename),
                            os.path.join(target_dir, m_d, filename))


