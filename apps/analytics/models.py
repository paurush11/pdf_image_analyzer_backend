try:
    from .infrastructure.orm.models import *  # noqa: F401,F403
except Exception:  # pragma: no cover - avoid import errors during setup
    pass
