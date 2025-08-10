from abc import abstractmethod
import heapq
from typing import List, Tuple, TypeVar, Generic, Iterable, Optional, runtime_checkable, Protocol
from math import radians, sin, cos, sqrt, atan2

@runtime_checkable
class PointLike(Protocol):
    """Protocol for objects that can be treated as a Point."""
    @abstractmethod
    def dist_to(self, other: "PointLike") -> float:
        """Calculate the distance to another point-like object."""

    @abstractmethod
    def axis_offset(self, other: "PointLike", axis: int) -> float:
        """Calculate the distance to another point-like object along a specific axis."""
    
    @abstractmethod
    def __getitem__(self, idx: int) -> float:
        """Get the x or y coordinate by index."""

    @abstractmethod
    def __setitem__(self, idx: int, value: float):
        """Set the x or y coordinate by index."""
    
    @abstractmethod
    def __lt__(self, other: "Point") -> bool:
        """Less than comparison based on x and y coordinates."""
    
    @abstractmethod
    def __gt__(self, other: "Point") -> bool:
        """Greater than comparison based on x and y coordinates."""
    
    @abstractmethod
    def __eq__(self, other: "Point") -> bool:
        """Equality comparison based on x and y coordinates."""
    
    @abstractmethod
    def __hash__(self) -> int:
        """Hash based on x and y coordinates."""

@runtime_checkable
class LabelledPointLike(PointLike, Protocol):
    """Protocol for objects that can be treated as a labelled Point."""    
    @property
    @abstractmethod
    def label(self) -> str:
        """Get the label associated with the point."""

class GeoPos(PointLike):
    """A geographical position defined by latitude and longitude."""
    __slots__ = ("lat", "lon")
    def __init__(self, lat: float, lon: float):
        """Initialize a GeoPos with latitude and longitude."""
        self.lat = lat
        self.lon = lon
    
    def dist_to(self, other: "GeoPos") -> float:
        """Calculate the Euclidean distance to another GeoPos, in kilometers."""
        # Haversine formula for distance between two lat/lon points (in kilometers)
        R = 6371.0  # Earth radius in kilometers

        lat1 = radians(self.lat)
        lon1 = radians(self.lon)
        lat2 = radians(other.lat)
        lon2 = radians(other.lon)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c
    
    def axis_offset(self, other: "GeoPos", axis: int) -> float:
        if axis == 0: #Lat
            return 111.32 * (self.lat - other.lat)  # Approximate conversion from degrees to kilometers
        else: #Lon
            return 111.32 * (self.lon - other.lon) * cos(radians((self.lat + other.lat) / 2))  # Approximate conversion from degrees to kilometers, adjusted for latitude
    
    def __repr__(self):
        return f"GeoPos({self.lat}, {self.lon})"
    
    def __lt__(self, other: "GeoPos") -> bool:
        """Less than comparison based on latitude and longitude."""
        return (self.lat, self.lon) < (other.lat, other.lon)
    
    def __gt__(self, other: "GeoPos") -> bool:
        """Greater than comparison based on latitude and longitude."""
        return (self.lat, self.lon) > (other.lat, other.lon)
    
    def __eq__(self, other: "GeoPos") -> bool:
        """Equality comparison based on latitude and longitude."""
        return self.lat == other.lat and self.lon == other.lon
    
    def __hash__(self) -> int:
        """Hash based on latitude and longitude."""
        return hash((self.lat, self.lon))

    def __str__(self) -> str:
        """String representation of the GeoPos."""
        return f"({self.lat}, {self.lon})"
    
    def __getitem__(self, idx: int) -> float:
        """Get the latitude or longitude by index."""
        if idx == 0:
            return self.lat
        elif idx == 1:
            return self.lon
        else:
            raise IndexError("Index can only be 0 or 1")
    
    def __setitem__(self, idx: int, value: float):
        """Set the latitude or longitude by index."""
        if idx == 0:
            self.lat = value
        elif idx == 1:
            self.lon = value
        else:
            raise IndexError("Index can only be 0 or 1")

TLabel = TypeVar("TLabel")

