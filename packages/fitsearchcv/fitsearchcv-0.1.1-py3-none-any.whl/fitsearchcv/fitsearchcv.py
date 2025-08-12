import itertools
import numbers
import numpy as np
from copy import deepcopy
from joblib import Parallel, delayed
from sklearn.model_selection import check_cv
from sklearn.metrics import get_scorer
from sklearn.utils.multiclass import type_of_target

def _positional_slice(obj, idx):
    """Safely slice numpy arrays, pandas DataFrames, or Series by position."""
    if hasattr(obj, "iloc"):  # pandas object
        return obj.iloc[idx]
    return obj[idx]

def _expand_param_grid(param_grid):
    """Expand dict or list of dicts into a list of all param combinations."""
    if isinstance(param_grid, dict):
        grids = [param_grid]
    elif isinstance(param_grid, (list, tuple)):
        grids = param_grid
    else:
        raise TypeError("param_grid must be dict or list of dicts")

    combos = []
    for grid in grids:
        keys = list(grid.keys())
        values = [v if isinstance(v, (list, tuple)) else [v] for v in grid.values()]
        for combo in itertools.product(*values):
            combos.append(dict(zip(keys, combo)))
    return combos

def _resolve_scorers(scoring, estimator):
    """Convert scoring into dict of {name: callable}."""
    if scoring is None:
        if not hasattr(estimator, "score"):
            raise ValueError("If scoring is None, estimator must have a .score method.")
        return {"score": get_scorer(None)}
    if isinstance(scoring, str):
        return {"score": get_scorer(scoring)}
    if callable(scoring):
        return {"score": scoring}
    if isinstance(scoring, (list, tuple)):
        return {name: get_scorer(name) for name in scoring}
    if isinstance(scoring, dict):
        out = {}
        for name, sc in scoring.items():
            out[name] = get_scorer(sc) if isinstance(sc, str) else sc
        return out
    raise TypeError("Invalid scoring format.")

def _fit_and_score_one_split(estimator, X, y, train_idx, test_idx, scorer, params):
    """Fit and score on one CV split."""
    est = deepcopy(estimator)
    est.set_params(**params)

    X_train = _positional_slice(X, train_idx)
    X_test  = _positional_slice(X, test_idx)
    y_train = _positional_slice(y, train_idx) if y is not None else None
    y_test  = _positional_slice(y, test_idx)  if y is not None else None

    est.fit(X_train, y_train)
    train_scores = {name: func(est, X_train, y_train) for name, func in scorer.items()}
    test_scores = {name: func(est, X_test, y_test) for name, func in scorer.items()}
    return train_scores, test_scores

class FitSearchCV:
    def __init__(self, estimator, param_grid, scoring=None, cv=5, n_jobs=None, refit=True, verbose=0):
        self.estimator = estimator
        self.param_grid = param_grid
        self.scoring = scoring
        self.cv = cv
        self.n_jobs = n_jobs
        self.refit = refit
        self.verbose = verbose

    def fit(self, X, y=None):
        param_combos = _expand_param_grid(self.param_grid)
        scorers = _resolve_scorers(self.scoring, self.estimator)
        cv = check_cv(self.cv, y, classifier=type_of_target(y) in ("binary", "multiclass"))

        results = {f"mean_train_{name}": [] for name in scorers}
        results.update({f"mean_test_{name}": [] for name in scorers})
        results["params"] = []

        for params in param_combos:
            if self.verbose:
                print(f"Testing parameters: {params}")

            scores = Parallel(n_jobs=self.n_jobs)(
                delayed(_fit_and_score_one_split)(
                    self.estimator, X, y, train_idx, test_idx, scorers, params
                )
                for train_idx, test_idx in cv.split(X, y)
            )

            train_means = {name: np.mean([s[0][name] for s in scores]) for name in scorers}
            test_means = {name: np.mean([s[1][name] for s in scores]) for name in scorers}

            for name in scorers:
                results[f"mean_train_{name}"].append(train_means[name])
                results[f"mean_test_{name}"].append(test_means[name])
            results["params"].append(params)

        self.cv_results_ = results
        self.best_index_ = self._select_best_index(list(scorers.keys()))
        self.best_params_ = results["params"][self.best_index_]

        if self.refit:
            self.best_estimator_ = deepcopy(self.estimator)
            self.best_estimator_.set_params(**self.best_params_)
            self.best_estimator_.fit(X, y)
        return self

    def _selection_metric_name(self, scorer_names):
        if isinstance(self.refit, str):
            return self.refit
        return scorer_names[0]

    def _select_best_index(self, scorer_names):
        metric = self._selection_metric_name(scorer_names)

        mean_train=self.cv_results_[f"mean_train_{metric}"]
        mean_test=self.cv_results_[f"mean_test_{metric}"]

        x1=mean_train-mean_test
        x2=1-mean_test

        avg_score=(x1+x2)/2

        return int(np.argmin(avg_score))

    def predict(self, X):
        if not hasattr(self, "best_estimator_"):
            raise ValueError("Call fit before predict.")
        return self.best_estimator_.predict(X)
