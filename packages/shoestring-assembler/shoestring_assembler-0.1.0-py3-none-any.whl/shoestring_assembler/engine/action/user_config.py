import jinja2
from pathlib import Path
import sys
import os
import re
from shoestring_assembler.interface.events import Update
from shoestring_assembler.model import SolutionModel, ServiceModuleModel

version_regex = re.compile("^\s*(\d+)\.(\d+)\s*$")


class UserConfig:
    @staticmethod
    async def configure(solution_model: SolutionModel):
        await Update.StepHeading("Configuring User Config")
        for service_module in solution_model.service_modules:
            if service_module.user_config.requires_configuration:
                await UserConfig.apply_template(service_module)

        await Update.SuccessMsg(f"User config ready")

    @staticmethod
    async def apply_template(sm: ServiceModuleModel):
        # setup for template engine
        jinja2_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(sm.user_config.template.fs.dir)
        )

        rel_dir_list, rel_file_list = await sm.user_config.template.fs.get_files()

        for dir_rel_path in rel_dir_list:  # make directories as needed
            sm.user_config.fs.ensure_directory(dir_rel_path)

        for file_rel_path in rel_file_list:  # render each template file
            templ = jinja2_env.get_template(str(file_rel_path))
            dest_file = sm.user_config.fs.get_file(file_rel_path)
            with dest_file.open("w") as f:
                for segment in templ.generate(sm.user_config.context):
                    f.write(segment)

        # write version file
        sm.user_config.version = sm.user_config.template.version

        # write answers
        sm.user_config.prev_answers = sm.user_config.answers





"""
Consider in Future:
* Looping prompts - e.g. power factor entry in PM analysis
* Cross service module references - e.g. fetch all specified machine names and loop over them
"""
