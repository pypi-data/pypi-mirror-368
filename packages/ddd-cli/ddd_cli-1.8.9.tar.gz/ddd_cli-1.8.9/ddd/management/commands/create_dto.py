from .utils import *
from colorama import Fore, Style

class CreateDTOCommand:
    def __init__(self, subparsers):
        parser = subparsers.add_parser('create-dto', help='Create a new DTO')
        parser.add_argument('app_path', type=str, help='The relative path of the app within the project (for example, "apps/app1")')
        parser.add_argument('dto_name', type=str, help='The name of the DTO')
        parser.add_argument(
            '--split', action='store_true', help='Create a separate file for this DTO'
        )        
        parser.add_argument("--simulate", action="store_true", help="Simulate the creation of this entity without writing files")
        parser.set_defaults(func=self.execute) 

    def execute(self, args):
        self.create_dto(args.app_path, args.dto_name, args.split, args.simulate)

    def create_dto(self, app_path, dto_name, split=False, simulate=False, **kwargs):
        """Crea un nuevo DTO"""
        dtos_dir = app_path if not split else os.path.join(app_path, 'dtos')
        dtos_path = os.path.join(dtos_dir, 'dtos.py') if not split else os.path.join(dtos_dir, dto_name.lower() + '_dto.py')

        if not simulate:
            # Crear directorios si no existen
            try:
                os.makedirs(dtos_dir, exist_ok=True)

                # Crear archivos __init__.py
                create__init__files(dtos_dir)
            except OSError as e:
                print(Fore.RED + f"Failed to create directory '{dtos_dir}': {e}" + Style.RESET_ALL)
                return
            
            #si split y ya existe el archivo mostrar error
            if split and os.path.exists(dtos_path):
                print(Fore.RED + f"File '{dtos_path}' already exists. Cannot create separate file" + Style.RESET_ALL)
                return

        # Escribir imports en el archivo 
        # si no existe el archivo template_imports
        if not os.path.exists(dtos_path) or simulate:
            readWriteTemplate(
                templateName='dto',
                fileName='imports.py',
                render_params={'dto_name': dto_name},
                repository_path=dtos_path,
                failIfError=True,
                simulate=simulate
            )

        readWriteTemplate(
            templateName='dto',
            fileName='class.py',
            render_params={'dto_name': dto_name},
            repository_path=dtos_path,
            failIfError=True,
            addition=True,
            simulate=simulate
        )
