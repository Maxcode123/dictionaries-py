from maptypes.bstmap import BSTMap
from maptypes._test import test_map_type, test_sorted_map_type

test_map_type(BSTMap, locals())
test_sorted_map_type(BSTMap, locals())
