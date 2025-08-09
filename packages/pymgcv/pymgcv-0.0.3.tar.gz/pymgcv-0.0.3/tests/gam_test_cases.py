"""A collection of GAM test cases."""

from dataclasses import dataclass, field
from collections.abc import Mapping
import numpy as np
import pandas as pd
import rpy2.robjects as ro
from rpy2.robjects.packages import importr

from pymgcv import terms
from pymgcv.basis_functions import (
    CubicSpline,
    MarkovRandomField,
    RandomEffect,
    RandomWigglyCurve,
)
from pymgcv.families import MVN, GauLSS, Poisson
from pymgcv.gam import BAM, GAM, AbstractGAM
from pymgcv.rpy_utils import data_to_rdf, to_py
from pymgcv.terms import Interaction, L, S, T


@dataclass
class GAMTestCase:  # GAM/BAM test cases
    mgcv_call: str
    gam_model: AbstractGAM
    data: pd.DataFrame | Mapping[str, np.ndarray | pd.Series]
    expected_predict_terms_structure: dict[str, list[str]]
    add_to_r_env: dict[str, ro.RObject] = field(default_factory=dict)

    def mgcv_gam(self, data: pd.DataFrame):
        with ro.local_context() as env:
            env["data"] = data_to_rdf(data)
            for k, v in self.add_to_r_env.items():
                env[k] = v
            return ro.r(self.mgcv_call)


# Factory functions for test cases
def linear_gam(model_type: type[AbstractGAM]) -> GAMTestCase:
    rng = np.random.default_rng(seed=42)
    data = pd.DataFrame({"x": rng.uniform(0, 1, 200), "y": rng.normal(0, 0.2, 200)})
    return GAMTestCase(
        mgcv_call=f"{model_type.__name__.lower()}(y~x, data=data)",
        gam_model=model_type({"y": L("x")}),
        data=data,
        expected_predict_terms_structure={"y": ["L(x)", "Intercept"]},
    )


def categorical_linear_gam(model_type: type[AbstractGAM]) -> GAMTestCase:
    rng = np.random.default_rng(seed=42)
    data = pd.DataFrame(
        {
            "group": pd.Series(rng.choice(["a", "b", "c"], 200), dtype="category"),
            "y": rng.normal(0, 0.2, 200),
        },
    )
    return GAMTestCase(
        mgcv_call=f"{model_type.__name__.lower()}(y~group, data=data)",
        gam_model=model_type({"y": L("group")}),
        data=data,
        expected_predict_terms_structure={"y": ["L(group)", "Intercept"]},
    )


def smooth_1d_gam(model_type: type[AbstractGAM]) -> GAMTestCase:
    rng = np.random.default_rng(seed=42)
    x = rng.uniform(0, 1, 200)
    data = pd.DataFrame({"x": x, "y": x**2 + rng.normal(0, 0.2, 200)})
    return GAMTestCase(
        mgcv_call=f"{model_type.__name__.lower()}(y~s(x), data=data)",
        gam_model=model_type({"y": S("x")}),
        data=data,
        expected_predict_terms_structure={"y": ["S(x)", "Intercept"]},
    )


def smooth_2d_gam(model_type: type[AbstractGAM]) -> GAMTestCase:
    rng = np.random.default_rng(seed=42)
    n = 200
    x0, x1 = rng.uniform(0, 1, n), rng.uniform(0, 1, n)
    y = np.sin(2 * np.pi * x0) * np.cos(2 * np.pi * x1) + rng.normal(0, 0.2, n)
    data = pd.DataFrame({"y": y, "x0": x0, "x1": x1})
    return GAMTestCase(
        mgcv_call=f"{model_type.__name__.lower()}(y~s(x0, x1), data=data)",
        gam_model=model_type({"y": S("x0", "x1")}),
        data=data,
        expected_predict_terms_structure={"y": ["S(x0,x1)", "Intercept"]},
    )


