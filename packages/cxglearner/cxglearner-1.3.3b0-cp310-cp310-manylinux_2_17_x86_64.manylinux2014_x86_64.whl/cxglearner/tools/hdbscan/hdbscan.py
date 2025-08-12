import numpy as np
from warnings import warn

try:
    import cuml
    from hdbscan.prediction import PredictionData, DistanceMetric
    HDBSCAN = cuml.cluster.hdbscan.HDBSCAN
    PD = PredictionData
except:
    import hdbscan
    from hdbscan.prediction import PredictionData, DistanceMetric
    HDBSCAN = hdbscan.HDBSCAN


class OPD(PredictionData):
    def __init__(self, data, mirror_data, condensed_tree, min_samples,
                 tree_type='kdtree', metric='euclidean', **kwargs):
        super(OPD, self).__init__(data, condensed_tree, min_samples, tree_type, metric, **kwargs)
        self.raw_data = data.astype(np.float64)
        if mirror_data is not None: get_data = mirror_data
        else: get_data = self.raw_data
        self.tree = self._tree_type_map[tree_type](self.raw_data,
                                                   metric=metric, **kwargs)
        self.core_distances = self.tree.query(data, k=min_samples)[0][:, -1]
        self.dist_metric = DistanceMetric.get_metric(metric, **kwargs)
        selected_clusters = sorted(condensed_tree._select_clusters())
        # raw_condensed_tree = condensed_tree.to_numpy()
        raw_condensed_tree = condensed_tree._raw_tree

        self.cluster_map = {c: n for n, c in enumerate(sorted(list(selected_clusters)))}
        self.reverse_cluster_map = {n: c for c, n in self.cluster_map.items()}

        self.cluster_tree = raw_condensed_tree[raw_condensed_tree['child_size'] > 1]
        self.max_lambdas = {}
        self.leaf_max_lambdas = {}
        self.exemplars = []

        all_clusters = set(np.hstack([self.cluster_tree['parent'],
                                      self.cluster_tree['child']]))

        for cluster in all_clusters:
            self.leaf_max_lambdas[cluster] = raw_condensed_tree['lambda_val'][
                raw_condensed_tree['parent'] == cluster].max()

        for cluster in selected_clusters:
            self.max_lambdas[cluster] = \
                raw_condensed_tree['lambda_val'][raw_condensed_tree['parent'] == cluster].max()

            for sub_cluster in self._clusters_below(cluster):
                self.cluster_map[sub_cluster] = self.cluster_map[cluster]
                self.max_lambdas[sub_cluster] = self.max_lambdas[cluster]

            cluster_exemplars = np.array([], dtype=np.int64)
            for leaf in self._recurse_leaf_dfs(cluster):
                leaf_max_lambda = raw_condensed_tree['lambda_val'][
                    raw_condensed_tree['parent'] == leaf].max()
                points = raw_condensed_tree['child'][
                    (raw_condensed_tree['parent'] == leaf)
                    & (raw_condensed_tree['lambda_val'] == leaf_max_lambda)
                    ]
                cluster_exemplars = np.hstack([cluster_exemplars, points])

            self.exemplars.append(get_data[cluster_exemplars])


class OHDBSCANCPU(HDBSCAN):
    def generate_prediction_data(self):

        from hdbscan.hdbscan_ import FAST_METRICS, KDTREE_VALID_METRICS, BALLTREE_VALID_METRICS
        if self.metric in FAST_METRICS:
            min_samples = self.min_samples or self.min_cluster_size
            if self.metric in KDTREE_VALID_METRICS:
                tree_type = "kdtree"
            elif self.metric in BALLTREE_VALID_METRICS:
                tree_type = "balltree"
            else:
                warn("Metric {} not supported for prediction data!".format(self.metric))
                return

            if hasattr(self, "mirror_data"): mirror_data = self.mirror_data
            else: mirror_data = None

            self._prediction_data = OPD(
                self._raw_data,
                mirror_data,
                self.condensed_tree_,
                min_samples,
                tree_type=tree_type,
                metric=self.metric,
                **self._metric_kwargs
            )
        else:
            warn(
                "Cannot generate prediction data for non-vector"
                "space inputs -- access to the source data rather"
                "than mere distances is required!"
            )


class OHDBSCAN(HDBSCAN):
    @property
    def prediction_data_(self):

        if not self.prediction_data:
            raise ValueError(
                'Train model with fit(prediction_data=True). or call '
                'model.generate_prediction_data()')

        if self.prediction_data_obj is None:
            from sklearn.neighbors import KDTree, BallTree
            from hdbscan.prediction import PredictionData

            FAST_METRICS = KDTree.valid_metrics + \
                           BallTree.valid_metrics + ["cosine", "arccos"]

            if self.metric in FAST_METRICS:
                min_samples = self.min_samples or self.min_cluster_size
                if self.metric in KDTree.valid_metrics:
                    tree_type = "kdtree"
                elif self.metric in BallTree.valid_metrics:
                    tree_type = "balltree"
                else:
                    warn("Metric {} not supported"
                         "for prediction data!".format(self.metric))
                    return

            if hasattr(self, "mirror_data"): mirror_data = self.mirror_data
            else: mirror_data = None

            if hasattr(self, "umap_states"): umap_states = self.umap_states
            else: umap_states = self.X_m.to_output("numpy")

            self.prediction_data_obj = OPD(
                umap_states,
                mirror_data,
                self.condensed_tree_,
                min_samples,
                tree_type=tree_type,
                metric=self.metric)

        return self.prediction_data_obj
