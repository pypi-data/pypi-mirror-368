import select
import subprocess

from shoestring_assembler.model import SolutionModel
from shoestring_assembler.interface.events import (
    Audit,
    Update,
    Progress,
    ProgressSection,
)
from shoestring_assembler.interface.events.progress import ProgressBar

from pathlib import Path
import yaml
import json


# TODO - look at --progress json tag for all operations


class Docker:
    @staticmethod
    def base_compose_command(solution_model):
        return [
            "docker",
            "compose",
            "--project-directory",
            str(solution_model.fs.root),
            "-f",
            str(solution_model.fs.compose_file),
            "--env-file",
            str(solution_model.fs.env_file),
        ]

    @classmethod
    async def build(cls, solution_model: SolutionModel):
        command = [
            *Docker.base_compose_command(solution_model),
            "build",
        ]
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        out_buffer = bytearray()
        err_buffer = bytearray()
        while process.returncode == None:
            while True:
                out_line = None
                err_line = None
                no_stdout = False
                no_stderr = False

                read_list, _wlist, _xlist = select.select(
                    [process.stderr, process.stdout], [], [], 1
                )
                if process.stderr in read_list:
                    char = process.stderr.read(1)
                    if char == b"\n":
                        err_line = err_buffer.decode()
                        err_buffer.clear()
                    elif char:
                        err_buffer += char
                    else:
                        no_stdout = True  # end of file
                else:
                    no_stdout = True  # timeout - break to check if process terminated

                if process.stdout in read_list:
                    char = process.stdout.read(1)
                    if char == b"\n":
                        out_line = out_buffer.decode()
                        out_buffer.clear()
                    elif char:
                        out_buffer += char
                    else:
                        no_stderr = True  # end of file
                else:
                    no_stderr = True  # timeout - break to check if process terminated

                if no_stdout and no_stderr:
                    break

                if out_line:
                    await Update.InfoMsg(f"[white]{out_line}", detail_level=2)
                if err_line:
                    await Update.SuccessMsg(f"{err_line}")

            process.poll()

        process.wait()

        return process.returncode == 0

    @classmethod
    async def setup_containers(cls, solution_model: SolutionModel):
        for service_name, service_spec in solution_model.compose_spec[
            "services"
        ].items():
            setup_cmd = service_spec.get("x-shoestring-setup-command")
            if setup_cmd:
                command = [
                    *Docker.base_compose_command(solution_model),
                    "run",
                    "--rm",
                    service_name,
                ]
                if isinstance(setup_cmd, list):
                    command.extend(setup_cmd)
                else:
                    command.append(setup_cmd)
                outcome = subprocess.run(command, capture_output=False)
                Update.InfoMsg(outcome.returncode)

    @classmethod
    async def start(cls, solution_model: SolutionModel):
        command = [
            *Docker.base_compose_command(solution_model),
            "--progress",
            "json",
            "up",
            "-d",
            "--remove-orphans",
        ]

        print
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        progress_trackers: dict[str, ProgressBar] = {}
        network_status_map = {"Creating": 2, "Created": 4}
        container_status_map = {
            "Creating": 1,
            "Created": 2,
            "Starting": 3,
            "Started": 4,
            "Running": 4,
        }

        async def handle_line(line_content):
            id_string: str = line_content.get("id")
            target_type, _, target_id = id_string.partition(" ")
            target_id = target_id.removesuffix("-1")
            if target_id not in progress_trackers.keys():
                progress_trackers[target_id] = await Progress.new_tracker(
                    target_id.strip(), target_id, 4, 0
                )
            status = line_content.get("status")
            if target_type == "Network":
                value = network_status_map.get(status)
            else:
                value = container_status_map.get(status)
            await progress_trackers[target_id].update(value)

        async with ProgressSection("start"):
            await parse_docker_json_progress(process, handle_line)

        return process.returncode == 0

    @classmethod
    async def stop(cls, solution_model: SolutionModel):
        command = [
            *Docker.base_compose_command(solution_model),
            "--progress",
            "json",
            "down",
        ]
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        progress_trackers: dict[str, ProgressBar] = {}
        status_map = {"Stopping": 1, "Stopped": 2, "Removing": 3, "Removed": 4}

        async def handle_line(line_content):
            id_string: str = line_content.get("id")
            target_type, _, target_id = id_string.partition(" ")
            target_id = target_id.removesuffix("-1")
            if target_id not in progress_trackers.keys():
                progress_trackers[target_id] = await Progress.new_tracker(
                    target_id.strip(), target_id, 4, 0
                )
            status = line_content.get("status")
            await progress_trackers[target_id].update(status_map.get(status))

        async with ProgressSection("stop"):
            await parse_docker_json_progress(process, handle_line)

        return process.returncode == 0


async def parse_docker_json_progress(process: subprocess.Popen, callback):
    out_buffer = bytearray()
    err_buffer = bytearray()
    while process.returncode == None:
        while True:
            out_line = None
            err_line = None
            no_stdout = False
            no_stderr = False

            read_list, _wlist, _xlist = select.select(
                [process.stderr, process.stdout], [], [], 1
            )

            if process.stderr in read_list:
                char = process.stderr.read(1)
                if char == b"\n":
                    err_line = err_buffer.decode()
                    err_buffer.clear()
                elif char:
                    err_buffer += char
                else:
                    no_stdout = True  # end of file
            else:
                no_stdout = True

            if process.stdout in read_list:
                char = process.stdout.read(1)
                if char == b"\n":
                    out_line = out_buffer.decode()
                    out_buffer.clear()
                elif char:
                    out_buffer += char
                else:
                    no_stderr = True  # end of file
            else:
                no_stderr = True

            if no_stdout and no_stderr:
                break  # timeout - break to check if process terminated

            if out_line:
                try:
                    line_content = json.loads(out_line)
                    await callback(line_content)
                except:
                    pass
            if err_line:
                try:
                    line_content = json.loads(err_line)
                    if "error" in line_content.keys():
                        await Update.ErrorMsg(line_content["message"])
                    else:
                        await callback(line_content)
                except:
                    pass

        process.poll()

    process.wait()
