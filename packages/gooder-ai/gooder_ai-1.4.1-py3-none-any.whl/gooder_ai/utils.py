from aiohttp import ClientSession
from numpy import ndarray
from pandas import DataFrame, RangeIndex, Series
from json import dump
from scipy.sparse import spmatrix
from gooder_ai.types import GetScoreColumnNamesParams, Data
import logging


async def validate_config(validation_url: str, config: dict) -> dict:
    async with ClientSession() as session:
        output = None
        async with session.post(validation_url, json=config) as response:
            if response.status == 200:
                output = await response.json()
            else:
                error = await response.text()
                logging.error(f"Validation failed with {response.status}: {error}")
                raise Exception(f"Validation failed with {response.status}: {error}")
        return output


# TODO: Verify if need to handle multi output classifiers.
def get_score_column_names(params: GetScoreColumnNamesParams) -> list[str]:
    scores = params["scores"]
    model_name = params["model_name"]

    # Ensure output has enough names, filling missing ones
    output = [f"{model_name}_score_{column_name}" for column_name in scores]

    return output


def get_scorer_functions(models_count: int, scorers: list[str]) -> list[str]:
    if models_count != len(scorers):
        logging.debug(
            f"Mismatch:  {models_count} Models, but {len(scorers)} scoring functions were provided."
        )

    output = (
        scorers[:models_count]
        + ["predict_proba" for _ in range(len(scorers), models_count)]
        if models_count != len(scorers)
        else scorers
    )

    return output


# Add column names to dataframe
def transform_dataframe(data: DataFrame, column_names: list[str]) -> DataFrame:
    transformed_dataframe = data.copy()

    # Get existing column names
    default_column_names = transformed_dataframe.columns
    column_count = transformed_dataframe.shape[1]
    final_column_names = []

    if len(column_names) != column_count:
        logging.debug(
            f"Mismatch: DataFrame has {column_count} columns, but {len(column_names)} column names were provided."
        )

    if len(column_names) == column_count:
        # Priority 1: Use provided column names
        final_column_names = column_names
    elif isinstance(default_column_names, RangeIndex) == False:
        # Priority 2: Use existing column names if not RangeIndex
        final_column_names = default_column_names
    else:
        # Priority 3: Generate default names if no names available
        final_column_names = column_names[:column_count] + [
            f"column-{i+1}" for i in range(len(column_names), column_count)
        ]

    # Assign final column names
    transformed_dataframe.columns = final_column_names

    return transformed_dataframe


def transform_unstructured_numpy_array(
    data: ndarray, column_names: list[str]
) -> DataFrame:
    logging.debug("Unstructured numpy array does not have any column name")
    numpy_array = data.copy()

    if numpy_array.ndim > 2:
        raise ValueError("Input data must be a 1D or 2D NumPy array.")

    column_count = (
        1 if numpy_array.ndim == 1 else data.shape[1]
    )  # For 2D arrays, second value of tuple is the column count
    column_names_length = len(column_names)

    if column_names_length != column_count:
        logging.debug(
            f"Mismatch: Numpy array has {column_count} columns, but {column_names_length} column names were provided."
        )

    final_column_names = column_names[:column_count] + [
        f"column-{i+1}" for i in range(column_names_length, column_count)
    ]

    output = DataFrame(numpy_array, columns=final_column_names)
    return output


def transform_structured_numpy_array(
    data: ndarray, column_names: list[str]
) -> DataFrame:
    numpy_array = data.copy()
    default_column_names = list(data.dtype.names)

    if numpy_array.ndim > 2:
        raise ValueError("Input data must be a 1D or 2D NumPy array.")

    column_names_length = len(column_names)
    column_count = 1 if numpy_array.ndim == 1 else data.shape[1]
    if column_names_length != column_count:
        logging.debug(
            f"Mismatch: Numpy array has {column_count} columns, but {column_names_length} column names were provided."
        )

    final_column_names = column_names[: min(column_count, column_names_length)]

    # Use default column names if available
    if len(final_column_names) < column_count:
        remaining_defaults = default_column_names[len(final_column_names) :]
        final_column_names.extend(
            remaining_defaults[: column_count - len(final_column_names)]
        )

    # Generate custom column names for any remaining unnamed columns
    if len(final_column_names) < column_count:
        final_column_names.extend(
            [f"column-{i+1}" for i in range(len(final_column_names), column_count)]
        )

    output = DataFrame(numpy_array, columns=final_column_names)
    return output