def tensor_2d_gam(model_type: type[AbstractGAM]) -> GAMTestCase:
    rng = np.random.default_rng(seed=42)
    n = 200
    x0, x1 = rng.uniform(0, 1, n), rng.uniform(0, 1, n)
    y = np.sin(2 * np.pi * x0) * np.cos(2 * np.pi * x1) + rng.normal(0, 0.2, n)
    data = pd.DataFrame({"y": y, "x0": x0, "x1": x1})
    return GAMTestCase(
        mgcv_call=f"{model_type.__name__.lower()}(y~te(x0, x1), data=data)",
        gam_model=model_type({"y": T("x0", "x1")}),
        data=data,
        expected_predict_terms_structure={"y": ["T(x0,x1)", "Intercept"]},
    )


def random_effect_gam(model_type: type[AbstractGAM]) -> GAMTestCase:
    rng = np.random.default_rng(42)
    n = 50
    group = pd.Series(rng.choice(["a", "b", "c"], n), dtype="category")
    x = np.linspace(0, 10, n)
    y = np.sin(x) + group.cat.codes + rng.normal(scale=0.1, size=n)
    data = pd.DataFrame({"group": group, "x": x, "y": y})
    return GAMTestCase(
        mgcv_call=f"{model_type.__name__.lower()}(y~s(x) + s(group, bs='re'), data=data)",
        gam_model=model_type({"y": S("x") + S("group", bs=RandomEffect())}),
        data=data,
        expected_predict_terms_structure={
            "y": ["S(x)", "S(group)", "Intercept"],
        },
    )


def categorical_interaction_gam(model_type: type[AbstractGAM]) -> GAMTestCase:
    rng = np.random.default_rng(seed=42)
    data = pd.DataFrame(
        {
            "group1": pd.Categorical(rng.choice(["a", "b"], size=200, replace=True)),
            "group2": pd.Categorical(
                rng.choice(["c", "d", "e"], size=200, replace=True),
            ),
            "y": rng.uniform(0, 1, size=200),
        },
    )
    return GAMTestCase(
        mgcv_call=f"{model_type.__name__.lower()}(y~group1:group2, data=data)",
        gam_model=model_type({"y": terms.Interaction("group1", "group2")}),
        data=data,
        expected_predict_terms_structure={
            "y": ["Interaction(group1,group2)", "Intercept"],
        },
    )


def multivariate_normal_gam(model_type: type[AbstractGAM]):
    rng = np.random.default_rng(seed=42)
    data = pd.DataFrame(
        {
            "x": rng.uniform(0, 1, 200),
            "y0": rng.normal(0, 0.2, 200),
            "y1": rng.normal(0, 0.2, 200),
        },
    )
    return GAMTestCase(
        mgcv_call=f"{model_type.__name__.lower()}(list(y0 ~ s(x, k=5), y1 ~ x), data=data, family=mvn(d=2))",
        gam_model=model_type({"y0": S("x", k=5), "y1": L("x")}, family=MVN(d=2)),
        data=data,
        expected_predict_terms_structure={
            "y0": ["S(x)", "Intercept"],
            "y1": ["L(x)", "Intercept"],
        },
    )


def gaulss_gam(model_type: type[AbstractGAM]):
    rng = np.random.default_rng(seed=42)
    data = pd.DataFrame(
        {
            "x0": rng.uniform(0, 1, 200),
            "x1": rng.normal(0, 0.2, 200),
            "y": rng.normal(0, 0.2, 200),
        },
    )
    return GAMTestCase(
        mgcv_call=f"{model_type.__name__.lower()}(list(y ~ s(x0), ~ s(x1)), data=data, family=gaulss())",
        gam_model=model_type(
            {"y": S("x0")},
            family_predictors={"log_scale": S("x1")},
            family=GauLSS(),
        ),
        data=data,
        expected_predict_terms_structure={
            "y": ["S(x0)", "Intercept"],
            "log_scale": ["S(x1)", "Intercept"],
        },
    )


