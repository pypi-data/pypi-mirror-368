from pandas import DataFrame, Series
from numpy import ndarray

from typing import TypedDict, Literal, NotRequired, Protocol, Optional, Any, Union, List
from scipy.sparse import (
    bsr_matrix,
    coo_matrix,
    csc_matrix,
    csr_matrix,
    dia_matrix,
    dok_matrix,
    lil_matrix,
)


class ScikitModel(Protocol):
    def predict_proba(self, X) -> Optional[Any]: ...


class ViewMeta(TypedDict):
    mode: NotRequired[Literal["public", "protected", "private"]]
    view_id: NotRequired[str]
    dataset_name: NotRequired[str]


class ValuateModelOutput(TypedDict):
    view_id: str | None
    view_url: str


class Credentials(TypedDict):
    email: NotRequired[str]
    password: NotRequired[str]


class AWSVariables(TypedDict):
    api_url: NotRequired[str]
    app_client_id: NotRequired[str]
    identity_pool_id: NotRequired[str]
    user_pool_id: NotRequired[str]
    bucket_name: NotRequired[str]
    base_url: NotRequired[str]
    validation_api_url: NotRequired[str]


class ColumnNames(TypedDict):
    dataset_column_names: NotRequired[list[str]]
    dependent_variable_name: NotRequired[str]


class GetScoreColumnNamesParams(TypedDict):
    model_name: str
    scores: list[str]


Data = Union[
    DataFrame,
    List[Union[str, int, float]],
    List[
        List[Union[str, int, float]]
        # Sparse matrix types Ref: https://docs.scipy.org/doc/scipy/reference/sparse.html#sparse-matrix-classes
    ],
    ndarray,
    bsr_matrix,
    coo_matrix,
    csc_matrix,
    csr_matrix,
    dia_matrix,
    dok_matrix,
    lil_matrix,
    Series,
]  # Using python 3.11 ersion compatible type definition


class AmplifyEnv(TypedDict):
    API_URL: str
    App_Client_ID: str
    Identity_Pool_ID: str
    User_Pool_ID: str
    Bucket_Name: str
    Validation_API_URL: str
    Base_URL: str
    AWS_Region_Name: str
