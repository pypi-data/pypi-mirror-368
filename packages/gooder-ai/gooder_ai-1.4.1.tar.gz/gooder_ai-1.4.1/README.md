# Gooder AI Package

This package provides a streamlined way to ~evaluate~ valuate machine learning models on the **Gooder AI platform**. It exports a simple yet powerful function, **`valuate_model`**, which is designed to seamlessly work with a variety of machine learning frameworks -- including `scikit-learn`, `XGBoost`, `PyTorch`, and `Catboost` models. The function does the following:

- **Valuates** models with [Gooder AI](https://app.gooder.ai).  
- **Validates and uploads** Gooder AI configurations and test datasets
 for secure storage and processing.
- **Creates or updates** a shared "view" on [Gooder AI](https://app.gooder.ai), allowing users to interactively visualize and analyze their model's business performance.


### Learn more here:
- For a **hands-on tutorial**, watch this short video [here](https://www.youtube.com/watch?v=EPYcHaL25OQ&list=PLdJkca7Mgj97bpG7QmFykU2IYCXgjdlJl&index=3).
- For **more information**, see the [Gooder AI hands-on guide](https://www.gooder.ai/handson).

---

## Installation
Install the package using pip:

```bash
pip install gooder_ai
```
---

## Sample Jupyter Notebook
[Running valuate_model on fraud detection models](https://drive.google.com/uc?export=download&id=1AUa4KAM-RsjAeHlO_y9hXTJjSmofuvSD) (suitable for Jupyter notebooks)

---

## Function Parameters

### `valuate_model(**kwargs)`
The `valuate_model` function takes the following input arguments:

1. **`models: list[ScikitModel]`**  
   - Machine learning models that follow the `ScikitModel` protocol.  
   - It must have a scoring function (e.g., `predict_proba`), which is used to generate probability scores for classification.  
   - It must also have a `classes_` attribute, representing the possible target classes.

2. **`x_data: ndarray | DataFrame | list[str | int | float] | spmatrix`**  
   - A dataset containing the input features for evaluation.  
   - This is the dataset that will be fed into the model for prediction.

3. **`y: ndarray | DataFrame | list[str | int | float] | spmatrix`**  
   - A dataset representing the true target values (labels) corresponding to `x_data`.  
   - This helps in validating model performance.

4. **`config: dict`**  
   - A dictionary containing model configuration settings.  
   - To load a [starter configuration](https://docs.gooder.ai) provided by Gooder AI, you can use the following example:
     ```python
     from gooder_ai.configs import load_starter_config
     config = load_starter_config()
     ```

5. **`view_meta: ViewMeta`**  
   - A dictionary containing metadata about the "view" (shared result visualization) being created or updated.  
   - Structure:
     ```python
     {
         "mode": Optional["public" | "protected" | "private"],  # Access control
         "view_id": Optional[str],  # ID of an existing view (if updating)
         "dataset_name": Optional[str]  # Name of the dataset (defaults to timestamp)
     }
     ```
   - If `view_id` is provided, an existing view is updated; otherwise, a new one is created.

6. **`auth_credentials: Credentials`**  
   - A dictionary with user authentication details for the Gooder AI platform.  
   - Structure:
     ```python
     {
         "email": str,  # User's email
         "password": str  # User's password
     }
     ```
   - These credentials are used for authentication to upload the dataset and configuration. It is optional if `upload_data_to_gooder = False` and `upload_config_to_gooder = False`.

7. **`model_names: list[str]`**
   - This property is used to label the score columns in the output dataset and configuration.
   - If not provided default names are generated based on model class names.
   - Example: For a model that outputs binary classification scores, a column named "model1_score, model2_score" will be created.

8. **`scorer_names: list[str]`**
   - This property is used to specify the different scorer function.
   - If not provided by default it uses `predict_proba` function.

9. **`column_names: ColumnNames = {}`** *(optional)*  
   - A dictionary specifying the column names for the dataset and scores.  
   - Structure:
     ```python
     {
         "dataset_column_names": Optional[list[str]],  # Feature names
         "dependent_variable_name": Optional[str]  # Name of the target variable
     }
     ```

10. **`included_columns: list[str] = []`** *(optional)*  
   - An optional list of names specifying which columns to include in the dataset before valuating your models on the Gooder platform. If left unspecified, all columns will be included, which generally results in an unnecessarily large data file, since Gooder typically only makes use of a small number of columns. Even when specified, the following columns will always be included: model scores, dependent variable.  

11. **`upload_data_to_gooder: Boolean = True`** *(optional)*  
   - This flag is used to prevent/allow dataset upload to Gooder AI platform

12. **`upload_config_to_gooder: Boolean = True`** *(optional)*  
   - This flag is used to prevent/allow config upload to Gooder AI platform


13. **`aws_variables: AWSVariables = {}`** *(optional)*  
   - A dictionary containing AWS-related variables. 
   - Used for authentication and file uploads.
   - Structure:
     ```python
     {
         "api_url": Optional[str],
         "app_client_id": Optional[str],
         "identity_pool_id": Optional[str],
         "user_pool_id": Optional[str],
         "bucket_name": Optional[str],
         "base_url": Optional[str],
         "validation_api_url": Optional[str]
     }
     ```
   - Defaults to global values if not provided.


14. **`max_size_uploaded_data: int = 10`** *(optional)* 
   - Defines the maximum allowed memory size (in megabytes, MB) for the combined dataset when uploading to Gooder AI.
   - Before uploading, the function calculates the memory usage of the full dataset.
   - If the dataset exceeds this threshold and `upload_data_to_gooder` is `True`, the operation is aborted and an exception is raised.
   - This is a safety limit to prevent large uploads that could impact performance or exceed platform limits.
   - Default value is 10MB, which is suitable for most use cases.
   - Increase this value if you need to work with larger datasets, but be aware of potential performance implications.

15. **`max_size_saved_data: int = 1000`** *(optional)* 
   - Defines the maximum allowed memory size (in megabytes, MB) for the combined dataset when saving locally.
   - Before saving, the function calculates the memory usage of the full dataset.
   - If the dataset exceeds this threshold and `upload_data_to_gooder` is `False`, the operation is aborted and an exception is raised.
   - This is a safety limit to prevent excessively large local files that could impact system performance.
   - Default value is 1000MB (approximately 1GB), which allows for much larger local datasets compared to uploads.
   - Increase this value if you need to work with very large datasets locally, but be aware of system memory constraints.


---


## Summary

- The function takes a **scikit-learn model**, **dataset**, **user credentials**, and **configuration details**.
- If either the data or config are set to be uploaded, it authenticates with the Gooder AI platform, validates the config, and uploads the file.
- If either the data or config are set to be uploaded, it either creates a new shared view or updates an existing one.
- Finally, it **returns the view ID and URL**, allowing users to access model evaluation results.


---

## Logging configuration

To configure logging in your notebook, add the following code:

```python
import logging
import sys

logging.basicConfig(
    format='%(asctime)s | %(levelname)s : %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)
```

### Log Levels

The logger supports three levels of verbosity:

1. **ERROR**: Only prints error logs
2. **INFO**: Prints information logs and error logs (default)
3. **DEBUG**: Verbose mode that prints all logs, including warnings

By default, sample notebooks are configured to use the INFO level. You can adjust this level based on your requirements.

---

## Custom Model Wrappers

In order to work with PyTorch models, the Gooder AI package provides a ModelWrapper abstract base class (this allows the valuate_model function to internally work with PyTorch models the same way it works with scikit-learn and XGBoost models).

### Using ModelWrapper

The `ModelWrapper` class provides a standardized interface that any model can implement:

```python
from gooder_ai import ModelWrapper

class YourCustomModel(ModelWrapper):
    @abstractmethod
    def predict_proba(self, x):
        """Must return probability predictions as numpy array"""
        pass
    
    @property
    @abstractmethod
    def classes_(self):
        """Must return array of class labels"""
        pass
```

[Sample Workbook: Using `valuate_model` with PyTorch Models](https://drive.google.com/file/d/1uny8_Bqj5YphCuXoi34hIl4xI6kleLa9/view?usp=drive_link)

---



## **Common Issues**
1. **Mismatch in column names:** Ensure that the number of column names matches the dataset shape.  
2. **Invalid model type:** Ensure that the model conforms to the `ScikitModel` or `XGBoost` interface and implements a scoring function e.g `predict_proba` method.
3. **Authentication failure:** Double-check credentials and the Gooder AI endpoint URL.
4. **Dataset size limits:** If you encounter size-related errors, adjust the `max_size_uploaded_data` or `max_size_saved_data` parameters.
5. **Model naming issues:** Ensure that the `model_names` list has the same length as the `models` list to avoid default naming.

---

## Running within a Databricks

### 1. [Sample notebook for Databricks](https://drive.google.com/uc?export=download&id=1Bej_j3frAdk7JxT51JlejK9r9YeROw5t)
- This version is ready for use in Databricks and does **not** contain any `%pip install` commands.
- The %pip install commands are removed because:
     - They can cause cold start issues in Databricks
     - They may conflict with cluster-level package management
     - They can lead to inconsistent environments across users
     - Databricks best practices recommend managing dependencies at the cluster level

### 2. [Setting Up the Databricks Environment](https://docs.databricks.com/aws/en/compute/serverless/dependencies)
- **Use Environment version 2**
- **Dependencies:**
  - Ensure the following packages are added to your Databricks cluster environment (via the UI, not by the notebook):
      - `gooder_ai`
      - `seaborn`
      - `matplotlib`
      - `xgboost`
      - `numpy`
      - `pandas`
      - `scikit-learn`
- **Cluster State:**
  - Wait for the cluster to show a "Connected" state before running any cells.


### 3. Handling Large Data Files
  - Databricks workspace has a 500 MB file size limit for [uploads and downloads](https://docs.databricks.com/gcp/en/files/workspace#file-size-limit).
  - For datasets larger than 500 MB:
    - Split them into multiple smaller files.
    - Upload the split files to Databricks.
    - Add a cell in your notebook to combine the files into a single DataFrame.
    - Pass the combined DataFrame to `valuate_model`.
    - Operations will fail if they attempt to:
         - Create a file exceeding 500 MB in the workspace
         - Upload a file larger than 500 MB to the workspace 
         - Download a file larger than 500 MB into the workspace.
   

   **Important:**
   
   After successful execution of the notebook, it will provide you:
   - A configuration file to be used with Gooder AI
   - A CSV file containing the scored test data

   If you have not instructed valuate_model to pass these files through the cloud to the Gooder AI application, you must then download these files locally and then upload them to the Gooder AI application to visualize the business performance of your models.

   **Note** 
   - `valuate_model` can be configured to reduce the size of the output CSV file by using the `included_columns` parameter to specify which columns to include.


