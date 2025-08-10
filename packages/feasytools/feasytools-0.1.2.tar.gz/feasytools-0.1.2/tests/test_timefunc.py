from feasytools import *

def test_timefunc():
    print("TimeFunc test:")
    f1 = ConstFunc(1)
    f2 = TimeImplictFunc(lambda: 1+2+3)
    f3 = ComFunc(lambda t: t)
    f4 = ManualFunc(1)
    f4.setManual(2)
    assert f1(0) == 1
    assert f2(0) == 6
    assert f3(0) == 0
    assert f4(0) == 2
    f5 = quicksum([f1,f2,f3,f4])
    f6 = quickmul([f1,f2,f3,f4])
    f7 = f5 + 1
    assert f7(0) == 10
    assert f5(0) == 9
    f8 = f6 * 2
    assert f8(1) == 24
    f9 = f5 + f6
    assert f9(1) == 22
    f10 = f5 * f6
    assert f10(1) == 120