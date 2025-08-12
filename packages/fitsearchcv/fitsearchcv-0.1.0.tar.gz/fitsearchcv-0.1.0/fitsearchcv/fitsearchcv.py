import itertools # generate all possible combinations
import numbers # checks if a variable is a number
import numpy as np 
from copy import deepcopy # for copying models
from joblib import Parallel, delayed # for parallel processing
from sklearn.model_selection import check_cv  
from sklearn.metrics import get_scorer
from sklearn.utils.multiclass import type_of_target


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


def _fit_and_score_one_split(estimator, X, y, train_idx, test_idx, params, scorers,
                             return_train, error_score):
    """Fit estimator on one split and score."""
    est = deepcopy(estimator)
    est.set_params(**params)

    X_train, X_test = X[train_idx], X[test_idx]
    y_train = y[train_idx] if y is not None else None
    y_test = y[test_idx] if y is not None else None

    out = {}
    try:
        est.fit(X_train, y_train)

        for name, scorer in scorers.items():
            try:
                out[f"test_{name}"] = scorer(est, X_test, y_test)
            except Exception:
                if error_score == "raise":
                    raise
                out[f"test_{name}"] = float(error_score)

        if return_train:
            for name, scorer in scorers.items():
                try:
                    out[f"train_{name}"] = scorer(est, X_train, y_train)
                except Exception:
                    if error_score == "raise":
                        raise
                    out[f"train_{name}"] = float(error_score)

    except Exception:
        if error_score == "raise":
            raise
        for name in scorers.keys():
            out[f"test_{name}"] = float(error_score)
            if return_train:
                out[f"train_{name}"] = float(error_score)

    return out


class FitSearchCV:
    def __init__(self, estimator, param_grid, *, scoring=None, n_jobs=None,
                 refit=True, cv=None, verbose=0, pre_dispatch="2*n_jobs",
                 error_score=np.nan, return_train_score=True):
        self.estimator = estimator
        self.param_grid = param_grid
        self.scoring = scoring
        self.n_jobs = n_jobs
        self.refit = refit
        self.cv = cv
        self.verbose = verbose
        self.pre_dispatch = pre_dispatch
        self.error_score = error_score
        self.return_train_score = return_train_score

    def fit(self, X, y=None, groups=None):
        cv = check_cv(self.cv, y,
                      classifier=(type_of_target(y) in ("binary", "multiclass", "multilabel-indicator")))
        splits = list(cv.split(X, y, groups))
        self.n_splits_ = len(splits)

        param_combos = _expand_param_grid(self.param_grid)
        scorers = _resolve_scorers(self.scoring, self.estimator)
        scorer_names = list(scorers.keys())

        def evaluate_params(params):
            split_results = []
            for train_idx, test_idx in splits:
                res = _fit_and_score_one_split(self.estimator, X, y, train_idx, test_idx,
                                               params, scorers, self.return_train_score, self.error_score)
                split_results.append(res)
            return split_results

        parallel = Parallel(n_jobs=self.n_jobs, verbose=self.verbose, pre_dispatch=self.pre_dispatch)
        all_results = parallel(delayed(evaluate_params)(params) for params in param_combos)

        results = {}
        for j in range(self.n_splits_):
            for name in scorer_names:
                results[f"split{j}_test_{name}"] = np.array([r[j][f"test_{name}"] for r in all_results])
                if self.return_train_score:
                    results[f"split{j}_train_{name}"] = np.array([r[j][f"train_{name}"] for r in all_results])

        for name in scorer_names:
            test_scores = np.vstack([results[f"split{j}_test_{name}"] for j in range(self.n_splits_)])
            results[f"mean_test_{name}"] = np.mean(test_scores, axis=0)
            results[f"std_test_{name}"] = np.std(test_scores, axis=0, ddof=0)

            if self.return_train_score:
                train_scores = np.vstack([results[f"split{j}_train_{name}"] for j in range(self.n_splits_)])
                results[f"mean_train_{name}"] = np.mean(train_scores, axis=0)
                results[f"std_train_{name}"] = np.std(train_scores, axis=0, ddof=0)

            ranks = np.argsort(-results[f"mean_test_{name}"], kind="mergesort")
            rank_scores = np.empty_like(ranks)
            rank_scores[ranks] = np.arange(1, len(ranks) + 1)
            results[f"rank_test_{name}"] = rank_scores

        results["params"] = param_combos
        self.cv_results_ = results

        self.best_index_ = self._select_best_index(scorer_names)
        self.best_params_ = param_combos[self.best_index_]
        self.best_score_ = results[f"mean_test_{self._selection_metric_name(scorer_names)}"][self.best_index_]

        if self.refit:
            if self.verbose:
                print(f"Refitting best model with params={self.best_params_}")
            self.best_estimator_ = deepcopy(self.estimator).set_params(**self.best_params_)
            self.best_estimator_.fit(X, y)
        else:
            self.best_estimator_ = None

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
        if self.best_estimator_ is None:
            raise ValueError("Refit was not done.")
        return self.best_estimator_.predict(X)

    def score(self, X, y=None):
        if self.best_estimator_ is None:
            raise ValueError("Refit was not done.")
        return self.best_estimator_.score(X, y)