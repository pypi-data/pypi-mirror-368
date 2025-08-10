from feasytools import RangeList

def test_parse_time():
    assert RangeList.parse_time("01:02:03") == 3723
    assert RangeList.parse_time("23:59:59") == 86399
    assert RangeList.parse_time("00:00:00") == 0
    assert RangeList.parse_time("12:34:56") == 45296
    assert RangeList.parse_time("25:00:00") == 90000  # Invalid time, should return 90000
    assert RangeList.parse_time("3600") == 3600
    assert RangeList.parse_time("1234") == 1234  # Valid integer time

def test_rangelist():
    ranges = [(0, 1), (2, 3), (4, 5)]
    t1 = RangeList(ranges)
    assert str(ranges) == str(t1)

    flag = False
    try:
        RangeList(ranges, 2, 3)
    except:
        flag = True
    
    if not flag:
        raise ValueError("Expected Error for invalid loop_period.")

    flag = False
    try:
        RangeList(ranges, 0, 10)
    except:
        flag = True
    
    if not flag:
        raise ValueError("Expected Error for invalid loop_times.")
    
    t2 = RangeList(ranges, 1, 10)
    assert str(t2) == str(ranges)

    t3 = RangeList(ranges, 2, 10)
    e3 = t3.toXMLNode("test")
    t4 = RangeList(e3)
    assert str(t3) == str(t4)

    assert 4 in t4
    assert 5 not in t4

    assert 10 in t4
    assert 11 not in t4

    assert 14 in t4
    assert 15 not in t4

    assert 20 not in t4
    assert 24 not in t4

    assert -1 not in t4
    assert 0 in t4
    assert 1000 not in t4

def test_rangelist_empty():
    t1 = RangeList()
    assert str(t1) == "[]"
    assert 0 in t1
    assert 1000 in t1
    assert -1000 in t1
    assert 1000000 in t1
    assert 1000000000 in t1

if __name__ == "__main__":
    test_parse_time()
    test_rangelist()
    test_rangelist_empty()
    print("All tests passed.")