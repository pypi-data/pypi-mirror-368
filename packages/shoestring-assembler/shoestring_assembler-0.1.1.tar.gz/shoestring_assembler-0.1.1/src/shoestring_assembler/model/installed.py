from shoestring_assembler.constants import Constants
from shoestring_assembler.model.common import ModelMap
from shoestring_assembler.model.solution import SolutionModel
from shoestring_assembler.model.recipe import NoRecipeError
from shoestring_assembler.interface.events import FatalError, Update
import json
from pathlib import Path

class InstalledSolutionsModel:
    def __init__(self):
        self.__solutions = None
        self.__file = Path(Constants.INSTALLED_SOLUTIONS_LIST)
        if not self.__file.parent.exists():
            self.__file.parent.mkdir()

    @property
    def solutions(self):
        return self.__solutions

    async def saturate_solutions(self):
        try:
            with self.__file.open() as f:
                contents = f.read()
                if contents != "":
                    install_dirs = json.loads(contents)
                else:
                    install_dirs = {}
        except FileNotFoundError:
            install_dirs = {}

        definition = {name:{"root_dir":path} for name,path in install_dirs.items()}
        self.__solutions = ModelMap.generate(SolutionModel, definition)
        for solution in self.__solutions:
            try:
                await solution.saturate()
            except NoRecipeError:
                pass

    async def add_solution(self,path):
        solution = SolutionModel(root_dir=path)
        try:
            await solution.saturate()
        except NoRecipeError as err:
            await Update.ErrorMsg(f"No recipe found for solution at {path}")
            return err

        try:
            with self.__file.open() as f:
                contents = f.read()
                if contents != "":
                    install_dirs = json.loads(contents)
                else:
                    install_dirs = {}
        except FileNotFoundError:
            install_dirs = {}

        try:
            with self.__file.open('w') as f:
                try:
                    json.dump({**install_dirs,solution.solution_details.name:str(path)},f)
                    self.__solutions[solution.solution_details.name] = solution
                except:
                    json.dump(install_dirs,f)
                    raise
        except FileNotFoundError:
            raise

        return solution
