from functools import partial

from maptypes import SSMap, BSMap, BSTMap


text = ""
with open(
    "maptypes/benchmarks/sample.txt", "r"
) as f:
    text = f.read()

text = text.split(" ")


def set_item(map_type):
    map = map_type()

    for word in text:
        if word in map:
            map[word] += 1
        else:
            map[word] = 1


set_item_ssmap = partial(set_item, SSMap)
set_item_bsmap = partial(set_item, BSMap)
set_item_bstmap = partial(set_item, BSTMap)
set_item_dict = partial(set_item, dict)


__benchmarks__ = [
    (set_item_dict, set_item_bstmap, "Set item: BSTMap instead of dict"),
]
