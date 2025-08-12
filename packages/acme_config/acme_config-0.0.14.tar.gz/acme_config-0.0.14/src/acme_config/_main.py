import os
import argparse
import logging

from dotenv import dotenv_values

from .aws_parameter_store import (
    fetch_parameters,
    set_parameters,
    set_default_version,
    get_default_version,
)


logger = logging.getLogger(__name__)


def save_fetched_parameters(parameters: dict, app_name: str, env: str, ver_number: int) -> None:
    """
    Save fetched parameters to a file.

    Parameters:
        parameters (dict): A dictionary containing the parameters to be saved.
        app_name (str): The name of the application.
        env (str): The environment (e.g., 'dev', 'prod').
        ver_number (int): The version number of the application.
    Returns:
        None
    """

    logger.info(parameters)
    fp = f"{app_name}.{env}.{ver_number}.env"
    with open(fp, "w") as f:
        for key, value in parameters.items():
            f.write(f"{key}={value}\n")
    logger.info(f"Parameters saved to {fp}")
    return fp


def load_saved_parameters(app_name: str, env: str, ver_number: int) -> dict:
    """
    Load parameters from a saved .env file.

    Parameters:
        app_name (str): The name of the application.
        env (str): The environment (e.g., 'dev', 'prod').
        ver_number (int): The version number of the application.
    Returns:
        dict: A dictionary containing the loaded parameters.
    Raises:
        FileNotFoundError: If the .env file does not exist.
    """
    fp = f"{app_name}.{env}.{ver_number}.env"
    return load_env_from_file(fp)


def load_env_from_file(params_path: str) -> dict:
    """
    Load parameters from a .env file at the specified path.

    Parameters:
        params_path (str): Path to the .env file to load parameters from.
    Returns:
        dict: A dictionary containing the loaded parameters.
    Raises:
        FileNotFoundError: If the .env file does not exist at the specified path.
    """
    if not os.path.exists(params_path):
        raise FileNotFoundError(f"Env file {params_path} not found")
    return dotenv_values(params_path)


def add_main_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-app-name", required=True, type=str, help="Application name")
    parser.add_argument("-env", required=True, type=str, help="Environment")
    parser.add_argument("-ver-number", required=True, type=int, help="Version number")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ac", description="System to store application configuration"
    )
    subparsers = parser.add_subparsers(dest="command")

    fetch_parser = subparsers.add_parser(
        "fetch",
        help="Fetch parameters",
        description="Fetch parameters from AWS AWS Parameter Store, print them to stdout, and save them to a file in CWD",
    )
    add_main_arguments(fetch_parser)

    set_parser = subparsers.add_parser(
        "set",
        help="Set parameters",
        description="Set parameters in AWS Parameter Store from a .evn file under the provided path",
    )
    add_main_arguments(set_parser)
    set_parser.add_argument(
        "--params-path", required=True, help="Path to .evn file to set as parameters"
    )

    set_version_parser = subparsers.add_parser(
        "set-version",
        help="Set version",
        description="Set default version number to use for (app-name, env) combination",
    )
    add_main_arguments(set_version_parser)

    get_version_parser = subparsers.add_parser(
        "get-version",
        help="Get version",
        description="Get default version number for (app-name, env) combination",
    )
    get_version_parser.add_argument(
        "-app-name", required=True, type=str, help="Application name"
    )
    get_version_parser.add_argument("-env", required=True, type=str, help="Environment")

    return parser.parse_args()


def main_logic(args: argparse.Namespace) -> None:
    if args.command == "fetch" or args.command == "get":
        parameters = fetch_parameters(args.app_name, args.env, args.ver_number)
        fp = save_fetched_parameters(parameters, args.app_name, args.env, args.ver_number)
        print(fp)
    elif args.command == "set":
        params_dict = load_env_from_file(args.params_path)
        set_parameters(args.app_name, args.env, args.ver_number, params_dict)
        logger.info("Parameters set successfully")
    elif args.command == "set-version":
        set_default_version(args.app_name, args.env, args.ver_number)
        logger.info("Default version set successfully")
    elif args.command == "get-version":
        version = get_default_version(args.app_name, args.env)
        logger.info(
            f"Default version for `{args.app_name}` in `{args.env}` is `{version}`"
        )
        print(version)


def main() -> None:
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(level=logging.INFO)
    args = parse_args()
    main_logic(args)


if __name__ == "__main__":
    main()