def offset_gam(model_type: type[AbstractGAM]) -> GAMTestCase:
    rng = np.random.default_rng(seed=42)
    data = pd.DataFrame(
        {
            "x": rng.uniform(0, 1, 200),
            "z": rng.uniform(0, 1, 200),
            "y": rng.normal(0, 0.2, 200),
        },
    )
    return GAMTestCase(
        mgcv_call=f"{model_type.__name__.lower()}(y~s(x) + offset(z), data=data)",
        gam_model=model_type({"y": S("x") + terms.Offset("z")}),
        data=data,
        expected_predict_terms_structure={"y": ["S(x)", "Offset(z)", "Intercept"]},
    )


def smooth_1d_by_categorical_gam(model_type: type[AbstractGAM]) -> GAMTestCase:
    rng = np.random.default_rng(seed=42)
    data = pd.DataFrame(
        {
            "x": rng.standard_normal(100),
            "group": pd.Categorical(rng.choice(["a", "b", "c"], 100)),
            "y": rng.standard_normal(100),
        },
    )
    return GAMTestCase(
        mgcv_call=f"{model_type.__name__.lower()}(y~s(x, by=group), data=data)",
        gam_model=model_type({"y": S("x", by="group")}),
        data=data,
        expected_predict_terms_structure={"y": ["S(x,by=group)", "Intercept"]},
    )


def smooth_1d_by_numeric_gam(model_type: type[AbstractGAM]) -> GAMTestCase:
    rng = np.random.default_rng(seed=42)
    data = pd.DataFrame(
        {
            "x": rng.standard_normal(100),
            "by_var": rng.standard_normal(100),
            "y": rng.standard_normal(100),
        },
    )
    return GAMTestCase(
        mgcv_call=f"{model_type.__name__.lower()}(y~s(x, by=by_var), data=data)",
        gam_model=model_type({"y": S("x", by="by_var")}),
        data=data,
        expected_predict_terms_structure={"y": ["S(x,by=by_var)", "Intercept"]},
    )


def tensor_2d_by_categorical_gam(model_type: type[AbstractGAM]) -> GAMTestCase:
    rng = np.random.default_rng(seed=42)
    data = pd.DataFrame(
        {
            "x0": rng.standard_normal(100),
            "x1": rng.standard_normal(100),
            "group": pd.Categorical(rng.choice(["a", "b", "c"], 100)),
            "y": rng.standard_normal(100),
        },
    )
    return GAMTestCase(
        mgcv_call=f"{model_type.__name__.lower()}(y~te(x0,x1, by=group), data=data)",
        gam_model=model_type({"y": T("x0", "x1", by="group")}),
        data=data,
        expected_predict_terms_structure={
            "y": ["T(x0,x1,by=group)", "Intercept"],
        },
    )


def tensor_2d_by_numeric_gam(model_type: type[AbstractGAM]) -> GAMTestCase:
    rng = np.random.default_rng(seed=42)
    data = pd.DataFrame(
        {
            "x0": rng.standard_normal(100),
            "x1": rng.standard_normal(100),
            "by_var": rng.standard_normal(100),
            "y": rng.standard_normal(100),
        },
    )
    return GAMTestCase(
        mgcv_call=f"{model_type.__name__.lower()}(y~te(x0,x1,by=by_var), data=data)",
        gam_model=model_type({"y": T("x0", "x1", by="by_var")}),
        data=data,
        expected_predict_terms_structure={
            "y": ["T(x0,x1,by=by_var)", "Intercept"],
        },
    )


def smooth_1d_random_wiggly_curve_gam(
    model_type: type[AbstractGAM] = GAM,
) -> GAMTestCase:
    rng = np.random.default_rng(seed=42)
    data = pd.DataFrame(
        {
            "x": rng.standard_normal(100),
            "group": pd.Categorical(rng.choice(["a", "b", "c"], 100)),
            "y": rng.standard_normal(100),
        },
    )
    bs = RandomWigglyCurve(CubicSpline())
    return GAMTestCase(
        mgcv_call=f"{model_type.__name__.lower()}(y~s(x,group,bs='fs',xt=list(bs='cr')),data=data)",
        gam_model=model_type({"y": S("x", "group", bs=bs)}),
        data=data,
        expected_predict_terms_structure={"y": ["S(x,group)", "Intercept"]},
    )


