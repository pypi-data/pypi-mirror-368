
import boto3
import logging

logger = logging.getLogger(__name__)


def fetch_parameters(app_name, env, ver_number):
    """
    Fetches parameters from AWS Systems Manager Parameter Store for a given application, environment, and version number.

    Parameters:
        app_name (str): The name of the application.
        env (str): The environment (e.g., 'dev', 'prod').
        ver_number (str): The version number of the configuration.
    Returns:
        dict: A dictionary containing parameter names and their corresponding values.
    """

    ssm = boto3.client("ssm")
    path = f"/{app_name}/{env}/{ver_number}"

    paginator = ssm.get_paginator("get_parameters_by_path")
    parameters = {}

    for page in paginator.paginate(Path=path, Recursive=True):
        for param in page["Parameters"]:
            param_name = param["Name"].split("/")[-1]
            parameters[param_name] = param["Value"]

    return parameters

def set_parameters(app_name, env, ver_number, params_dict):
    """
    Stores parameters in AWS Systems Manager Parameter Store.
    
    Parameters:
        app_name (str): The name of the application.
        env (str): The environment (e.g., 'dev', 'prod').
        ver_number (str): The version number of the application.
        params_dict (dict): A dictionary of parameter names and their corresponding values.
    Returns:
        None
    """

    ssm = boto3.client("ssm")
    path = f"/{app_name}/{env}/{ver_number}"

    for param_name, param_value in params_dict.items():
        param_path = f"{path}/{param_name}"
        ssm.put_parameter(
            Name=param_path, Value=param_value, Type="String", Overwrite=False
        )

def set_default_version(app_name, env, ver_number):
    """
    Sets the default version number for a given application and environment combination in AWS Parameter Store.
    This version number can be used as a reference point for the latest stable configuration.

    Parameters:
        app_name (str): The name of the application.
        env (str): The environment (e.g., 'dev', 'prod').
        ver_number (str): The version number to set as default.
    Returns:
        None
    """
    ssm = boto3.client("ssm")
    path = f"/{app_name}/{env}/DEFAULT_VERSION"
    ssm.put_parameter(
        Name=path, Value=str(ver_number), Type="String", Overwrite=True
    )

def get_default_version(app_name, env):
    ssm = boto3.client("ssm")
    path = f"/{app_name}/{env}/DEFAULT_VERSION"
    try:
        response = ssm.get_parameter(Name=path)
        return response["Parameter"]["Value"]
    except ssm.exceptions.ParameterNotFound:
        logger.error(f"Default version for `{app_name}` in `{env}` not found. Set it with `set-version` command.")
        raise