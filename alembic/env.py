"""Alembic environment.

The database lives under a user-scoped data root, so the URL is resolved at run time rather than
read from alembic.ini.

    alembic upgrade head                      # rr.yaml's default_user
    alembic -x user=someone upgrade head      # a named user in this project
    alembic -x root=/path/to/proj upgrade head  # a different project entirely

Alembic resolves `script_location` against the working directory, so run it from the repository
root and point it at a data root with `-x root=` rather than changing directory.
"""

from __future__ import annotations

from pathlib import Path

from alembic import context
from sqlmodel import SQLModel

from rr import models  # noqa: F401  - imported for its side effect of registering tables
from rr.db import engine_for
from rr.paths import resolve

config = context.config
target_metadata = SQLModel.metadata


def _data_root():
    args = context.get_x_argument(as_dictionary=True)
    repo_root = Path(args["root"]).resolve() if args.get("root") else None
    return resolve(args.get("user"), repo_root=repo_root)


def run_migrations_offline() -> None:
    root = _data_root()
    context.configure(
        url=f"sqlite:///{root.database}",
        target_metadata=target_metadata,
        literal_binds=True,
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    root = _data_root()
    connectable = engine_for(root.database)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # SQLite cannot drop or retype a column; batch mode does the table rebuild for us.
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()
    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
