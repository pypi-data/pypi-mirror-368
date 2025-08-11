import boto3
from pandas import DataFrame
from io import BytesIO
from json import dumps
from asyncio import TaskGroup
from botocore.exceptions import ClientError
from gooder_ai.s3.types import UploadParams, UploadFileParams
from botocore.client import BaseClient
from typing import cast


# Convert dataframe to an in-memory csv sheet Ref: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html#pandas.DataFrame.to_csv
# Using buffer reference: https://stackoverflow.com/a/40540730
# Using BytesIO instead of StringIO because, s3 upload file function uses BytesIO
async def transform_dataframe_to_csv_file_object(data: DataFrame) -> BytesIO:
    csv_buffer = BytesIO()
    data.to_csv(csv_buffer, index=False)
    csv_buffer.seek(
        0
    )  # When we write something in buffer, file pointer is moved at the end of file. Here we are resetting the file pointer position to start after writing to file. Ref: https://stackoverflow.com/a/53485819
    return csv_buffer


# Convert config dictionary to a string to an in-memory json Ref: https://docs.python.org/3/library/json.html#basic-usage
# Using buffer reference: https://docs.python.org/3/library/io.html#binary-i-o
# Using BytesIO instead of StringIO because, s3 upload file function uses BytesIO
async def transform_config_to_json_file_object(config: dict) -> BytesIO:
    json_string = dumps(config)
    json_buffer = BytesIO(json_string.encode("utf-8"))
    json_buffer.seek(
        0
    )  # When we write something in buffer, file pointer is moved at the end of file. Here we are resetting the file pointer position to start after writing to file. Ref: https://stackoverflow.com/a/53485819
    return json_buffer


async def upload_handler(input: UploadParams) -> str | None:
    s3_client = input["s3_client"]
    identity_id = input["identity_id"]
    data = input["data"]
    mode = input["mode"]
    bucket_name = input["bucket_name"]
    file_name = input["file_name"]

    path: str | None = None
    parsed_data: BytesIO | None = None

    if isinstance(data, DataFrame):
        # The path to upload file is referenced from amplify. Ref: https://docs.amplify.aws/gen1/javascript/build-a-backend/storage/path/#using-protected-accesslevel
        path = f"{mode}/{identity_id}/data/{file_name}.csv"
        parsed_data = await transform_dataframe_to_csv_file_object(data)
    else:
        path = f"{mode}/{identity_id}/config/{file_name}.json"
        parsed_data = await transform_config_to_json_file_object(data)

    try:
        s3_client.upload_fileobj(parsed_data, bucket_name, path)
    except ClientError as e:
        print(f"Error uploading file: {e}")
        path = None
    return path


async def upload_files(input: UploadFileParams) -> dict[str, str | None]:
    credentials = input["credentials"]
    data = input["data"]
    file_name = input["file_name"]
    config = input["config"]
    mode = input["mode"]
    bucket_name = input["bucket_name"]
    upload_data_to_gooder = input["upload_data_to_gooder"]
    upload_config_to_gooder = input["upload_config_to_gooder"]
    aws_access_key_id = credentials["cognito_credentials"]["Credentials"]["AccessKeyId"]
    aws_secret_access_key = credentials["cognito_credentials"]["Credentials"][
        "SecretKey"
    ]
    aws_session_token = credentials["cognito_credentials"]["Credentials"][
        "SessionToken"
    ]
    identity_id = credentials["cognito_credentials"]["IdentityId"]

    # Reference for using temporary credentials : https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp_use-resources.html
    s3_client = cast(
        BaseClient,
        boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            region_name="us-east-1",
        ),
    )  # Mimicing "as" assertion to prevent type mismatch

    csv_path: str | None = None
    config_path: str | None = None

    """
    A new alternative to create and run tasks concurrently and wait for their completion 
    is asyncio.TaskGroup. TaskGroup provides stronger safety guarantees 
    than gather for scheduling a nesting of subtasks: if a task (or a subtask,
    a task scheduled by a task) raises an exception, TaskGroup will, while
    gather will not, cancel the remaining scheduled tasks).
    """
    csv_task = None
    config_task = None

    async with TaskGroup() as tg:
        if upload_data_to_gooder == True:
            csv_task = tg.create_task(
                upload_handler(
                    {
                        "identity_id": identity_id,
                        "s3_client": s3_client,
                        "data": data,
                        "file_name": file_name,
                        "mode": mode,
                        "bucket_name": bucket_name,
                    }
                )
            )

        if upload_config_to_gooder == True:
            config_task = tg.create_task(
                upload_handler(
                    {
                        "bucket_name": bucket_name,
                        "file_name": file_name,
                        "data": config,
                        "identity_id": identity_id,
                        "mode": mode,
                        "s3_client": s3_client,
                    }
                )
            )

    if csv_task is not None:
        csv_path = csv_task.result()

    if config_task is not None:
        config_path = config_task.result()

    return {"csv_path": csv_path, "config_path": config_path}