class LabelledGeoPos(GeoPos, LabelledPointLike, Generic[TLabel]):
    """A geographical position with an associated label."""
    __slots__ = ("lat", "lon")
    def __init__(self, lat: float, lon: float, label: TLabel):
        """Initialize a LabelledGeoPos with latitude, longitude, and a label."""
        super().__init__(lat, lon)
        self.__lb = label
    
    @property
    def label(self) -> TLabel:
        """Get the label associated with the GeoPos."""
        return self.__lb
    @label.setter
    def label(self, value: TLabel):
        """Set the label associated with the GeoPos."""
        self.__lb = value
    
    def __repr__(self):
        return f"LabelledGeoPos({self.lat}, {self.lon}, '{self.label}')"
    
    def __str__(self):
        return f"({self.lat}, {self.lon}, '{self.label}')"

class Point(PointLike):
    """A 2D point class."""
    __slots__ = ("x", "y")
    def __init__(self, x: float, y: float):
        """Initialize a point with x and y coordinates."""
        self.x = x
        self.y = y

    def dist_to(self, other: "Point") -> float:
        """Calculate the Euclidean distance to another point."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def axis_offset(self, other: "Point", axis: int) -> float:
        return self[axis] - other[axis]

    def __repr__(self):
        return f"Point({self.x}, {self.y})"
    
    def __lt__(self, other: "Point") -> bool:
        """Less than comparison based on x and y coordinates."""
        return (self.x, self.y) < (other.x, other.y)
    
    def __gt__(self, other: "Point") -> bool:
        """Greater than comparison based on x and y coordinates."""
        return (self.x, self.y) > (other.x, other.y)
    
    def __eq__(self, other: "Point") -> bool:
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __getitem__(self, idx: int):
        if idx == 0:
            return self.x
        elif idx == 1:
            return self.y
        else:
            raise IndexError("Index can only be 0 or 1")

    def __setitem__(self, idx: int, value: float):
        if idx == 0:
            self.x = value
        elif idx == 1:
            self.y = value
        else:
            raise IndexError("Index can only be 0 or 1")

class LabelledPoint(Point, LabelledPointLike, Generic[TLabel]):
    """A 2D point with an associated label."""
    __slots__ = ("x","y")
    def __init__(self, x: float, y: float, label: TLabel):
        """Initialize a labelled point with x, y coordinates and a label."""
        super().__init__(x, y)
        self.__lb = label
    
    @property
    def label(self) -> TLabel:
        """Get the label associated with the Point."""
        return self.__lb
    @label.setter
    def label(self, value: TLabel):
        """Set the label associated with the Point."""
        self.__lb = value

    def __repr__(self):
        return f"LabelledPoint({self.x}, {self.y}, '{self.label}')"
    
    def __str__(self):
        return f"({self.x}, {self.y}, '{self.label}')"

TPoint = TypeVar("TPoint", bound=PointLike)

class KDTree(Generic[TPoint, TLabel]):
    """A 2D KD-Tree for nearest neighbor search. Each node is a point with string label in 2D space."""
    def __init__(
        self, points: Iterable[TPoint], labels: Optional[Iterable[TLabel]] = None, reverse_mapping: bool = False
    ):
        """
        Initialize the KD-Tree with a list of points and optional labels.
            points: An iterable of Point objects. If a list is provided, it will be used directly; otherwise, it will be converted to a list.
            labels: An optional iterable of labels corresponding to the points. If provided, it should have the same length as points.
            reverse_mapping: If True and labels are provided, a reverse mapping from labels to points will be created. Labels must be unique in this case.
        """
        self.__pts = list(points)
        if labels is not None:
            self.__lbs = {point: label for point, label in zip(self.__pts, labels)}
            assert len(self.__lbs) == len(self.__pts), "Points and labels must have the same length, and points must be unique"
            if reverse_mapping:
                self.__rlbs = {label: point for point, label in self.__lbs.items()}
                assert len(self.__rlbs) == len(self.__lbs), "Labels must be unique for reverse mapping"
            else:
                self.__rlbs = {}
        else:
            self.__lbs = {}
            if reverse_mapping:
                if all(isinstance(pt, LabelledPointLike) for pt in self.__pts):
                    self.__rlbs = {pt.label: pt for pt in self.__pts} # type: ignore
                    assert len(self.__rlbs) == len(self.__pts), "Labels must be unique for reverse mapping"
                else:
                    raise ValueError("Cannot create reverse mapping without labels")
            self.__rlbs = {}
        self.root = self._build(0, self.__pts)

    @property
    def points(self) -> "List[TPoint]":
        """Get all points in the KD-Tree."""
        return self.__pts
    
    def items(self) -> "Iterable[Tuple[TPoint, TLabel]]":
        """Get all (point, label) pairs in the KD-Tree."""
        assert len(self.__lbs) > 0, "No mapping available"
        return self.__lbs.items()
    
    def get_point(self, label: TLabel) -> Optional[TPoint]:
        """Get the point associated with a label."""
        assert len(self.__rlbs) > 0, "No reverse mapping available"
        return self.__rlbs.get(label)
    
    def get_label(self, point: TPoint) -> Optional[TLabel]:
        """Get the label associated with a point."""
        assert len(self.__lbs) > 0, "No mapping available"
        return self.__lbs.get(point)
    
    def __getitem__(self, label: TLabel) -> TPoint:
        """Get the point associated with a label."""
        assert len(self.__rlbs) > 0, "No reverse mapping available"
        return self.__rlbs[label]
    
    def __len__(self) -> int:
        """Get the number of points in the KD-Tree."""
        return len(self.__pts)
    
    def _build(self, depth: int, points: "List[TPoint]"): 
        '''$$ O(N log^2 N) $$'''
        if not points:
            return None
        axis = depth % 2
        points.sort(key=lambda point: point[axis])
        median = len(points) // 2
        return {
            "point": points[median],
            "left": self._build(depth + 1, points[:median]),
            "right": self._build(depth + 1, points[median+1:]),
        }

    def _nearest(self, node: Optional[dict], point: TPoint, depth: int):
        if node is None:
            return None
        axis = depth % 2
        next_branch = None
        opposite_branch = None
        if point[axis] < node["point"][axis]:
            next_branch = node["left"]
            opposite_branch = node["right"]
        else:
            next_branch = node["right"]
            opposite_branch = node["left"]
        best = self._closest(
            point, self._nearest(next_branch, point, depth + 1), node["point"]
        )
        if self._should_visit(point, best, node["point"]):
            best = self._closest(
                point, self._nearest(opposite_branch, point, depth + 1), best
            )
        return best

    def _k_nearest(
        self, node: Optional[dict], point: TPoint, depth: int, k: int, heap: list
    ):
        if node is None:
            return
        axis = depth % 2
        next_branch = None
        opposite_branch = None
        if point[axis] < node["point"][axis]:
            next_branch = node["left"]
            opposite_branch = node["right"]
        else:
            next_branch = node["right"]
            opposite_branch = node["left"]

        self._k_nearest(next_branch, point, depth + 1, k, heap)

        dist = point.dist_to(node["point"])
        if len(heap) < k:
            heapq.heappush(heap, (-dist, node["point"]))
        elif dist < -heap[0][0]:
            heapq.heappushpop(heap, (-dist, node["point"]))

        if len(heap) < k or abs(point.axis_offset(node["point"], axis)) < -heap[0][0]:
            self._k_nearest(opposite_branch, point, depth + 1, k, heap)
    
    def k_nearest(self, point: TPoint, k: int) -> "List[TPoint]":
        """
        Find the k nearest points to a given point.
        Returns a list of the k nearest points in ascending order of distance.
        """
        assert k > 0, "k must be greater than 0"
        heap = []
        if k > len(self.__pts):
            k = len(self.__pts)
        self._k_nearest(self.root, point, 0, k, heap)
        return [item[1] for item in sorted(heap, key=lambda x: -x[0])]
    
    def k_nearest_with_distance(self, point: TPoint, k: int) -> "List[Tuple[TPoint, float]]":
        """
        Find the k nearest points to a given point and return them with their distances.
        Returns a list of tuples (point, distance) in ascending order of distance.
        """
        assert k > 0, "k must be greater than 0"
        heap = []
        if k > len(self.__pts):
            k = len(self.__pts)
        self._k_nearest(self.root, point, 0, k, heap)
        return [(item[1], -item[0]) for item in sorted(heap, key=lambda x: -x[0])]

    def k_nearest_mapped(self, point: TPoint, k: int) -> "List[TLabel]":
        """
        Find the k nearest points to a given point and return their labels.
        Returns a list of the k nearest labels in ascending order of distance.
        """
        return [self.__lbs[pt] for pt in self.k_nearest(point, k)]
    
    def k_nearest_mapped_with_distance(self, point: TPoint, k: int) -> "List[Tuple[TLabel, float]]":
        """
        Find the k nearest points to a given point and return their labels with distances.
        Returns a list of tuples (label, distance) in ascending order of distance.
        """
        if len(self.__lbs) == 0:
            raise ValueError("No mapping available")
        return [(self.__lbs[pt], dist) for pt, dist in self.k_nearest_with_distance(point, k)]
    
    def k_nearest_full(self, point: TPoint, k: int) -> "List[Tuple[TPoint, TLabel, float]]":
        """
        Find the k nearest points to a given point and return them with their labels and distances.
        Returns a list of tuples (point, label, distance) in ascending order of distance.
        """
        if len(self.__lbs) == 0:
            raise ValueError("No mapping available")
        nearest_points = self.k_nearest_with_distance(point, k)
        return [(pt, self.__lbs[pt], dist) for pt, dist in nearest_points]

    def _closest(self, point: TPoint, p1: Optional[TPoint], p2: Optional[TPoint]):
        if p1 is None:
            return p2
        if p2 is None:
            return p1
        d1 = point.dist_to(p1)
        d2 = point.dist_to(p2)
        return p1 if d1 < d2 else p2

    def _should_visit(self, point: TPoint, best: Optional[TPoint], node: TPoint):
        if best is None:
            return True
        return point.dist_to(node) < point.dist_to(best)

    def nearest(self, point: TPoint) -> Optional[TPoint]:
        """Find the nearest point to a given point."""
        return self._nearest(self.root, point, 0)

    def nearest_with_distance(self, point: TPoint) -> Optional[Tuple[TPoint, float]]:
        """Find the nearest point to a given point and return it with its distance."""
        nearest_point = self._nearest(self.root, point, 0)
        if nearest_point is None:
            return None
        return nearest_point, point.dist_to(nearest_point)
    
    def nearest_mapped(self, point: TPoint) -> Optional[TLabel]:
        """Find the nearest point to a given point and return its label."""
        if self.__lbs is None:
            raise ValueError("No map given")
        p = self.nearest(point)
        if p is None:
            raise RuntimeError("No segment found")
        return self.__lbs[p]
    
    def nearest_mapped_with_distance(self, point: TPoint) -> Optional[Tuple[TLabel, float]]:
        """Find the nearest point to a given point and return its label and distance."""
        if self.__lbs is None:
            raise ValueError("No map given")
        p = self.nearest(point)
        if p is None:
            raise RuntimeError("No segment found")
        return self.__lbs[p], point.dist_to(p)
    
    def _query(self, node: Optional[dict], point: TPoint, max_dist: float, depth: int, heap: list, k: Optional[int] = None):
        if node is None:
            return
        axis = depth % 2
        dist = point.dist_to(node["point"])
        # Accept if within max_dist or if max_dist is None (unlimited)
        
        if dist <= max_dist:
            if k is not None:
                if len(heap) < k:
                    heapq.heappush(heap, (-dist, node["point"]))
                elif dist < -heap[0][0]:
                    heapq.heappushpop(heap, (-dist, node["point"]))
            else:
                heap.append((dist, node["point"]))
            
        # Decide whether to visit left/right branches
        if point.axis_offset(node["point"], axis) <= max_dist:
            self._query(node["left"], point, max_dist, depth + 1, heap, k)
        if point.axis_offset(node["point"], axis) >= -max_dist:
            self._query(node["right"], point, max_dist, depth + 1, heap, k)

    def query(self, point: TPoint, max_dist: Optional[float] = None, k: Optional[int] = None) -> "List[TPoint]":
        """
        Query the KD-Tree for points within a certain distance of a given point.
        If k is specified, return at most k closest points (within max_dist if given).
        If max_dist is None, search all points (but k must be specified).
        max_dist and k cannot both be None.
        Returns a list of the k nearest points in ascending order of distance.
        """
        if max_dist is None:
            if k is None:
                raise ValueError("max_dist and k cannot both be None")
            else:
                return self.k_nearest(point, k)
        
        heap = []
        self._query(self.root, point, max_dist, 0, heap, k)
        if k is not None:
            return [item[1] for item in sorted(heap, key=lambda x: -x[0])]
        else:
            return [item[1] for item in sorted(heap, key=lambda x: x[0])]
    
    def query_with_distance(self, point: TPoint, max_dist: Optional[float] = None, k: Optional[int] = None) -> "List[Tuple[TPoint, float]]":
        """
        Query the KD-Tree for points within a certain distance of a given point and return them with their distances.
        If k is specified, return at most k closest points (within max_dist if given).
        If max_dist is None, search all points (but k must be specified).
        max_dist and k cannot both be None.
        Returns a list of tuples (point, distance) in ascending order of distance.
        """
        if max_dist is None:
            if k is None:
                raise ValueError("max_dist and k cannot both be None")
            else:
                return self.k_nearest_with_distance(point, k)
        heap = []
        self._query(self.root, point, max_dist, 0, heap, k)
        if k is not None:
            return [(item[1], -item[0]) for item in sorted(heap, key=lambda x: -x[0])]
        else:
            return [(item[1], item[0]) for item in sorted(heap, key=lambda x: x[0])]
    
    def query_mapped(self, point: TPoint, max_dist: Optional[float] = None, k: Optional[int] = None) -> "List[TLabel]":
        """
        Query the KD-Tree for labels of points within a certain distance of a given point.
        If k is specified, return at most k closest labels (within max_dist if given).
        If max_dist is None, search all points (but k must be specified).
        max_dist and k cannot both be None.
        Returns a list of the k nearest labels in ascending order of distance.
        """
        if len(self.__lbs) == 0:
            raise ValueError("No mapping available")
        points = self.query(point, max_dist, k)
        return [self.__lbs[pt] for pt in points]
    
    def query_mapped_with_distance(self, point: TPoint, max_dist: Optional[float] = None, k: Optional[int] = None) -> "List[Tuple[TLabel, float]]":
        """
        Query the KD-Tree for labels of points within a certain distance of a given point and return them with their distances.
        If k is specified, return at most k closest labels (within max_dist if given).
        If max_dist is None, search all points (but k must be specified).
        max_dist and k cannot both be None.
        Returns a list of tuples (label, distance) in ascending order of distance.
        """
        if len(self.__lbs) == 0:
            raise ValueError("No mapping available")
        points_with_dist = self.query_with_distance(point, max_dist, k)
        return [(self.__lbs[pt], dist) for pt, dist in points_with_dist]
    
    def query_full(self, point: TPoint, max_dist: Optional[float] = None, k: Optional[int] = None) -> "List[Tuple[TPoint, TLabel, float]]":
        """
        Query the KD-Tree for points within a certain distance of a given point and return them with their labels and distances.
        If k is specified, return at most k closest points (within max_dist if given).
        If max_dist is None, search all points (but k must be specified).
        max_dist and k cannot both be None.
        Returns a list of tuples (point, label, distance) in ascending order of distance.
        """
        if len(self.__lbs) == 0:
            raise ValueError("No mapping available")
        nearest_points = self.query_with_distance(point, max_dist, k)
        return [(pt, self.__lbs[pt], dist) for pt, dist in nearest_points]
    
    def cluster_by_distance(self, max_dist: float) -> List[List[TPoint]]:
        """
        Cluster points in the KD-Tree such that all points in a cluster are within max_dist of at least one other point in the cluster.
        Returns a list of clusters, each cluster is a list of points.
        """
        visited = set()
        clusters = []

        for pt in self.__pts:
            if pt in visited:
                continue
            cluster = []
            queue = [pt]
            visited.add(pt)
            while queue:
                current = queue.pop()
                cluster.append(current)
                neighbors = self.query(current, max_dist)
                for neighbor in neighbors:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            clusters.append(cluster)
        return clusters

class Seg:
    """A line segment defined by two points."""
    __slots__ = ("p1", "p2")
    def __init__(self, p1: Point, p2: Point):
        self.p1 = p1
        self.p2 = p2

    def dist_to(self, point: Point) -> float:
        x0, y0 = self.p1.x, self.p1.y
        x1, y1 = self.p2.x, self.p2.y
        x2, y2 = point.x, point.y

        dx = x1 - x0
        dy = y1 - y0

        if dx == 0 and dy == 0:
            # The segment is actually a point
            return point.dist_to(self.p1)

        t = ((x2 - x0) * dx + (y2 - y0) * dy) / (dx * dx + dy * dy)

        if t < 0:
            # The closest point is p1
            return point.dist_to(self.p1)
        elif t > 1:
            # The closest point is p2
            return point.dist_to(self.p2)
        else:
            # The closest point is on the segment
            closest_x = x0 + t * dx
            closest_y = y0 + t * dy
            closest_point = Point(closest_x, closest_y)
            return point.dist_to(closest_point)

    def intersects_with(self, seg: "Seg") -> bool:
        x1, y1 = self.p1.x, self.p1.y
        x2, y2 = self.p2.x, self.p2.y
        x3, y3 = seg.p1.x, seg.p1.y
        x4, y4 = seg.p2.x, seg.p2.y

        def ccw(x1, y1, x2, y2, x3, y3):
            return (y3 - y1) * (x2 - x1) > (y2 - y1) * (x3 - x1)

        return ccw(x1, y1, x3, y3, x4, y4) != ccw(x2, y2, x3, y3, x4, y4) and ccw(
            x1, y1, x2, y2, x3, y3
        ) != ccw(x1, y1, x2, y2, x4, y4)

    def divide(self, k: int) -> "List[Point]":
        x1, y1 = self.p1.x, self.p1.y
        x2, y2 = self.p2.x, self.p2.y
        return [
            Point(x1 + (x2 - x1) * i / k, y1 + (y2 - y1) * i / k) for i in range(1, k)
        ]

    @property
    def length(self) -> float:
        return self.p1.dist_to(self.p2)

    def __repr__(self):
        return f"Seg({self.p1}, {self.p2})"

    def __eq__(self, other: "Seg") -> bool:
        return self.p1 == other.p1 and self.p2 == other.p2

    def __hash__(self):
        return hash((self.p1, self.p2))

    def __str__(self):
        return f"({self.p1}--{self.p2})"


class EdgeFinder:
    def __init__(self, segs: "dict[str, List[tuple[float, float]]]"):
        self.__pts: dict[Point, str] = {}
        for edge, shape in segs.items():
            for i, (x, y) in enumerate(shape):
                p = Point(x, y)
                self.__pts[p] = edge
                p0 = Point(shape[i - 1][0], shape[i - 1][1])
                seg = Seg(p, p0)
                for pp in seg.divide(max(1, int(seg.length / 10))):
                    self.__pts[pp] = edge
        self.kdtree = KDTree(self.__pts.keys())

    def find_nearest_edge(self, point: Point) -> "tuple[float, str]":
        nearest_point = self.kdtree.nearest(point)
        if nearest_point is None:
            raise RuntimeError("No segment found")
        return point.dist_to(nearest_point), self.__pts[nearest_point]


__all__ = ["Point", "Seg", "KDTree", "EdgeFinder", "GeoPos", "LabelledGeoPos", "LabelledPoint", "PointLike", "LabelledPointLike"]