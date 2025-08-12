import jwt
from rich import print

from spiral.cli import state


def command(org_id: str | None = None, force: bool = False):
    token = state.settings.device_code_auth.authenticate(force=force, org_id=org_id)
    print("Successfully logged in.")
    print(token.expose_secret())


def whoami():
    """Display the current user's information."""
    payload = jwt.decode(state.settings.authn.token().expose_secret(), options={"verify_signature": False})
    print(f"{payload['org_id']}")
    print(f"{payload['sub']}")


def logout():
    state.settings.device_code_auth.logout()
    print("Logged out.")
