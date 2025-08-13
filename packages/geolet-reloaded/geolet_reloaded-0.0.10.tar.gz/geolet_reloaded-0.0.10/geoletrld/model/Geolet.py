import copy
import random
from typing import Any

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin, TransformerMixin

from geoletrld.distances import DistanceInterface
from geoletrld.partitioners import PartitionerInterface
from geoletrld.selectors import SelectorInterface
from geoletrld.utils import Trajectories


class Geolet(BaseEstimator, ClassifierMixin, TransformerMixin):
    def __init__(self,
                 partitioner: PartitionerInterface,
                 selector: SelectorInterface,
                 distance: DistanceInterface,
                 model_to_fit: BaseEstimator = None,
                 subset_candidate_geolet: int | float = None,
                 subset_trj_in_selection: int | float = None,
                 verbose: bool = False
                 ):
        if not isinstance(partitioner, PartitionerInterface):
            raise ValueError('Partitioner must be an instance of PartitionerInterface')

        if not isinstance(selector, SelectorInterface):
            raise ValueError('Selector must be an instance of SelectorInterface')

        if not isinstance(distance, DistanceInterface):
            raise ValueError('Distance must be an instance of DistanceInterface')

        if model_to_fit is not None and not isinstance(model_to_fit, BaseEstimator):
            raise ValueError('Model_to_fit must be an instance of ClassifierMixin')

        self.partitioner = partitioner
        self.selector = selector
        self.distance = distance
        self.model_to_fit = model_to_fit
        self.subset_candidate_geolet = subset_candidate_geolet
        self.subset_trj_in_selection = subset_trj_in_selection
        self.verbose = verbose

        self.selected_geolets_scores = None
        self.selected_geolets = None

    def fit(self, X: Trajectories, y: np.ndarray = None):
        if y is None:
            y = np.array([-1]*len(X))

        if self.subset_trj_in_selection is not None and type(self.subset_trj_in_selection) is float:
            self.subset_trj_in_selection = int(len(X) * self.subset_trj_in_selection)

        self.candidate_geolets = self.partitioner.transform(X)

        if self.subset_candidate_geolet is not None and type(self.subset_candidate_geolet) is float:
            self.subset_candidate_geolet = int(len(X) * self.subset_candidate_geolet)

        if self.verbose:
            print(f"Found {len(self.candidate_geolets)} candidate geolet")

        if self.subset_candidate_geolet is not None:
            candidate_geolets_to_delete = random.sample(list(self.candidate_geolets.keys()),
                                                        k=max(0,
                                                              len(self.candidate_geolets) -
                                                              self.subset_candidate_geolet))

            for geo_id in candidate_geolets_to_delete:
                self.candidate_geolets.pop(geo_id)

        self.sub_x = copy.deepcopy(X)
        self.sub_y = copy.deepcopy(y)
        if self.subset_trj_in_selection is not None:
            candidate_trj_to_keep = random.sample(list(zip(self.sub_x.keys(), range(len(y)))),
                                                  k=min(len(X), self.subset_trj_in_selection))

            candidate_trj_to_keep_keys = [x for x, _ in candidate_trj_to_keep]
            for trj_id in X.keys():
                if trj_id not in candidate_trj_to_keep_keys:
                    self.sub_x.pop(trj_id)

            self.sub_y = copy.deepcopy(y[[x for _, x in candidate_trj_to_keep]])

        self.selected_geolets, self.selected_geolets_scores = self.selector.select(geolets=self.candidate_geolets,
                                                                                   trajectories=self.sub_x,
                                                                                   y=self.sub_y)

        if self.model_to_fit is not None:
            self.dist_matrix_fit, self.best_i_fit = self.distance.transform(trajectories=X,
                                                                            geolets=self.selected_geolets)
            self.model_to_fit.fit(X=self.dist_matrix_fit, y=y)

        return self

    def transform(self, X: Trajectories, y: np.ndarray = None):
        self.dist_matrix, self.best_i = self.distance.transform(trajectories=X, geolets=self.selected_geolets)

        return self.dist_matrix

    def predict(self, X: Trajectories):
        if self.model_to_fit is None:
            raise ValueError('No model to fit')

        self.dist_matrix, self.best_i = self.distance.transform(trajectories=X, geolets=self.selected_geolets)

        return self.model_to_fit.predict(self.dist_matrix)

    def get_feature_names_out(self, input_features=None):
        return self.selected_geolets.keys()
