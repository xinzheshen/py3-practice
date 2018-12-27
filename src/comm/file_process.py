import os


def get_valid_sub_folder_list(base_path):
    sub_folder_list = []
    all_sub = os.listdir(base_path)
    for sub in all_sub:
        if not os.path.isdir(os.path.join(base_path, sub)) or sub.startswith("."):
            continue
        sub_folder_list.append(sub)

    print(sub_folder_list)
    return sub_folder_list


def get_valid_sub_file_list(base_path, postfix):
    sub_file_list = []
    all_sub = os.listdir(base_path)
    for sub in all_sub:
        if not os.path.isfile(os.path.join(base_path, sub)) or not sub.endswith(postfix):
            continue
        sub_file_list.append(sub)

    print(sub_file_list)
    return sub_file_list
