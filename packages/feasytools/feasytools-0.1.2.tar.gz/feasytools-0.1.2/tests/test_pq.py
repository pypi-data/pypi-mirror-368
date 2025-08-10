from feasytools import PQueue, Heap

def test_PQ():
    hp = Heap()
    hp.push("h")
    hp.push("e")
    assert hp.empty() == False
    assert len(hp) == 2
    assert hp.remove("h") == True
    hp.push("f")
    assert hp.pop() == "e"
    assert hp.pop() == "f"
    assert hp.empty() == True

    q = PQueue()
    q.push(3, "henks")
    q.push(1, "shjd")
    assert q.pop() == (1,"shjd")
    assert q.remove("henks") == True