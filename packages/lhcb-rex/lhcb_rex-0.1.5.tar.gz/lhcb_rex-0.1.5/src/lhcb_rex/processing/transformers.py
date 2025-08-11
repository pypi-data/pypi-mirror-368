import numpy as np
from sklearn.preprocessing import QuantileTransformer
from scipy import stats
import re

_residualfrac_limit = 5.0


def inverse_symlog(y, linthresh=1, base=10):
    return np.sign(y) * linthresh * (base ** np.abs(y) - 1)


def symlog(x, linthresh=1, base=10):
    return np.sign(x) * np.log1p(np.abs(x) / linthresh) / np.log(base)


def invsymlog(y, linthresh=1.0):
    sign = np.sign(y)
    abs_y = np.abs(y)
    return sign * linthresh * (10**abs_y - 1)


def np_based_qt_transform(X_col, quantiles, inverse):
    """Private function to transform a single feature."""

    quantiles = np.squeeze(quantiles)

    BOUNDS_THRESHOLD = 1e-7
    n_quantiles_ = np.shape(quantiles)[0]
    references_ = np.linspace(0, 1, n_quantiles_, endpoint=True)

    output_distribution = "normal"

    if not inverse:
        lower_bound_x = quantiles[0]
        upper_bound_x = quantiles[-1]
        lower_bound_y = 0
        upper_bound_y = 1
    else:
        lower_bound_x = 0
        upper_bound_x = 1
        lower_bound_y = quantiles[0]
        upper_bound_y = quantiles[-1]
        X_col = stats.norm.cdf(X_col)

    lower_bounds_idx = X_col - BOUNDS_THRESHOLD < lower_bound_x
    upper_bounds_idx = X_col + BOUNDS_THRESHOLD > upper_bound_x

    isfinite_mask = ~np.isnan(X_col)
    X_col_finite = X_col[isfinite_mask]

    if not inverse:
        X_col[isfinite_mask] = 0.5 * (
            np.interp(X_col_finite, quantiles, references_)
            - np.interp(-X_col_finite, -quantiles[::-1], -references_[::-1])
        )
    else:
        X_col[isfinite_mask] = np.interp(X_col_finite, references_, quantiles)

    X_col[upper_bounds_idx] = upper_bound_y
    X_col[lower_bounds_idx] = lower_bound_y
    if not inverse:
        with np.errstate(invalid="ignore"):
            if output_distribution == "normal":
                X_col = stats.norm.ppf(X_col)
                clip_min = stats.norm.ppf(BOUNDS_THRESHOLD - np.spacing(1))
                clip_max = stats.norm.ppf(1 - (BOUNDS_THRESHOLD - np.spacing(1)))
                X_col = np.clip(X_col, clip_min, clip_max)

    return X_col


