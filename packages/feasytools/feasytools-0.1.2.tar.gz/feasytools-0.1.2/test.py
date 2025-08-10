from tests.test_argcheck import *
from tests.test_ranglist import *
from tests.test_segfunc import *
from tests.test_timefunc import *
from tests.test_pq import *
from tests.test_kdtree import *

def test_all():
    test_argcheck()

    test_parse_time()
    test_rangelist()
    test_rangelist_empty()

    test_timefunc()
    test_segfunc()

    test_PQ()
    test_kdtree()

if __name__ == "__main__":
    test_all()
    print("All tests passed.")