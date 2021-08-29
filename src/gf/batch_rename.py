
import os


def rename(pic_dir):
    rename_file_pair = []
    for file in os.listdir(pic_dir):
        file_key = file.split("_")[-1].split(".")[0]
        if start <= int(file_key) <= stop:
            renamed_num = int(file_key) + change_num
            renamed_path = os.path.join(pic_dir, f"{renamed_num}.png")
            original_path = os.path.join(pic_dir, file)

            if change_num < 0:
                os.rename(original_path, renamed_path)
            else:
                rename_file_pair.append((original_path, renamed_path))

    for src, dst in reversed(rename_file_pair):
        os.rename(src, dst)






if __name__ == '__main__':
    pic_dir = r"D:\work\gf\截图\pictures\17"
    start = 13
    stop = 99
    change_num = 10
    rename(pic_dir)