class UpdatedTransformer:
    def __init__(self, min_maxes=None, use_min_max_for_mom_deltas=True):
        self.qt_fit = False
        self.clip_value = 4.0
        if min_maxes:
            self.min_maxes = min_maxes
        self.use_min_max_for_mom_deltas = use_min_max_for_mom_deltas

    def fit_data(self, data_raw, column, n_quantiles=500):
        self.column = column

        self.qt = QuantileTransformer(
            n_quantiles=n_quantiles, output_distribution="normal"
        )
        self.qt.fit(data_raw)
        self.quantiles = self.qt.quantiles_
        self.unit_converter = 1.0

    def fit(self, quantiles, column, unit_converter=1.0):
        self.column = column

        self.qt = QuantileTransformer(
            n_quantiles=np.shape(quantiles)[0], output_distribution="normal"
        )
        self.qt.quantiles_ = quantiles
        self.quantiles = quantiles
        self.qt.references_ = np.linspace(0, 1, np.shape(quantiles)[0], endpoint=True)
        # self.quantiles = quantiles
        self.qt_fit = True
        self.unit_converter = unit_converter

    def process(self, data_raw, force_quantile=False):
        try:
            data = data_raw.copy()
        except Exception:
            # pass # value is likely a single element
            data = np.asarray(data_raw).astype("float64")

        if "DIRA" in self.column:
            where = np.where(np.isnan(data))
            where_not_nan = np.where(np.logical_not(np.isnan(data)))
            data[where] = np.amin(data[where_not_nan])

        if "VTXISOBDTHARD" in self.column:
            data[np.where(data == -1)] = np.random.uniform(
                low=-1.1, high=-1.0, size=np.shape(data[np.where(data == -1)])
            )
        if "FLIGHT" in self.column or "FD" in self.column or "IP" in self.column:
            data[np.where(data == 0)] = np.random.uniform(
                low=-0.1, high=0.0, size=np.shape(data[np.where(data == 0)])
            )

        if not self.qt_fit:
            self.qt.fit(data.reshape(-1, 1))
            self.qt_fit = True

        if "TRUEID" in self.column:
            data_out = np.zeros(np.shape(data))
            data_out[np.where(np.abs(data) == 11)] = -1
            data_out[np.where(np.abs(data) == 13)] = -0.5
            data_out[np.where(np.abs(data) == 211)] = 0.0
            data_out[np.where(np.abs(data) == 321)] = 0.5
            data_out[np.where(np.abs(data) == 2212)] = 1
            return data_out

        if (
            (
                "delta_PX" in self.column
                or "delta_PY" in self.column
                or "delta_PZ" in self.column
            )
            and self.use_min_max_for_mom_deltas
            and not force_quantile
        ):
            data = data * self.unit_converter
            data = data - self.min_maxes[self.column]["mean"]
            data = data / self.min_maxes[self.column]["std"]

            data = np.sign(data) * np.log10(1 + np.abs(data)) * (5.0 / np.log10(5 + 1))

            return data

        # if (
        #     (
        #         self.column[-8:] == "_delta_P"
        #         or self.column[-9:] == "_delta_PT"
        #         or self.column[-10:] == "_missing_P"
        #         or self.column[-11:] == "_missing_PT"
        #     )
        #     and self.use_min_max_for_mom_deltas
        #     and not force_quantile
        # ):
        #     data = data * self.unit_converter
        #     data = data - self.min_maxes[self.column]["mean"]
        #     data = data / self.min_maxes[self.column]["std"]

        #     data = np.sign(data) * np.log10(1 + np.abs(data)) * (5.0 / np.log10(5 + 1))

        #     return data
        

        if (
            (
                bool(
                    re.compile(r"^DAUGHTER\d+_(TRUEP(_[XYZ])?|TRUEE)$").match(
                        self.column
                    )
                )
                or bool(
                    re.compile(r"^DAUGHTER\d+_(E|P(X|Y|Z)?)_TRUE$").match(self.column)
                )
            )
            and self.use_min_max_for_mom_deltas
            and not force_quantile
        ):
            data = data * self.unit_converter
            data = data - self.min_maxes[self.column]["mean"]
            data = data / self.min_maxes[self.column]["std"]

            data = np.sign(data) * np.log10(1 + np.abs(data)) * (5.0 / np.log10(5 + 1))

            return data

        # if (
        #     self.column[-2:] == "IP"
        #     or self.column[:-7] == "IP_TRUE"
        #     or self.column[:-4] == "DIRA"
        #     or self.column[:-9] == "DIRA_TRUE"
        # ):
        #     data = data - self.min_maxes[self.column]["mean"]
        #     data = data / self.min_maxes[self.column]["std"]
        #     return data

        data = np_based_qt_transform(
            data.reshape(-1, 1) * self.unit_converter, self.quantiles, inverse=False
        )[:, 0]
        data = np.clip(data, -self.clip_value, self.clip_value)
        data = data / self.clip_value

        return data

    def unprocess(self, data_raw, force_quantile=False):
        data = data_raw.copy()

        # if (
        #     "TRUEORIGINVERTEX_X" in self.column or "TRUEORIGINVERTEX_Y" in self.column
        # ) or ("origX_TRUE" in self.column or "origY_TRUE" in self.column):
        #     return data

        if (
            (
                "delta_PX" in self.column
                or "delta_PY" in self.column
                or "delta_PZ" in self.column
            )
            and self.use_min_max_for_mom_deltas
            and not force_quantile
        ):
            k = 5.0 / np.log10(5 + 1)
            data = np.sign(data) * (10 ** (np.abs(data) / k) - 1)

            data = data * self.min_maxes[self.column]["std"]
            data = data + self.min_maxes[self.column]["mean"]

            return data * (1.0 / self.unit_converter)

        # if (
        #     (
        #         self.column[-8:] == "_delta_P"
        #         or self.column[-9:] == "_delta_PT"
        #         or self.column[-10:] == "_missing_P"
        #         or self.column[-11:] == "_missing_PT"
        #     )
        #     and self.use_min_max_for_mom_deltas
        #     and not force_quantile
        # ):
        #     k = 5.0 / np.log10(5 + 1)
        #     data = np.sign(data) * (10 ** (np.abs(data) / k) - 1)

        #     data = data * self.min_maxes[self.column]["std"]
        #     data = data + self.min_maxes[self.column]["mean"]

        #     return data * (1.0 / self.unit_converter)
            

        if (
            (
                bool(
                    re.compile(r"^DAUGHTER\d+_(TRUEP(_[XYZ])?|TRUEE)$").match(
                        self.column
                    )
                )
                or bool(
                    re.compile(r"^DAUGHTER\d+_(E|P(X|Y|Z)?)_TRUE$").match(self.column)
                )
            )
            and self.use_min_max_for_mom_deltas
            and not force_quantile
        ):
            k = 5.0 / np.log10(5 + 1)
            data = np.sign(data) * (10 ** (np.abs(data) / k) - 1)

            data = data * self.min_maxes[self.column]["std"]
            data = data + self.min_maxes[self.column]["mean"]

            return data * (1.0 / self.unit_converter)

        # if (
        #     self.column[-2:] == "IP"
        #     or self.column[:-7] == "IP_TRUE"
        #     or self.column[:-4] == "DIRA"
        #     or self.column[:-9] == "DIRA_TRUE"
        # ):
        #     data = data * self.min_maxes[self.column]["std"]
        #     data = data + self.min_maxes[self.column]["mean"]
        #     return data

        data = data * self.clip_value

        data = np_based_qt_transform(data.reshape(-1, 1), self.quantiles, inverse=True)[
            :, 0
        ] * (1.0 / self.unit_converter)

        if "VTXISOBDTHARD" in self.column:
            data[np.where(data < -1)] = -1.0
        if "FLIGHT" in self.column or "FD" in self.column or "IP" in self.column:
            data[np.where(data < 0)] = 0.0

        return data