def tensor_2d_random_wiggly_curve_gam(
    model_type: type[AbstractGAM] = GAM,
) -> GAMTestCase:
    rng = np.random.default_rng(seed=42)
    data = pd.DataFrame(
        {
            "x0": rng.standard_normal(100),
            "x1": rng.standard_normal(100),
            "group": pd.Categorical(rng.choice(["a", "b", "c"], 100)),
            "y": rng.standard_normal(100),
        },
    )
    bs = RandomWigglyCurve()
    return GAMTestCase(
        mgcv_call=f"{model_type.__name__.lower()}(y~t(x0,x1,group,bs='fs'),data=data)",
        gam_model=model_type({"y": T("x0", "x1", "group", bs=bs)}),
        data=data,
        expected_predict_terms_structure={
            "y": ["T(x0,x1,group)", "Intercept"],
        },
    )


def poisson_gam(model_type: type[AbstractGAM]) -> GAMTestCase:
    rng = np.random.default_rng(seed=42)
    data = pd.DataFrame(
        {
            "x": rng.standard_normal(100),
            "counts": rng.poisson(size=100),
        },
    )
    return GAMTestCase(
        mgcv_call=f"{model_type.__name__.lower()}(counts~s(x), data=data, family=poisson)",
        gam_model=model_type({"counts": S("x")}, family=Poisson()),
        data=data,
        expected_predict_terms_structure={"counts": ["S(x)", "Intercept"]},
    )


def markov_random_field_gam(model_type: type[AbstractGAM]) -> GAMTestCase:
    mgcv = importr("mgcv")
    polys = ro.packages.data(mgcv).fetch("columb.polys")["columb.polys"]
    data = ro.packages.data(mgcv).fetch("columb")["columb"]
    data = to_py(data)
    polys_list = list([to_py(x) for x in polys.values()])
    return GAMTestCase(
        mgcv_call=f"{model_type.__name__.lower()}(crime ~ s(district,bs='mrf',xt=list(polys=polys)),data=columb,method='REML')",
        gam_model=model_type(
            {"y": S("district", bs=MarkovRandomField(polys=polys_list))},
        ),
        data=data,
        expected_predict_terms_structure={"crime": ["S(district)", "Intercept"]},
        add_to_r_env={"polys": polys},
    )


def linear_and_interaction_gam(model_type: type[AbstractGAM]) -> GAMTestCase:
    # note mgcv will not include parameters for all interaction terms
    rng = np.random.default_rng(seed=42)
    n = 400
    group1 = pd.Series(rng.choice(["a", "b"], n), dtype="category")
    group2 = pd.Series(rng.choice(["a", "b"], n), dtype="category")
    y = rng.normal(size=n, scale=0.2) + group1.cat.codes * group2.cat.codes
    data = pd.DataFrame(
        {
            "group1": group1,
            "group2": group2,
            "y": y,
        },
    )
    return GAMTestCase(
        mgcv_call=f"{model_type.__name__.lower()}(y ~ group1 + group1:group2, data=data)",
        gam_model=model_type(
            {
                "y": L("group1") + Interaction("group1", "group2"),
            },
        ),
        data=data,
        expected_predict_terms_structure={
            "y": [
                "L(group1)",
                "Interaction(group1,group2)",
                "Intercept",
            ],
        },
    )


def linear_functional_smooth_1d_gam(model_type: type[AbstractGAM]) -> GAMTestCase:
    rng = np.random.default_rng(123)
    n = 200
    n_hours = 24
    hourly_x = rng.lognormal(size=(n, n_hours))
    true_fn = lambda x: np.sqrt(x)
    y = sum(true_fn(col) for col in hourly_x.T) + rng.normal(scale=0.1, size=n)
    data = {"y": y, "hourly_x": hourly_x}
    gam = model_type({"y": S("hourly_x")})

    return GAMTestCase(
        mgcv_call=f"{model_type.__name__.lower()}(y ~ s(hourly_x), data=data)",
        gam_model=gam,
        data=data,
        expected_predict_terms_structure={"y": ["S(hourly_x)", "Intercept"]}
    )


