from maptypes.bsmap import BSMap
from maptypes._test import test_map_type, test_sorted_map_type

test_map_type(BSMap, locals())

test_sorted_map_type(BSMap, locals())