def transform_df(data, transformers, transform_by_index=False, tag=""):
    data_copy = data.copy()

    if transform_by_index:
        for (branch, data_i), (transformer_key, transformer) in zip(
            data_copy.items(), transformers.items()
        ):
            if "N_daughters" in branch:
                data_copy[branch] = data_copy[branch]
                continue

            data_copy[branch] = transformer.process(np.asarray(data_copy[branch]))
    else:
        branches = list(data_copy.keys())

        for branch in branches:
            if "N_daughters" in branch:
                data_copy[branch] = data_copy[branch]
                continue

            if tag != "":
                transformer_branch = branch.replace(tag, "")
            else:
                transformer_branch = branch

            data_copy[branch] = transformers[transformer_branch].process(
                np.asarray(data_copy[branch])
            )

    return data_copy


def untransform_df(data, transformers, transformer_key_overrides=None):
    data_copy = data.copy()

    branches = list(data_copy.keys())

    for idx, branch in enumerate(branches):
        if transformer_key_overrides is not None:
            transformer_i = transformers[transformer_key_overrides[idx]]
        else:
            transformer_i = transformers[branch]

        if "N_daughters" in branch:
            data_copy[branch] = data_copy[branch]
            continue

        data_copy[branch] = transformer_i.unprocess(np.asarray(data_copy[branch]))

    return data_copy