def linear_functional_tensor_2d_gam(model_type: type[AbstractGAM]) -> GAMTestCase:
    rng = np.random.default_rng(123)
    n = 200
    n_times = 4
    x0 = rng.lognormal(size=(n, n_times))
    x1 = rng.lognormal(size=(n, n_times))
    true_fn = lambda x0, x1: np.sqrt(x0) + np.sqrt(x1)
    y = sum(true_fn(x0_col, x1_col) for x0_col, x1_col in zip(x0.T, x1.T, strict=True)) + rng.normal(scale=0.1, size=n)
    data = {"y": y, "x0": x0, "x1": x1}
    gam = model_type({"y": T("x0", "x1")})

    return GAMTestCase(
        mgcv_call=f"{model_type.__name__.lower()}(y ~ te(x0, x1), data=data)",
        gam_model=gam,
        data=data,
        expected_predict_terms_structure={"y": ["T(x0,x1)", "Intercept"]}
    )
# def many_term_types_gam() -> GAMTestCase:
# rng = np.random.default_rng(seed=42)
# n = 400
# group1 = pd.Series(rng.choice(["a", "b"], n), dtype="category")
# group2 = pd.Series(rng.choice(["a", "b"], n), dtype="category")
# x0 = rng.standard_normal(n)
# x1 = rng.standard_normal(n)
# y = rng.normal(size=n, scale=0.2) + group1.cat.codes * group2.cat.codes * np.sin(
#     (x0 + x1) * 2,
# )
# data = pd.DataFrame(
#     {
#         "x0": x0,
#         "x1": x1,
#         "x2": rng.standard_normal(n),
#         "group1": group1,
#         "group2": group2,
#         "y": y,
#     },
# )
# return GAMTestCase(
#     mgcv_call=f"{model_type.__name__.lower()}(y~ti(x0,x1,by=group1) + s(x0, by=group1) + s(x1, by=group1) + group1 + group1:x0 + group1:group2, data=data)",
#     gam_model=model_type(
#         {
#             "y": (
#                 T("x0", "x1", by="group1", interaction_only=True)
#                 + S("x0", by="group1")
#                 + S("x1", by="group1")
#                 + L("group1")
#                 + Interaction("group1", "x0")
#                 + Interaction("group1", "group2")
#             ),
#         },
#     ),
#     data=data,
#     expected_predict_terms_structure={
#         "y": [
#             "T(x0,x1,by=group1)",
#             "S(x0,by=group1)",
#             "S(x1,by=group1)",
#             "L(group1)",
#             "Interaction(group1,x0)",
#             "Interaction(group1,group2)",
#             "Intercept",
#         ],
#     },
# )


def get_test_cases() -> dict[str, GAMTestCase]:
    supported_types_and_cases = [
        (
            (GAM, BAM),
            [
                linear_gam,
                categorical_linear_gam,
                smooth_1d_gam,
                smooth_2d_gam,
                tensor_2d_gam,
                random_effect_gam,
                smooth_1d_random_wiggly_curve_gam,
                categorical_interaction_gam,
                offset_gam,
                smooth_1d_by_categorical_gam,
                smooth_1d_by_numeric_gam,
                tensor_2d_by_categorical_gam,
                tensor_2d_by_numeric_gam,
                poisson_gam,
                linear_and_interaction_gam,
                linear_functional_smooth_1d_gam,
                linear_functional_tensor_2d_gam,
                # many_term_types_gam,
                # markov_random_field_gam  # TODO: Uncomment when ready
            ],
        ),
        (
            (GAM,),
            [
                multivariate_normal_gam,
                gaulss_gam,
            ],
        ),
    ]

    test_cases = {}
    for gam_types, cases in supported_types_and_cases:
        for gam_type in gam_types:
            for case in cases:
                test_cases[f"{gam_type.__name__} - {case.__name__}"] = case(gam_type)

    return test_cases
