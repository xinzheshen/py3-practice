import json

map_info = {1: (2, 10), 2: (15, 6)}

# with open(r"./map.json", "w") as f:
#     json.dump(map_info, f)


with open(r"./chapter_page_info.json", "r") as f:
    tmp = json.load(f)
    print(tmp)
