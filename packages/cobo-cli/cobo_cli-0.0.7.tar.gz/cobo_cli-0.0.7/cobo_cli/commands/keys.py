import logging
import os
import secrets

import click
from click import ClickException
from dotenv import get_key, load_dotenv, set_key  # Import dotenv functions
from nacl.signing import SigningKey

from cobo_cli.data.context import CommandContext
from cobo_cli.data.manifest import Manifest

logger = logging.getLogger(__name__)


@click.group(
    "keys",
    context_settings=dict(help_option_names=["-h", "--help"]),
    help=(
        "Commands to generate and manage API/APP keys. "
        "Use these commands to create new keys or manage existing ones."
    ),
)
@click.pass_context
def keys(ctx: click.Context):
    """Key management command group."""


@keys.command("validate", help="Validate API keys")
@click.option(
    "--alg",
    default="ed25519",
    help="Specify the key generation algorithm.",
)
@click.option(
    "--secret",
    type=str,
    help="Secret to be validated against.",
)
@click.option(
    "--pubkey",
    type=str,
    help="Pubkey to be validated against.",
)
@click.pass_context
def validate_key(ctx: click.Context, alg: str, secret: str, pubkey: str):
    try:
        _, _pubkey = generate_key_pair(alg, secret)
        if _pubkey != pubkey:
            raise ClickException("Public key does not match.")
    except Exception as e:
        raise ClickException(str(e))


@keys.command("generate", help="Generate a new API/APP key pair.")
@click.option(
    "--key-type",
    type=click.Choice(["API", "APP"]),
    default="API",
    help="Type of key to generate (API or APP).",
)
@click.option(
    "--alg",
    default="ed25519",
    help="Specify the key generation algorithm.",
)
@click.option(
    "--force",
    is_flag=True,
    help="Force to replace existing keys.",
)
@click.option(
    "--file",
    help="Specify the filepath that the key will be written to.",
)
@click.pass_context
def generate_keys(
    ctx: click.Context, key_type: str, alg: str, force: bool, file: str = None
):
    """Generate a new API/APP key pair."""
    command_context: CommandContext = ctx.obj

    logger.debug(
        f"Generating keys using the following options, key_type: {key_type}, "
        f"algorithm: {alg}, force: {force}"
    )

    try:
        secret, pubkey = generate_key_pair(alg)
    except ValueError as e:
        raise click.ClickException(str(e))

    if key_type == "API":
        handle_api_key_generation(command_context, pubkey, secret, force, file)
    elif key_type == "APP":
        handle_app_key_generation(pubkey, secret, force, file)

    click.echo(f"{key_type} key generation successful.")
    click.echo(f"Public key: {pubkey}")
    if file:
        click.echo(f"Secret key has been saved securely in the {file}.")
    elif key_type == "APP":
        click.echo("Secret key has been saved securely in the .env file.")
    else:
        current_env = command_context.config_manager.get_config("environment")
        click.echo(
            f"Secret key has been saved securely in the {current_env} environment section."
        )


def generate_key_pair(alg, secret=None):
    """Generate a key pair based on the specified algorithm."""
    if not secret:
        secret = secrets.token_hex(32)

    if alg == "ed25519":
        sk = SigningKey(bytes.fromhex(secret))
        return secret, sk.verify_key.encode().hex()

    raise NotImplementedError("Algorithm {} is not supported".format(alg))


def handle_key_generation_to_file(
    pubkey: str, secret: str, force: bool, prefix: str, file: str
):
    load_dotenv(file)
    pubkey_key_to_set = f"{prefix}_KEY"
    secret_key_to_set = f"{prefix}_SECRET"
    exist_key = get_key(file, pubkey_key_to_set)
    exist_secret = get_key(file, secret_key_to_set)
    if not force and (exist_key or exist_secret):
        raise click.ClickException(
            f"--force must be used when {pubkey_key_to_set} or {secret_key_to_set} in {file} exists."
        )

    set_key(file, f"{prefix}_KEY", pubkey, quote_mode="never")
    set_key(file, f"{prefix}_SECRET", secret, quote_mode="never")


def handle_api_key_generation(
    command_context: CommandContext,
    pubkey: str,
    secret: str,
    force: bool,
    file: str = None,
):
    """Handle API key generation logic."""
    if file:
        handle_key_generation_to_file(pubkey, secret, force, "COBO_API", file)
        return
    config_manager = command_context.config_manager

    if config_manager.get_config("api_key") and not force:
        raise click.ClickException("--force must be used when API key exists.")

    # Save the secret key in the config file under the right environment section
    config_manager.set_config("api_key", pubkey)
    config_manager.set_config("api_secret", secret)


def handle_app_key_generation(pubkey: str, secret: str, force: bool, file: str = None):
    """Handle APP key generation logic."""
    # Load the manifest
    try:
        manifest, manifest_path = Manifest.load()
    except ValueError as e:
        raise click.ClickException(str(e))

    if not manifest:
        if file:
            handle_key_generation_to_file(pubkey, secret, force, "COBO_APP", file)
            return
        raise click.ClickException(
            "Manifest file not found. Please move to app directory."
        )

    # Check if app_key already exists
    if manifest.app_key and manifest.app_key != "your-app-key" and not force:
        if not click.confirm(
            f"An app_key already exists: {manifest.app_key}. Do you want to overwrite it?"
        ):
            raise click.ClickException("Operation aborted by the user.")

    # Update the app_key and save the manifest
    manifest.app_key = pubkey
    manifest.save(manifest_path)

    # Load or create the .env file
    if file:
        handle_key_generation_to_file(pubkey, secret, force, "COBO_APP", file)
    dotenv_path = os.path.join(os.path.dirname(manifest_path), ".env")
    load_dotenv(dotenv_path)

    # Store the APP_SECRET in the .env file
    set_key(dotenv_path, "APP_SECRET", secret, quote_mode="never")


if __name__ == "__main__":
    keys()
