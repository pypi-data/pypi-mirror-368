import math
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from scipy.optimize import Bounds, shgo
from tqdm.auto import tqdm

from geoletrld.distances.DistanceInterface import DistanceInterface
from geoletrld.distances._DistancesUtils import rotate
from geoletrld.utils import Trajectory, Trajectories
from geoletrld.distances import EuclideanDistance


class RotatingGenericDistance(DistanceInterface):
    def __init__(self, distance, return_rot: bool = False, n_jobs=1, verbose=False):
        self.distance = distance
        self.distance.n_jobs = n_jobs
        self.return_rot = return_rot

        self.n_jobs = n_jobs
        self.verbose = verbose

    def transform(self, trajectories: Trajectories, geolets: Trajectories) -> tuple:
        distances = np.zeros((len(trajectories), len(geolets)))
        best_idx = np.zeros((len(trajectories), len(geolets)), dtype=int)
        angles = np.zeros((len(trajectories), len(geolets)))

        if self.n_jobs == 1:
            for i, (_, trajectory) in enumerate(tqdm(trajectories.items(), disable=not self.verbose)):
                distances[i], best_idx[i], angles[i] = self._compute_dist_geolets_trajectory(trajectory, geolets)
        else:
            executor = ProcessPoolExecutor(max_workers=self.n_jobs)
            processes = []
            for _, trajectory in trajectories.items():
                processes += [
                    executor.submit(self._compute_dist_geolets_trajectory, trajectory, geolets)
                ]

            for i, process in enumerate(tqdm(processes, disable=not self.verbose)):
                res = process.result()
                distances[i], best_idx[i] = res[0], res[1]
                if self.return_rot:
                    angles[i] = res[2]

        if self.return_rot:
            return np.hstack([distances, angles]), best_idx
        else:
            return distances, best_idx

    def _compute_dist_geolets_trajectory(self, trajectory: Trajectory, geolets: Trajectories):
        distances = np.zeros(len(geolets))
        best_idx = np.zeros(len(geolets))
        angles = np.zeros(len(geolets))
        for i, (_, geolet) in enumerate(geolets.items()):
            distances[i], best_idx[i], angles[i] = RotatingGenericDistance.best_fitting(
                trajectory=trajectory,
                geolet=geolet.normalize(),
                distance=self.distance,
                return_rot=True
            )
        if self.return_rot:
            return distances, best_idx, angles
        else:
            return distances, best_idx

    @staticmethod
    def best_fitting(trajectory: Trajectory, geolet: Trajectory, distance, return_rot: bool = False) -> tuple:
        bounds = Bounds([0], [2 * math.pi], )
        result = shgo(_objective_function, sampling_method="sobol", args=(trajectory, geolet, distance), bounds=bounds)
        angle = result.x
        dist, idx = distance.best_fitting(trajectory=trajectory, geolet=rotate(geolet, angle))

        if return_rot:
            return dist, idx, angle
        else:
            return dist, idx

    def __str__(self):
        return f"Rotating({self.distance}, {self.return_rot}, {self.n_jobs}, {self.verbose})"


def _objective_function(angle, trajectory: Trajectory, geolet: Trajectory, distance):
    rotated_geolet = rotate(geolet.copy(), angle)

    geolets = Trajectories()
    geolets["demo"] = rotated_geolet

    return distance._compute_dist_geolets_trajectory(trajectory=trajectory, geolets=geolets)[0][0]
