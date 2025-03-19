import shutil
import subprocess
from pathlib import Path


def _inject_pip_install_crawlee_from_whl_to_docker_file(wheel_name: str, docker_file: Path, line_marker:str='FROM apify/') -> None:
    with open(docker_file) as f:
        modified_lines =  []
        for line in f.readlines():
            # pip install crawlee early in the docker build so that the following installations will consider the requirement already satisfied
            if line.startswith(line_marker):
                modified_lines.append(f"""COPY {wheel_name} ./\nRUN pip install ./{wheel_name}\n""")
            modified_lines.append(line)

    with open(docker_file, 'w') as f:
        f.write(''.join(modified_lines))


def patch_crawlee_version_in_uv_project(project_path: Path, wheel_path: Path):
    shutil.copy(wheel_path, project_path)

    _inject_pip_install_crawlee_from_whl_to_docker_file(docker_file=project_path/'Dockerfile',
                                                       wheel_name=wheel_path.name,
                                                       line_marker='COPY pyproject.toml uv.lock')

    subprocess.run(
        args=['uv', 'add', wheel_path.name],
        cwd=str(project_path),
        check=True,
        capture_output=True,
    )
    subprocess.run(
        args=['uv', 'lock'],
        cwd=str(project_path),
        check=True,
        capture_output=True,
    )
