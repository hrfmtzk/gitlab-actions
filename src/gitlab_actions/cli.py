import os
from typing import List, Optional, TextIO

import click
from gitlab import Gitlab

from gitlab_actions.jobs import JobParser


def find_env_vars(
    env_vars: List[str], default: Optional[str] = None
) -> Optional[str]:
    for env in env_vars:
        try:
            return os.environ[env]
        except KeyError:
            continue
    return default


@click.command()
@click.option(
    "--url",
    default=find_env_vars(
        ["SERVER_URL", "CI_SERVER_URL"], default="https://gitlab.com"
    ),
)
@click.option(
    "--project-id",
    default=find_env_vars(["PROJECT_ID", "CI_PROJECT_ID"]),
    required=True,
)
@click.option(
    "--access-token",
    default=find_env_vars(["ACCESS_TOKEN", "PRIVATE_TOKEN"]),
    required=True,
)
@click.option(
    "--job-file",
    type=click.File("rb"),
    default=find_env_vars(["JOB_FILE"]),
    required=True,
)
def gljob(
    url: Optional[str],
    project_id: Optional[str],
    access_token: Optional[str],
    job_file: TextIO,
):
    gl = Gitlab(url, access_token)
    project = gl.projects.get(project_id)

    parser = JobParser(job_file)
    parser.parse()

    for job in parser.jobs:
        click.echo(f"- [{job.target_type.name}] {job.name} ...", nl=False)
        targets = job.run(project)
        click.echo(f" (targets: {len(targets)})")
