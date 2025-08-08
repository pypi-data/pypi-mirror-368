import warnings
from typing import Callable, Any, List
import numpy as np
import hypertiling.kernel.GR_util as util
from hypertiling.kernel.GR_util import PI2
from hypertiling.kernel_abc import Tiling
import hypertiling.transformation as transform
import hypertiling.arraytransformation as arraytransform
import hypertiling.distance as distance
from hypertiling.ion import htprint
from hypertiling.kernel.hyperpolygon import HyperPolygon

# Magic number: real irrational number \Gamma(\frac{1}{4})
MANGLE = 3.6256099082219083119306851558676720029951676828800654674333779995


class GenerativeReflection(Tiling):
    """
    Very fast and lightweight tiling construction kernel, using reflections on ``open'' edges to generate new cells. 
    Only one symmetry sector is held on storage, with cells outside of this sector being generated on demand.

    p: Number of edges/vertices of a polygon
    q: Number of polygons that meet at a vertex
    n: Number of layers (reflective definition)
    m: Number of polygons
    m = m(p, q, n)

    LIMITATIONS:
    - A reflection layer can hold at max 4294967295 polys as the size is stored as uint32 (util.get_reflection_n_estimation)
    - The whole tiling can holy at max 34359738353 polys as the size of _sector_polys is determined as sum of uint32 of the 
    layers size in the fundamental sector
    - The number of reflection layers is limited to 255 at max, as util.generate stores the layers as uint8
    """

    def __init__(self, p: int, q: int, n: int, mangle: float = MANGLE):
        """
        Initialize a hyperbolic tiling. CELL CENTERED ONLY!

        Time-complexity: O(p^2 m + n + m / p * n)

        Parameters
        ----------
        p : int
            Number of vertices per cells.
        q : int
            Number of cells meeting at each vertex.
        n : int
            Number of layers to be constructed.
        degtol : int
            Tolerance at boundary in degrees.
        mangle : float
            Rotation of the center polygon in degrees
            (prevents boundaries from being along symmetry axis).
        """
        super().__init__(p, q, n, mangle)

        # technical attributes
        fac = np.pi / (p * q)
        self.r = np.sqrt(np.cos(fac * (p + q)) / np.cos(fac * (p - q)))
        self.mangle = mangle / 360 * PI2

        # estimate some other technical attributes
        if n != 0:
            lengths = util.get_reflection_n_estimation(p, q, n)  # n
            self._sector_lengths = np.ceil(lengths / p).astype(np.uint32)  # n
        else:
            self._sector_lengths = np.array([1])

        self._sector_polys = np.empty((np.sum(self._sector_lengths), p + 1), dtype=np.complex128)  # + center = p + 1
        self._edge_array = np.empty(self._sector_polys.shape[0], dtype=np.min_scalar_type(2 ** self.p - 1))
        """
        edge_array is not the most compact representation of the edges. The idea is to store which edges are blocked
        within a number in the array. Each polygon has its own number where the index is equal in edge_array and 
        the tiling

        This is saved for the possibility to expand the grid later (not yet implemented)
        """

        # calculate tiling
        rf = self.generate()  # p^2 m + n

        # correct properties of the tiling
        self.length = self.p * (len(rf) - 1) + 1
        self._sector_polys = self._sector_polys[:len(rf)]
        self._edge_array = self._edge_array[:len(rf)]
        self._sector_lengths = np.array([np.count_nonzero(rf == i) for i in range(np.max(rf) + 1)], dtype=np.uint32)

        # calculate additional helper variables
        self._sector_lengths_cumulated = np.empty((self._sector_lengths.shape[0] + 1,), dtype=np.uint32)
        self._sector_lengths_cumulated[0] = 0
        for i, element in enumerate(self._sector_lengths):  # n loop execs
            self._sector_lengths_cumulated[i + 1] = element + self._sector_lengths_cumulated[i]

        # possible to fill
        self._layers = None

    # Helper ###########################################################################################################

    def _polygen(self, polys: np.array) -> np.array:
        """
        Protected(!)
        Generator for iterating over polygons.

        Time-complexity (single polygon, cf. last yield): O(p)

        Parameters
        ----------
        polys : np.array
        Array of shape (n, p + 1) representing the segments the generator will create the rotations duplicates for and rotate over.

        Yields
        ------
        np.array
        Polygon of the segment polys or its rotational duplicates.
        """
        for poly in polys:
            yield poly

        dphi = PI2 / self.p
        phis = np.array([dphi * i for i in range(1, self.p)])
        for i, angle in enumerate(phis):
            for poly in polys:
                if self._sector_polys[0, 0] == 0:
                    yield poly * np.exp(angle * 1j)
                else:
                    poly_c = np.copy(poly)
                    arraytransform.morigin(self.p, self._sector_polys[0, 0], poly_c)
                    poly_c *= np.exp(angle * 1j)
                    arraytransform.morigin(self.p, - self._sector_polys[0, 0], poly_c)
                    yield poly_c

    def _wiggle_index(self, index1: int, index2: int, tol: int = 1) -> int:
        """
        Protected(!)
        Changes the position of index2 until the polygon shares a boundary with index 1.

        Time-complexity (single polygon): O(tol p^2)

        Parameters
        ----------
        index1 : int
            Index of the primary polygon.
        index2 : int
            Index of the searched polygon.

        Returns
        -------
        int
            Index of the searched polygon.
        """
        layer = self._get_reflection_level_in_sector(index2)
        connection = util.any_close_matrix(self._sector_polys[index1], self._sector_polys[index2])
        index_wiggled = index2
        side = 1
        while connection.shape[0] != 2:
            index_wiggled += side
            side += 1 if side > 0 else -1
            side *= -1
            if (index_wiggled - index2) > tol:
                return False

            connection = util.any_close_matrix(self._sector_polys[index1],
                                               self[self._index_from_ref_layer_index(index_wiggled, layer)])

        return index_wiggled

    def _index_from_ref_layer_index(self, index: int, ref_layer: int) -> int:
        """
        Protected(!)
        Calculates the index in the tiling a polygon in ref_layer would have when the reference layer would have been
        created circular.

        Time-complexity: O(1)

        Parameters
        ----------
        index : int
            Index the polygon would have if ref_layer would have been created circular.
        ref_layer : int
            Index of the reflection layer the polygons are created in.

        Returns
        -------
        int
            Index of the polygon in the tiling.
        """
        if index < self._sector_lengths_cumulated[ref_layer]:
            index += self._sector_lengths[ref_layer]
            index += (self._sector_polys.shape[0] - 1) * (self.p - 1)
        elif index >= self._sector_lengths_cumulated[ref_layer + 1]:
            index -= self._sector_lengths[ref_layer]
            index += self._sector_polys.shape[0] - 1
        return index

    def _expand_sector_index_to_tiling(self, index: int, f: Callable) -> Any:
        """
        Protected(!)
        Takes an index (for the tiling) and a function defined in the fundamental sector.
        Calculates the corresponding sector_index, applies function f, and corrects the result to index.

        Time-complexity: O(f(index))

        Parameters
        ----------
        index : int
            Index of a polygon in the tiling.
        f : Callable
            Function to apply on sector_index.

        Returns
        -------
        np.array
            Polygon of the segment polys or its rotational duplicates.
        """
        if index != 0:
            # get equivalent poly in sector
            index -= 1
            sector_replica = index // (self._sector_polys.shape[0] - 1)
            index %= (self._sector_polys.shape[0] - 1)
            index += 1
            jump = self._sector_polys.shape[0] - 1

            indices = f(index)

            indices = [(i + sector_replica * jump) if i != 0 else 0 for i in indices]
            return [i if i < self.length else i % self.length + 1 for i in indices]

        return f(index)

    @staticmethod
    def _to_weierstrass(polygons: np.array) -> np.array:
        """
        Protected(!)
        Calculates the Weierstrass coordinates for an array of polygons in Poincaré disks.

        Time-complexity: O(m / p)

        Parameters
        ----------
        polygons : np.array
            Array of shape (n, p + 1) representing polygons to calculate Weierstrass coordinates for.

        Returns
        -------
        np.array
            Array of shape (p + 1, 3) representing polygons in Weierstrass coordinates.
        """
        weierstrass = np.empty((len(polygons), 3), dtype=np.float64)
        weierstrass[:, 0] = 1
        weierstrass[:, 1] = np.real(polygons[:, 0])
        weierstrass[:, 2] = np.imag(polygons[:, 0])
        xx, yy = weierstrass[:, 1] * weierstrass[:, 1], weierstrass[:, 2] * weierstrass[:, 2]
        weierstrass[:, 0] += xx + yy
        weierstrass /= (1 - (xx + yy))[:, None]
        weierstrass[:, 1] *= 2
        weierstrass[:, 2] *= 2
        return weierstrass

    # Helper ###########################################################################################################
    # Basics ###########################################################################################################

    def generate(self):
        """
        Calculate the tiling polygons for an angular sector.

        Time-complexity: O(p^2 m + n)

        Returns
        -------
        void
        """
        return util.generate(self.p, self.q, self.r, self._sector_polys, self._sector_lengths, self._edge_array,
                             self.mangle)

    def add_layer(self):
        raise NotImplementedError(
            '[hypertiling]: Error: The requested function is not implemented! Please use a different kernel!')

    def map_layers(self):
        """
        This function is numerically expensive!
        Calculates the layer to each polygon.

        Time-complexity: O(m + p)

        Returns
        -------
        void
        """
        self._layers = np.empty(self._sector_polys.shape[0], dtype=np.uint8)
        self._layers.fill(self.n)  # m / p
        self._layers[0] = 0

        vertices = {np.round(vertex, 12): [np.uint8(1), 0] for vertex in self._sector_polys[0, 1:]}  # p

        for i, poly in enumerate(self._sector_polys[1:], start=1):  # m / p loop execs
            to_add = []
            for vertex_ in poly[1:]:  # p
                vertex = np.round(vertex_, 12)
                vertex__ = np.round(vertex_ * np.exp(- PI2 / self.p * 1j), 12)
                if vertex in vertices:  # 1
                    vertices[vertex][0] += 1
                    if vertices[vertex] == self.q:
                        del vertices[vertex]

                    v = vertices[vertex][1] + 1
                    self._layers[i] = v if v < self._layers[i] else self._layers[i]

                elif vertex__ in vertices:
                    vertices[vertex__][0] += 1
                    if vertices[vertex__] == self.q:
                        del vertices[vertex__]

                    v = vertices[vertex__][1] + 1
                    self._layers[i] = v if v < self._layers[i] else self._layers[i]

                else:
                    to_add.append(vertex)  # p

            for vertex in to_add:  # p loop execs
                vertices[vertex] = [np.uint8(1), self._layers[i]]

    def map_nbrs(self, tol: float = 1e-5):
        """
        This function is numerically expensive!
        Calculates the neighbors for each polygon.

        Time-complexity: O(m[ld(n + 1) / p + p^(log(m)) + ld(m / p) / p])

        Parameters
        ----------
        tol : float
            Tolerance to search neighbors in.

        Returns
        -------
        void
        """

        dtype = np.min_scalar_type(self.length)
        self._nbrs = np.empty((self._sector_polys.shape[0], self.p), dtype=dtype)
        self._nbrs.fill(- 1)  # to lazy to figure out what 2 ** dtype - 1 would be  # m / p
        self._nbrs[0] = [1 + i * (self._sector_polys.shape[0] - 1) for i in range(self.p)]  # p

        # fundamental sector
        weierstrass = self._to_weierstrass(self._sector_polys)  # m / p

        # boundary
        boundary_polys_indices = np.empty((2 * (len(self._sector_lengths) - 1), 1), dtype=np.uint32)
        boundary_polys = np.empty((2 * (len(self._sector_lengths) - 1), 1), dtype=np.complex128)
        for i in range(1, len(self._sector_lengths)):
            i1 = 2 * i - 2
            i2 = i1 + 1
            boundary_polys_indices[i1] = self._index_from_ref_layer_index(
                self._sector_lengths_cumulated[i] - 1, i)
            boundary_polys[i1, 0] = self[boundary_polys_indices[i1, 0]][0]
            boundary_polys_indices[i2] = self._index_from_ref_layer_index(
                self._sector_lengths_cumulated[i + 1], i)
            boundary_polys[i2, 0] = self[boundary_polys_indices[i2, 0]][0]
        boundary_weierstrass = self._to_weierstrass(boundary_polys)  # 2 * n
        del boundary_polys  # 2 * log(n + 1)

        for i, poly in enumerate(self._sector_polys[1:], start=1):  # m / p loop execs
            ref_layer = self._get_reflection_level_in_sector(i)  # log(m / p)

            # parents
            dists = distance.lorentzian_distance(weierstrass[
                                                 self._sector_lengths_cumulated[ref_layer - 1]:
                                                 self._sector_lengths_cumulated[
                                                     ref_layer]], weierstrass[i])  # p^(log_p(m) - 1)

            indices = np.argpartition(dists, 2)[:2] if len(dists) > 2 else np.arange(len(dists))  # p^(log_p(m) - 1)
            # necessary to compensate the cumulated uncertainty in the last layer
            ref_dist = np.min(dists[indices])
            allowed = np.argwhere(util.is_close_within_tol(dists[indices], ref_dist, tol=tol))
            c = len(allowed)
            self._nbrs[i, :c] = indices[allowed].flatten() + self._sector_lengths_cumulated[ref_layer - 1]

            # siblings
            if self.q == 3:
                self._nbrs[i, c] = self._index_from_ref_layer_index(i + 1, ref_layer)
                c += 1
                self._nbrs[i, c] = self._index_from_ref_layer_index(i - 1, ref_layer)
                c += 1
            else:
                next_ = i + 1
                if next_ < self._sector_lengths_cumulated[ref_layer + 1] and \
                        util.is_close_within_tol(distance.lorentzian_distance(weierstrass[next_], weierstrass[i]),
                                                 ref_dist,
                                                 tol=tol):
                    self._nbrs[i, c] = next_
                    c += 1

                before = i - 1
                if before >= self._sector_lengths_cumulated[ref_layer] and \
                        util.is_close_within_tol(distance.lorentzian_distance(weierstrass[before], weierstrass[i]),
                                                 ref_dist,
                                                 tol=tol):
                    self._nbrs[i, c] = before
                    c += 1

            # children
            if len(self._sector_lengths) > ref_layer + 1:
                dists = distance.lorentzian_distance(weierstrass[
                                                     self._sector_lengths_cumulated[ref_layer + 1]:
                                                     self._sector_lengths_cumulated[
                                                         ref_layer + 1] + self._sector_lengths[ref_layer + 1]],
                                                     weierstrass[i])  # p^(log_p(m) + 1)

                to_get = self.p - c
                indices = np.argpartition(dists, to_get)[:to_get] if len(dists) > to_get else np.arange(len(dists))
                # p^(log_p(m) + 1)
                # necessary to compensate the cumulated uncertainty in the last layer
                allowed = np.argwhere(util.is_close_within_tol(dists[indices], ref_dist, tol=tol))  # p - 2
                c_ = len(allowed)
                self._nbrs[i, c:c + c_] = indices[allowed].flatten() + self._sector_lengths_cumulated[
                    ref_layer + 1]  # p - 2
                c += c_

            # control boundary child->nephew artifact
            # boundary
            rest = self.p - c
            if rest == 0:
                continue

            dists = distance.lorentzian_distance(boundary_weierstrass, weierstrass[i])  # 2 * log(n + 1)
            indices = np.argsort(dists)  # 2 * log(n + 1)
            allowed = np.argwhere(util.is_close(dists[indices], ref_dist))  # 2 * log(n + 1)
            for index in boundary_polys_indices[indices[allowed]].flatten():  # p
                if index in self._nbrs[i]:
                    continue
                self._nbrs[i, c] = index
                c += 1

    def check_integrity(self):
        """
        This function is numerically expensive!
        Checks the integrity of the grid. The number of neighbors as well as a search for duplicates is applied.
        Raises AttributeError if the grid seems to be invalid.

        Time-complexity: O(m p^2 n)

        Returns
        -------
        void
        """
        # check if one polygon is shifted in the range of another or if duplicates exist
        for i in range(len(self._sector_polys)):  # m / p loop execs
            poly_center = self._sector_polys[i, 0]
            self._sector_polys[i, 0] = 0
            try:
                if self.find(poly_center):  #
                    raise AttributeError(
                        f"[hypertiling] Error: Duplicate detected at index {i} at layer {self.get_reflection_level(i)}")
            finally:
                self._sector_polys[i, 0] = poly_center

        # check if all edges have a partner
        for i in range(len(self._sector_polys)):
            neighbor_counter = len(self.get_nbrs_generative(i))
            if neighbor_counter == self.p:
                continue
            print(f"Integrity ensured till index {i} at layer {self.get_reflection_level(i)}")
            return

    def __len__(self):
        """
        Return the number of polygons in the tiling.

        Time-complexity: O(1)

        Returns
        -------
        int
            Number of polygons in the tiling.
        """
        return self.length

    def __iter__(self) -> np.array:
        """
        Iterates over the whole grid. As only one sector is stored in the memory, the others are generated when needed.
        Time-complexity (single polygon): O(p)
        :yield: np.array
            Array of shape [center, vertices].
        """
        for poly in self._sector_polys:
            yield poly

        dphi = PI2 / self.p
        phis = np.array([dphi * i for i in range(1, self.p)])
        for i, angle in enumerate(phis):
            for poly in self._sector_polys[1:]:
                if self._sector_polys[0, 0] == 0:
                    yield poly * np.exp(angle * 1j)
                else:
                    poly_c = np.copy(poly)
                    arraytransform.morigin(self.p, self._sector_polys[0, 0], poly_c)
                    poly_c *= np.exp(angle * 1j)
                    arraytransform.morigin(self.p, - self._sector_polys[0, 0], poly_c)
                    yield poly_c

    def __getitem__(self, index: int) -> np.array:
        """
        Returns the center and vertices of the polygon at index. As only one sector is stored,
        the corresponding polygon is calculated if necessary.
        Time-complexity: O(p)

        Parameters
        ----------
        index : int
            Index of the polygon.

        Returns
        -------
        np.array
            Array of shape (p + 1) representing [center, vertices].
        """
        if index == 0:
            return self._sector_polys[0]

        # remove the first one (the central polygon) from consideration
        index -= 1

        phi = PI2 / self.p * (index // (self._sector_polys.shape[0] - 1))
        index = index if index < (self._sector_polys.shape[0] - 1) else index % (self._sector_polys.shape[0] - 1)

        # +1 to ignore the first one
        poly = self._sector_polys[index + 1]

        if phi == 0:
            return poly

        if self._sector_polys[0, 0] == 0:
            return poly * np.exp(phi * 1j)

        else:
            poly_c = np.copy(poly)
            arraytransform.morigin(self.p, self._sector_polys[0, 0], poly_c)
            poly_c *= np.exp(phi * 1j)
            arraytransform.morigin(self.p, - self._sector_polys[0, 0], poly_c)
            return poly_c

    # Basics ###########################################################################################################
    # API ##############################################################################################################

    def get_nbrs_list(self, tol: float = 1e-5, method="default") -> List[List[int]]:
        """
        Create and return list of all neighbors

        Time-complexity: O(mp)

        Parameters
        ----------
        tol : float
            Tolerance to search neighbors in.
        method : str
            Method to use for calculating the neighbors. Currently "default" only.

        Returns
        -------
        List[List[int]]
            List of all neighbors for all polygons.
        """
        if method != "default":
            raise AttributeError("[hypertiling] Error: Only default implemented yet")

        if len(self) == 1:
            htprint("Warning", "Tiling consists of one polygon!")
            return [[]]

        if self._nbrs is None:
            self.map_nbrs(tol=tol)

        part = np.copy(self._nbrs[1:]).astype(np.uint32)  # m / p * p = m
        max_number = np.iinfo(self._nbrs.dtype).max  # m / p

        jump = np.uint32(self._sector_polys.shape[0] - 1)
        rotate = np.vectorize(lambda x: x if x == max_number else x if x == 0 else x + jump)
        neighbors = [[element for element in line if element != max_number] for line in self._nbrs.tolist()]
        # m / p loop execs: p loop execs: O(1)

        for sector_i in range(1, self.p):  # p loop execs
            part = rotate(part)  # m / p * p = m
            neighbors += [[i if i < self.length else i % self.length + 1 for i in line if i != max_number] for line in
                          part.tolist()]
            # m / p loop execs: p loop execs: O(1)

        return neighbors

    def get_layer(self, index: int) -> int:
        """
        Returns the layer that the polygon at index refers to.

        Time-complexity (without map.): O(1)

        Parameters
        ----------
        index : int
            Index of the polygon.

        Returns
        -------
        int
            Number of the layer.
        """
        if self._layers is None:
            htprint("Status", "Layers are not yet mapped. Start mapping")
            self.map_layers()

        if index == 0:
            return self._layers[0]

        # remove the first one from consideration
        index -= 1
        index = index if index < (self._sector_polys.shape[0] - 1) else index % (self._sector_polys.shape[0] - 1)
        return self._layers[index + 1]

    def get_sector(self, index: int) -> int:
        """
        Returns the sector that the polygon at index refers to.

        Time-complexity: O(1)

        Parameters
        ----------
        index : int
            Index of the polygon.

        Returns
        -------
        int
            Number of the sector.
        """
        if index == 0:
            return 0
        else:
            index -= 1
            return index // (self._sector_polys.shape[0] - 1)

    def get_center(self, index: int) -> np.complex128:
        """
        Returns the center of the polygon at index.

        Time-complexity: O(1)

        Parameters
        ----------
        index : int
            Index of the polygon.

        Returns
        -------
        np.complex128
            Center of the polygon.
        """
        return self[index][0]

    def get_vertices(self, index: int) -> np.array:
        """
        Returns the p vertices of the polygon at index.

        Time-complexity: O(p)

        Parameters
        ----------
        index : int
            Index of the polygon.

        Returns
        -------
        np.array
            Array of shape (p,) containing vertices of the polygon.
        """
        return self[index][1:]

    def get_angle(self, index: int) -> float:
        """
        Returns the angle to the center of the polygon at index.

        Time-complexity: O(1)

        Parameters
        ----------
        index : int
            Index of the polygon.

        Returns
        -------
        np.complex128
            Center of the polygon.
        """
        return np.angle(self[index][0])

    # API ##############################################################################################################
    # Sector only ######################################################################################################

    def _find(self, sector_proj: np.complex128, eps: float = 1e-12) -> int:
        """
        Protected(!)
        Find the polygons index sector_projection belongs to.
        However, sector_projection has to be in the fundamental sector.

        Time-complexity: O(m / p)

        Parameters
        ----------
        sector_proj : np.complex128
            Position to search polygon for.
        eps : float
            Threshold for comparison.

        Returns
        -------
        int
            Index of the corresponding polygon.
        """
        disk_distance = np.vectorize(lambda z: util.f_dist_disc(z, sector_proj))
        dists = disk_distance(self._sector_polys[:, 0])  # m / p
        index = int(np.argmin(dists))  # m / p
        if dists[index] - util.f_dist_disc(self._sector_polys[0, 0], self._sector_polys[1, 0]) / 2 < eps:
            return index
        return False

    def _get_reflection_level_in_sector(self, sector_index: int) -> int:
        """
        Protected(!)
        Returns the reflection level the polygon at index belongs to.

        Time-complexity: O(log(n + 1))

        Parameters
        ----------
        sector_index : int
            Index of the polygon.

        Returns
        -------
        int
            Reflection level.
        """
        pos = np.searchsorted(self._sector_lengths_cumulated, sector_index)
        if self._sector_lengths_cumulated[pos] > sector_index:
            return pos - 1
        return pos

    def _get_nbrs_generative(self, sector_index: int) -> np.array:
        """
        Protected(!)
        Get neighbor of the polygon at sector_index. Has to be in the fundamental sector!

        Time-complexity (single polygon): O(m + p^2)

        Parameters
        ----------
        sector_index : int
            Index of the polygon for whom the neighbors will be searched for.

        Returns
        -------
        np.array
            Indices of the neighbors.
        """
        if sector_index == 0:
            neigbor_centers = util.generate_raw(self._sector_polys[sector_index])  # p^2
            indices = [self.find(e) for e in neigbor_centers]  # p loop execs: m / p
            indices = [e for e in indices if not (e is False)]  # p
            return [i % (self.length - 1) if i != 0 else 0 for i in indices]  # p

        neighbor_centers = util.generate_raw(self._sector_polys[sector_index])
        indices = [self.find(e) for e in neighbor_centers]
        return [e for e in indices if not (e is False)]

    def _get_nbrs_radius(self, sector_index: int, tol: float = 1e-5) -> np.array:
        """
        Protected(!)
        Get neighbor of the polygon at sector_index. Has to be in the fundamental sector!

        Time-complexity (single polygon): O(m / p + n)

        Parameters
        ----------
        sector_index : int
            Index of the polygon for whom the neighbors will be searched for.

        Returns
        -------
        np.array
            Indices of the neighbors.
        """
        if sector_index == 0:
            jump = len(self._sector_polys) - 1
            return [1 + i * jump for i in range(self.p)]

        dist_ref = util.f_dist_disc(self._sector_polys[0, 0], self._sector_polys[1, 0]) + tol
        disk_distance = np.vectorize(lambda z: util.f_dist_disc(z, self._sector_polys[sector_index][0]))

        # sector bulk
        dists = disk_distance(self._sector_polys[:, 0])
        neighbors = np.argwhere(np.logical_and(dists <= dist_ref, dists > 0)).flatten().tolist()

        # sector boundary
        for i in range(1, len(self._sector_lengths)):
            b_l = self._index_from_ref_layer_index(self._sector_lengths_cumulated[i] - 1, i)
            if 0 < disk_distance(self[b_l][0]) <= dist_ref:
                neighbors.append(b_l)
            b_r = self._index_from_ref_layer_index(self._sector_lengths_cumulated[i + 1], i)
            if 0 < disk_distance(self[b_r][0]) <= dist_ref:
                neighbors.append(b_r)

            if len(neighbors) == self.p:
                break

        return neighbors

    def _get_nbrs_geometrical(self, sector_index: int) -> np.array:
        """
        Protected(!)
        Get the neighbors of the polygon at sector_index using an experimental method.
        Has to be in the fundamental sector!

        Time-complexity: O(p^3 + n)

        Parameters
        ----------
        sector_index : int
            Index of the polygon.

        Returns
        -------
        np.array
            Array containing the indices of the neighbors.
        """
        if sector_index == 0:
            return np.array([1 + i * (self._sector_polys.shape[0] - 1) for i in range(self.p)])  # p

        neighbors = np.empty((self.p), dtype=np.uint32)
        c = 0

        ref_layer = self._get_reflection_level_in_sector(sector_index)
        pos_in_layer = sector_index - self._sector_lengths_cumulated[ref_layer]
        # relative position in the reflection layer
        ratio = pos_in_layer / self._sector_lengths[ref_layer]

        # 1. parents
        # calculate position of parent through relative position
        parent_index_candidate = self._sector_lengths_cumulated[ref_layer - 1] + int(
            ratio * self._sector_lengths[ref_layer - 1])
        parent_index = self._wiggle_index(sector_index, parent_index_candidate, tol=2)  # tol p^2 = 2 p^2
        neighbors[c] = parent_index
        c += 1

        # 2. check if next is parent too
        if ref_layer != 1:
            for shift in [1, -1]:
                parent2_candidate = self._index_from_ref_layer_index(neighbors[c - 1] + shift, ref_layer - 1)
                connection = util.any_close_matrix(self._sector_polys[sector_index], self[parent2_candidate])  # p^2
                if connection.shape[0] == 2:
                    neighbors[c] = parent2_candidate
                    c += 1
                    break

        # 3. siblings / cousins
        if self.q == 3:
            # siblings
            neighbors[c] = self._index_from_ref_layer_index(sector_index + 1, ref_layer)
            c += 1
            neighbors[c] = self._index_from_ref_layer_index(sector_index - 1, ref_layer)
            c += 1
        elif self.q & 1:
            # if number is even, it is not a cousin but a nephew and will be find along with the children
            # if odd, exactly one cousin should be found. It is either the next polygon or the before
            for shift in [1, -1]:
                cousin_candidate = self._index_from_ref_layer_index(sector_index + shift, ref_layer)
                connection = util.any_close_matrix(self._sector_polys[sector_index], self[cousin_candidate])  # p^2
                if connection.shape[0] == 2:
                    neighbors[c] = cousin_candidate
                    c += 1
                    break

        # 4. children
        if ref_layer + 1 != len(self._sector_lengths):
            child_index_candidate = self._sector_lengths_cumulated[ref_layer + 1] + int(
                ratio * self._sector_lengths[ref_layer + 1])
            child_index = self._wiggle_index(sector_index, child_index_candidate, tol=3)  # 3 p^2

            # if on boundary no children exist
            if child_index is False:
                return neighbors[:c]

            neighbors[c] = child_index

            side = 1
            start = neighbors[c]
            current = neighbors[c] + side
            c += 1

            left = self.p - c
            steps = 2 * left
            step = 0
            while c < self.p and step < steps:  # 2 * (p - 1) loop execs
                current_index = self._index_from_ref_layer_index(current, ref_layer + 1)
                connection = util.any_close_matrix(self._sector_polys[sector_index], self[current_index])  # p^2
                if connection.shape[0] == 2:
                    neighbors[c] = current_index
                    c += 1
                elif side == 1:
                    # change search direction
                    current = start
                    side = -1
                    current += side
                    continue
                elif side == -1:
                    break

                current += side
                step += 1

        # control boundary child->grand-nephew artifact
        ref_dist = util.f_dist_disc(self._sector_polys[0, 0], self._sector_polys[1, 0])
        for layer_index in range(2, len(self._sector_lengths_cumulated) - 1):  # n loop execs
            if c == self.p:
                break
            for index_ in [self._sector_lengths_cumulated[layer_index] - 1,
                           self._sector_lengths_cumulated[layer_index + 1]]:
                index_b = self._index_from_ref_layer_index(index_, layer_index)
                dist = util.f_dist_disc(self[index_b][0], self._sector_polys[sector_index, 0])
                if util.is_close(dist, ref_dist) and index_b not in neighbors:
                    neighbors[c] = index_b
                    c += 1

        return neighbors[:c]

    def _get_nbrs_mapping(self, sector_index: int) -> np.array:
        """
        Protected(!)
        Get neighbor of the polygon at sector_index. Has to be in the fundamental sector!

        Time-complexity (without map.): O(p)

        Parameters
        ----------
        sector_index : int
            Index of the polygon for whom the neighbors will be searched for.

        Returns
        -------
        np.array
            Indices of the neighbors.
        """
        if self._nbrs is None:
            htprint("Status", "start mapping neighbors")
            self.map_nbrs()  # m[ld(n + 1) / p + p^(log(m)) + ld(m / p) / p]
        neighbor_indices = self._nbrs[sector_index]

        # get value from nice little overflow
        overflow = np.iinfo(neighbor_indices.dtype).max
        return neighbor_indices[np.argwhere(neighbor_indices != overflow)].flatten()  # p

    # Sector only ######################################################################################################
    # Generative #######################################################################################################

    def get_polygon(self, index: int) -> HyperPolygon:
        """
        Returns the polygon at index as HyperPolygon object.

        Parameters
        ----------
        index : int
            Index of the polygon.

        Returns
        -------
        HyperPolygon
            Polygon at index.
        """
        htprint("Warning", "Method exists only for compatibility reasons. Usage is discouraged!")

        polygon = HyperPolygon(self.p, )
        polygon.idx = index
        polygon.layer = self.get_reflection_level(index)
        polygon.sector = self.get_sector(index)
        polygon.angle = self.get_angle(index)
        polygon.orientation = None
        polygon.set_polygon(self[index])

        return polygon

    def find(self, v: np.complex128) -> int:
        """
        Find the polygons index v belongs to.

        Time-complexity: O(m / p + p)

        Parameters
        ----------
        v : complex
            Position to search polygon for.

        Returns
        -------
        int
            Index of the corresponding polygon.
        """
        angle = np.angle(v)
        factor = int(np.floor(angle / (PI2 / self.p)))
        for modify in [0, 1, -1]:
            modi = factor + modify
            modi = modi if modi >= 0 else modi + self.p
            sector_proj = v * np.exp(-(modi * PI2 / self.p) * 1j) if modi != 0 else v  # p + 1
            index = self._find(sector_proj)  # m / p
            if index:
                index = int(index + (self._sector_polys.shape[0] - 1) * modi)
                return (index + self.length) % self.length
            elif not (index is False):
                return 0

        return False

    def get_reflection_level(self, index) -> int:
        """
        Get the neighbors of a polygon at index.
        Time-complexity: O(log(n + 1))

        Parameters
        ----------
        index : int
            Index of the polygon.

        Returns
        -------
        np.array
            Array containing the indices of the neighbors.
        """
        if index == 0:
            return 0

        index -= 1
        index %= (self._sector_polys.shape[0] - 1)
        index += 1
        return self._get_reflection_level_in_sector(index)  # log(n + 1)

    def get_nbrs(self, i, method="mapping"):
        """
        Get the neighbors of a polygon at index with method.

        Parameters
        ----------
        i : int
            Index of the polygon.
        method : str
            Method to use.

        Returns
        -------
        np.array
            Array containing the indices of the neighbors.
        """
        if len(self) == 1:
            htprint("Warning", "Tiling consists of one polygon!")
            return []
        methods = {"mapping": self.get_nbrs_mapping,
                   "generative": self.get_nbrs_generative,
                   "radius": self.get_nbrs_radius,
                   "geometrical": self.get_nbrs_geometrical}
        return methods[method](i)

    def get_nbrs_generative(self, index: int) -> np.array:
        """
        Get the neighbors of a polygon at index.
        Time-complexity: O(m + p^2)

        Parameters
        ----------
        index : int
            Index of the polygon.

        Returns
        -------
        np.array
            Array containing the indices of the neighbors.
        """
        if len(self) == 1:
            htprint("Warning", "Tiling consists of one polygon!")
            return []
        return self._expand_sector_index_to_tiling(index, self._get_nbrs_generative)

    def get_nbrs_geometrical(self, index: int) -> np.array:
        """
        Get the neighbors of the polygon at index using an experimental method.
        Time-complexity: O(?)

        Parameters
        ----------
        index : int
            Index of the polygon.

        Returns
        -------
        np.array
            Array containing the indices of the neighbors.
        """
        if len(self) == 1:
            htprint("Warning", "Tiling consists of one polygon!")
            return []
        return self._expand_sector_index_to_tiling(index, self._get_nbrs_geometrical)

    def get_nbrs_mapping(self, index: int) -> np.array:
        """
        Get neighbor of the polygon at index.
        Time-complexity (single polygon): O(p)

        Parameters
        ----------
        index : int
            Index of the polygon for whom the neighbors will be searched for.

        Returns
        -------
        np.array
            Indices of the neighbors.
        """
        if len(self) == 1:
            htprint("Warning", "Tiling consists of one polygon!")
            return []
        return self._expand_sector_index_to_tiling(index, self._get_nbrs_mapping)

    def get_nbrs_radius(self, index: int) -> np.array:
        """
        Get the neighbors of a polygon at index.
        Time-complexity: O(m / p)

        Parameters
        ----------
        index : int
            Index of the polygon.

        Returns
        -------
        np.array
            Array containing the indices of the neighbors.
        """
        if len(self) == 1:
            htprint("Warning", "Tiling consists of one polygon!")
            return []
        return self._expand_sector_index_to_tiling(index, self._get_nbrs_radius)

    # Generative #######################################################################################################
    # Transformations ##################################################################################################

    def transform(self, function: Callable):
        """
        Applies function to each polygon.

        Parameters
        ----------
        function : callable
            Function to apply on each polygon.

        Time-complexity: O(m / p)

        Returns
        -------
        void
        """
        raise NotImplementedError(
            '[hypertiling]: Error: The requested function is not implemented! Please use a different kernel!')
        if not isinstance(function, np.vectorize):
            function = np.vectorize(function)
        self._sector_polys = function(self._sector_polys)

    def rotate(self, angle: float):
        """
        Rotates the grid around angle.

        Parameters
        ----------
        angle : float
            Angle to rotate the polygon.

        Time-complexity: O(m / p)

        Returns
        -------
        void
        """
        raise NotImplementedError(
            '[hypertiling]: Error: The requested function is not implemented! Please use a different kernel!')
        self.transform(lambda x: transform.moeb_rotate_trafo(-angle, x))

    def translate(self, z: np.complex128):
        """
        Translates the grid to z.

        Parameters
        ----------
        z : complex
            Position of the new origin.

        Time-complexity: O(m / p)

        Returns
        -------
        void
        """
        raise NotImplementedError(
            '[hypertiling]: Error: The requested function is not implemented! Please use a different kernel!')
        self.transform(lambda x: transform.moeb_origin_trafo(z, x))

    # Transformations ##################################################################################################


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    import time

    fig_ax = plt.subplots()
    fig_ax[1].set_xlim(-1, 1)
    fig_ax[1].set_ylim(-1, 1)
    fig_ax[1].set_box_aspect(1)
    t1 = time.time()
    tiling = GenerativeReflection(7, 3, 4)
    t2 = time.time()
    print(tiling.length)
    # print(tiling.get_nbrs_geometrical(3))
    # print(tiling.get_nbrs(3))

    print(f"Polygons in total :{len(tiling)}")
    print(f"Polygons in sector:{len(tiling._sector_polys)}")
    print(f"Took: {t2 - t1: .4f} s")

    # tiling.check_integrity()
    colors = ["#FF000080", "#00FF0080", "#0000FF80"]

    for polygon_index, pgon in enumerate(tiling):
        # print(polygon_index)
        # print(polygon_index, pgon)
        # poly_layer = tiling.get_layer(polygon_index)
        poly_layer = tiling.get_reflection_level(polygon_index)
        facecolor = colors[poly_layer % len(colors)]
        patch = mpl.patches.Polygon(np.array([(np.real(e), np.imag(e)) for e in pgon[1:]]),
                                    facecolor=facecolor, edgecolor="#FFFFFF")
        fig_ax[1].add_patch(patch)
        fig_ax[1].text(np.real(pgon[0]), np.imag(pgon[0]), str(polygon_index))

    plt.show()
