import random, tqdm, time
from feasytools import KDTree, Point

def test_kdtree():    
    points = [
        Point(random.uniform(0, 10), random.uniform(0, 10)) for _ in range(100000)
    ]
    kdt = KDTree(points)
    for i in tqdm.trange(100):
        pt = Point(random.uniform(0, 10), random.uniform(0, 10))
        res1 = kdt.query(pt, max_dist=0.1)
        res2 = kdt.k_nearest(pt, k=len(res1))
        if len(res1) != len(res2):
            print(f"Length mismatch: {len(res1)} != {len(res2)}")
            raise ValueError("Length mismatch")
        for j, (p1, p2) in enumerate(zip(res1, res2)):
            if p1 != p2:
                print(f"Point {j} mismatch: {p1} != {p2} for query point {pt}")
                print(f"res1: {res1}")
                print(f"res2: {res2}")
                raise ValueError("Point mismatch")
        ans = []
        for p in points:
            if p.dist_to(pt) < 0.1:
                ans.append(p)
        assert len(ans) == len(res1), f"Expected {len(ans)} points, got {len(res1)}"


if __name__ == "__main__":
    test_kdtree()