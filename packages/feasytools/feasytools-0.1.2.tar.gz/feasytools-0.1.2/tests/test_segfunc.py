from feasytools import SegFunc

def test_segfunc():
    dataA = [(2, 1.0), (3, 2.0), (4, 3.0)]
    a = SegFunc(dataA)
    assert str(a) == str(dataA)
    dataB = ([1, 3, 5], [1.0, 2.0, 3.0])
    b = SegFunc(*dataB)
    assert str(b) == str(list(zip(*dataB)))
    c = SegFunc([])
    assert str(c) == str([])
    d = SegFunc.qs([a,b,c])
    dataD = [(1, 1.0), (2, 2.0), (3, 4.0), (4, 5.0), (5, 6.0)]
    assert str(d) == str(dataD)
    e = d.repeat(2,10)
    assert str(e) == str([(1, 1.0), (2, 2.0), (3, 4.0), (4, 5.0), (5, 6.0), (11, 1.0), (12, 2.0), (13, 4.0), (14, 5.0), (15, 6.0)])

    assert str(SegFunc.qs([])) == str([(0, 0)])

    empty = SegFunc()
    assert empty.value_at(1) == 0
    assert empty(1) == 0

    bi = b.interpolate(0, 100)
    assert str(bi) == str([(0, 0), (1, 1.0), (2, 1.0), (3, 2.0), (4, 2.0), (5, 3.0), (100, 3.0)])

    assert a(2) == 1.0
    assert a(3) == 2.0
    assert a(4) == 3.0
    assert a(5) == 3.0

    flag = False
    try:
        a(1)
    except:
        flag = True
    if not flag:
        raise ValueError("Expected Error for out of range access.")
    assert a.value_at(1) == 0

    tl, dseq = SegFunc.cross_interpolate([a, b])
    assert str(tl) == str([1, 2, 3, 4, 5])
    assert str(dseq) == str([[0, 1.0, 2.0, 3.0, 3.0], [1.0, 1.0, 2.0, 2.0, 3.0]])
    #print(e.toXML())
