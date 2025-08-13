from concurrent.futures import ProcessPoolExecutor

import numpy as np
import scipy
from PIL import Image
from PIL import ImageDraw
from tqdm.auto import tqdm

from geoletrld.distances.DistanceInterface import DistanceInterface
from geoletrld.utils import Trajectory, Trajectories
from skimage.transform import hough_line


class ShapeDistance(DistanceInterface):
    def __init__(self, agg=np.sum, resolution=(480, 480), use_accumulator=False, use_fft=False, angle_step=1,
                 n_jobs=1, verbose=False):
        self.agg = agg
        self.resolution = resolution
        self.use_accumulator = use_accumulator
        self.use_fft = use_fft
        self.angle_step = angle_step

        if use_fft and not use_accumulator:
            raise ValueError("use_fft is only available with use_accumulator=True")

        self.n_jobs = n_jobs
        self.verbose = verbose

    def transform(self, trajectories: Trajectories, geolets: Trajectories) -> tuple:
        if self.n_jobs == 1:
            distances = np.zeros((len(trajectories), len(geolets)))
            best_idx = np.zeros((len(trajectories), len(geolets)), dtype=int)

            for i, (_, trajectory) in enumerate(tqdm(trajectories.items(), disable=not self.verbose)):
                distances[i], best_idx[i] = self._compute_dist_geolets_trajectory(trajectory, geolets)

            return distances, best_idx
        else:
            executor = ProcessPoolExecutor(max_workers=self.n_jobs)
            processes = []
            for _, trajectory in trajectories.items():
                processes += [
                    executor.submit(self._compute_dist_geolets_trajectory, trajectory, geolets)
                ]

            distances = np.zeros((len(trajectories), len(geolets)))
            best_idx = np.zeros((len(trajectories), len(geolets)), dtype=int)

            for i, process in enumerate(tqdm(processes, disable=not self.verbose)):
                distances[i], best_idx[i] = process.result()

            return distances, best_idx

    def _compute_dist_geolets_trajectory(self, trajectory: Trajectory, geolets: Trajectories):
        distances = np.zeros(len(geolets))
        best_idx = np.zeros(len(geolets))
        for i, (_, geolet) in enumerate(geolets.items()):
            distances[i], best_idx[i] = ShapeDistance.best_fitting(
                trajectory=trajectory,
                geolet=geolet.normalize(),
                agg=self.agg,
                resolution=self.resolution,
                use_fft=self.use_fft,
                angle_step=self.angle_step
            )

        return distances, best_idx

    @staticmethod
    def best_fitting(
            trajectory: Trajectory,
            geolet: Trajectory,
            agg=np.sum,
            resolution=(480, 480),
            use_accumulator=False,
            use_fft=False,
            angle_step=1,
    ) -> tuple:
        tested_angles = np.linspace(-np.pi / 2, np.pi / 2, int(180 / angle_step), endpoint=False)

        img_geo = ShapeDistance.draw_image(geolet, resolution=resolution, padding=1)
        img_trj = ShapeDistance.draw_image(trajectory, resolution=resolution, padding=1)

        h_geo, theta_geo, d_geo = hough_line(np.array(img_geo), theta=tested_angles)
        h_trj, theta_trj, d_trj = hough_line(np.array(img_trj), theta=tested_angles)
        dist_geo, dist_trj = np.log(1 + h_geo), np.log(1 + h_trj)

        if not use_accumulator:
            dist_geo, dist_trj = dist_geo.sum(axis=0), dist_trj.sum(axis=0)

        if use_fft:
            dist_geo, dist_trj = np.abs(scipy.fft.fft(dist_geo)), np.abs(scipy.fft.fft(dist_trj))

        return np.linalg.norm(dist_geo - dist_trj), 0

    @staticmethod
    def draw_image(lines:Trajectory, resolution=(480, 480), padding=10, verbose=False):
        min_x, max_x = lines.longitude.min(), lines.longitude.max()
        min_y, max_y = lines.latitude.min(), lines.latitude.max()

        if verbose:
            print(min_x, max_x, min_y, max_y, '\r\n', resolution)

        image = Image.new("1", resolution, "black")
        draw = ImageDraw.Draw(image)

        scale_x = (resolution[0] - 2 * padding) / (max_x - min_x)
        scale_y = (resolution[1] - 2 * padding) / (max_y - min_y)

        scale = min(scale_x, scale_y)

        for line in zip((lines.longitude[:-1] - min_x) * scale + padding,
                        (lines.latitude[:-1] - min_y) * scale + padding,
                        (lines.longitude[1:] - min_x) * scale + padding,
                        (lines.latitude[1:] - min_y) * scale + padding):
            draw.line(line, fill="white", width=1)

        return image

    def __str__(self):
        return f"Euclidean({self.agg.__name__}, {self.n_jobs}, {self.verbose})"