def transform_list(
    data: (
        list[str]
        | list[int]
        | list[float]
        | list[list[str]]
        | list[list[int]]
        | list[list[float]]
    ),
    column_names: list[str],
) -> DataFrame:
    logging.debug("List does not have any column name.")
    data_list = data.copy()
    final_column_names = []

    # 1D list handling.
    if isinstance(data_list[0], (str, int, float)):
        data_list = [[value] for value in data_list]
        final_column_names = column_names[:1] if column_names else ["column-1"]

    elif isinstance(data_list[0], list):
        column_count = len(data_list[0])
        if len(column_names) != column_count:
            logging.debug(
                f"Mismatch: DataFrame has {column_count} columns, but {len(column_names)} column names were provided."
            )
        final_column_names = column_names[:column_count] + [
            f"column-{i+1}" for i in range(len(column_names), column_count)
        ]

    else:
        raise ValueError("Input data must be a 1D or 2D list.")

    # Create DataFrame
    output = DataFrame(data_list, columns=final_column_names)
    return output


def get_transformed_data(data: Data, column_names: list[str]) -> DataFrame:
    output = DataFrame()
    if isinstance(data, DataFrame):
        output = transform_dataframe(data, column_names)
    elif isinstance(data, Series):
        output = data.to_frame(name=column_names[0])
    elif isinstance(data, ndarray) and data.dtype.names is None:
        output = transform_unstructured_numpy_array(data, column_names)
    elif isinstance(data, ndarray) and data.dtype.names is not None:
        transform_structured_numpy_array(data, column_names)
    elif isinstance(data, list):
        output = transform_list(data, column_names)
    elif isinstance(data, spmatrix):
        """
        scipy has multiple types of matrix all of them are extending spmatrix
        Ref: https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.spmatrix.html#spmatrix
        """
        numpy_array = data.toarray()
        output = transform_unstructured_numpy_array(numpy_array, column_names)

    if isinstance(output.columns, RangeIndex):
        raise ValueError("Invalid columns")
    return output


def save_config(config: dict, file_path: str):
    with open(file_path, "w") as file:
        # dump automatically writes to file
        dump(
            config, file, indent=4
        )  # Ref: https://docs.python.org/3/library/json.html#basic-usage


def get_positive_class(df: DataFrame):
    # Returns the less frequent value in a single-column DataFrame.
    # Rules:
    # - For columns with 1 unique value: returns that value
    # - For binary columns (2 unique values): returns the less frequent value
    # - For empty columns: raises ValueError

    # Args: df: Single-column pandas DataFrame
    # Returns: The value that appears less frequently (or the single value)
    # Raises: ValueError: If input isn't single-column, is empty, or has >2 unique values

    # Validate input structure
    if df.shape[1] != 1:
        logging.error("Input must be a single-column DataFrame")
        raise ValueError("Input must be a single-column DataFrame")

    # Extract values
    if df.empty:  # Get the column name and is it empty or not
        logging.error("DataFrame column is empty")
        raise ValueError("DataFrame column is empty")

    column_name = df.columns[0]
    # Convert to list once
    # Ref: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.value_counts.html
    value_counts = df.value_counts(
        f"{column_name}"
    )  # Column name can be of type string and index depending on the dataFrame
    # Ref: https://pandas.pydata.org/docs/reference/api/pandas.Series.to_dict.html#pandas.Series.to_dict
    count_dictionary = value_counts.to_dict()

    if len(count_dictionary.keys()) > 2:
        logging.error(
            f"Column must contain maximum 2 unique values (found {len(count_dictionary.keys())})"
        )
        raise ValueError(
            f"Column must contain maximum 2 unique values (found {len(count_dictionary.keys())})"
        )

    least_frequent = min(count_dictionary.keys(), key=lambda k: count_dictionary[k])
    return least_frequent
