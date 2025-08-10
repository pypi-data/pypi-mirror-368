#!/usr/bin/env python3
#
"""
    Esté módulo serve para manipulação de arquivos, diretórios e documentos
entre outros. Não depende de módulos externos apenas de builtins e stdlib.
"""
from __future__ import annotations
from enum import Enum
import os
import json
import platform
from pathlib import Path
from hashlib import md5

# Windows / Linux / ...
KERNEL_TYPE = platform.system()


class ExtensionFiles(Enum):

    PNG = '.png'
    JPG = '.jpg'
    JPEG = '.jpeg'
    SVG = '.svg'
    PDF = '.pdf'
    XLSX = '.xlsx'
    XLS = '.xls'
    CSV = '.csv'
    ODS = '.ods'
    JSON = '.json'


class LibraryDocs(Enum):
    """
        Enum para tipos de documentos como imagens, PDFs, Planilhas e JSON.
    """

    IMAGE = ['.png', '.jpg', '.jpeg', '.svg']
    PDF = ['.pdf']
    DOCUMENTS = ['.png', '.jpg', '.jpeg', '.svg', '.pdf']
    #
    EXCEL = ['.xlsx', '.xls']
    CSV = ['.csv', '.txt']
    ODS = ['.ods']
    #
    SHEET = ['.csv', '.txt', '.xlsx', '.xls', '.ods']
    JSON = ['.json']
    #
    ALL_DOCUMENTS = [
        '.png', '.jpg', '.jpeg', '.svg',
        '.csv', '.txt', '.xlsx', '.xls', '.ods',
        '.pdf',
        '.json',
    ]
    #
    ALL = None


class File(object):
    def __init__(self, filename: str):
        if os.path.isdir(filename):
            raise ValueError(f'{__class__.__name__} File() não pode ser um diretório.')
        self.filename: str = os.path.abspath(filename)
        self.__path: Path = Path(self.filename)

    @property
    def path(self) -> Path:
        return self.__path
    
    @path.setter
    def path(self, new: Path):
        if not isinstance(new, Path):
            return
        self.__path = new
        
    def __eq__(self, value):
        if not isinstance(value, File):
            return NotImplemented
        return self.absolute() == value.absolute()
    
    def __hash__(self):
        return self.absolute().__hash__()

    def is_image(self) -> bool:
        try:
            return True if self.extension() in LibraryDocs.IMAGE.value else False
        except:
            return False

    def is_pdf(self) -> bool:
        try:
            return True if self.extension() in LibraryDocs.PDF.value else False
        except:
            return False
        
    def is_excel(self) -> bool:
        try:
            return True if self.extension() in LibraryDocs.EXCEL.value else False
        except:
            return False
        
    def is_csv(self) -> bool:
        try:
            return True if self.extension() in LibraryDocs.CSV.value else False
        except:
            return False

    def is_sheet(self) -> bool:
        try:
            return True if self.extension() in LibraryDocs.SHEET.value else False
        except:
            return False

    def is_json(self) -> bool:
        try:
            return True if self.extension() in LibraryDocs.JSON.value else False
        except:
            return False

    def is_ods(self):
        try:
            return True if self.extension() in LibraryDocs.ODS.value else False
        except:
            return False

    def update_extension(self, e: str) -> File:
        """
            Retorna uma instância de File() no mesmo diretório com a nova
        extensão informada.
        """
        current = self.extension()
        full_path = self.absolute().replace(current, '')
        return File(os.path.join(f'{full_path}{e}'))

    def get_text(self) -> str | None:
        try:
            return self.__path.read_text()
        except Exception as e:
            print(e)
            return None

    def write_string(self, s: str):
        if s is None:
            return False
        try:
            self.__path.write_text(s)
        except Exception as e:
            print(e)
            return False
        else:
            return True

    def write_list(self, items: list[str]) -> bool:
        # Abrindo o arquivo em modo de escrita
        if len(items) == 0:
            return False
        try:
            with open(self.filename, "w", encoding="utf-8") as file:
                for string in items:
                    file.write(string + "\n")  # Adiciona uma quebra de linha após cada string
        except Exception as e:
            print(e)
            return False
        else:
            return True

    def name(self):
        e = self.extension()
        if (e is None) or (e == ''):
            return os.path.basename(self.filename)
        return os.path.basename(self.filename).replace(e, '')
    
    def name_absolute(self) -> str:
        e = self.extension()
        if (e is None) or (e == ''):
            return self.filename
        return self.filename.replace(e, '')

    def extension(self) -> str:
        return self.__path.suffix

    def dirname(self) -> str:
        return os.path.dirname(self.filename)

    def basename(self) -> str:
        return os.path.basename(self.filename)

    def exists(self) -> bool:
        return self.__path.exists()

    def absolute(self) -> str:
        return self.filename
    
    def size(self):
        return os.path.getsize(self.filename)
    
    def md5(self) -> str | None:
        """Retorna a hash md5 de um arquivo se ele existir no disco."""
        if not self.path.exists():
            return None
        _hash_md5 = md5()
        with open(self.absolute(), "rb") as f:
            for _block in iter(lambda: f.read(4096), b""):
                _hash_md5.update(_block)
        return _hash_md5.hexdigest()


class Directory(object):
    def __init__(self, dirpath:str):
        self.dirpath: str = os.path.abspath(dirpath)
        self.path: Path = Path(self.dirpath)
        
    def __eq__(self, value):
        if not isinstance(value, Directory):
            return NotImplemented
        return self.absolute() == value.absolute()
    
    def __hash__(self):
        return self.absolute().__hash__()
        
    def iterpaths(self) -> list[Path]:
        return list(self.path.rglob('*'))

    def __content_recursive(self) -> list[File]:
        _paths = self.iterpaths()
        values = []
        for p in _paths:
            if p.is_file():
                values.append(
                    File(os.path.abspath(p.absolute()))
                )
        return values

    def __content_no_recursive(self) -> list[File]:
        content_files: list[str] = os.listdir(self.absolute())
        values: list[File] = []
        for file in content_files:
            fp: str = os.path.join(self.absolute(), file)
            if os.path.isfile(fp):
                values.append(
                    File(os.path.abspath(fp))
                )
        return values

    def content_files(self, *, recursive: bool = True) -> list[File]:
        if recursive:
            return self.__content_recursive()
        return self.__content_no_recursive()

    def content_dirs(self, recursive: bool = True) -> list[Directory]:
        values: list[Directory] = []
        if recursive:
            _paths = self.iterpaths()
            for p in _paths:
                if p.is_dir():
                    values.append(
                        Directory(os.path.abspath(p.absolute()))
                    )
        else:
            _paths = os.listdir(self.absolute())
            for d in _paths:
                _dirpath = os.path.join(self.absolute(), d)
                if os.path.isdir(_dirpath):
                    values.append(
                        Directory(os.path.abspath(_dirpath))
                    )
        return values
    
    def basename(self) -> str:
        return os.path.basename(self.absolute())

    def mkdir(self):
        try:
            os.makedirs(self.absolute())
        except:
            pass

    def absolute(self) -> str:
        return self.dirpath

    def concat(self, d: str, create: bool = False) -> Directory:
        if create:
            try:
                os.makedirs(os.path.join(self.absolute(), d))
            except:
                pass
        return Directory(os.path.join(self.absolute(), d))

    def parent(self) -> Directory:
        return Directory(
            os.path.abspath(self.path.parent)
        )

    def join_file(self, name:str) -> File:
        return File(
            os.path.join(self.absolute(), name)
        )
   
   
class InputFiles(object):
    """
        Obeter uma lista de arquivos/documentos do diretório informado.
    """
    def __init__(self, d: Directory, *, maxFiles: int = 5000):
        if not isinstance(d, Directory):
            raise ValueError(f'{__class__.__name__}\nUse: Directory(), não {type(d)}')
        self.input_dir: Directory = d
        self.maxFiles: int = maxFiles
        
    def get_files_with(self, *, infile: str, sort: bool = True) -> list[File]:
        """
            Retorna arquivos que contém a ocorrência (infile) no nome absoluto.
        """
        content_files: list[File] = []
        count: int = 0
        paths = self.input_dir.iterpaths()
        for file in paths:
            if not file.is_file():
                continue
            if infile in os.path.abspath(file.absolute()):
                content_files.append(
                        File(os.path.abspath(file.absolute()))
                    )
                count += 1
            if count >= self.maxFiles:
                break
        return content_files

    def __get_files_recursive(self, *, file_type: LibraryDocs, sort: bool) -> list[File]:
        #
        _paths: list[Path] = self.input_dir.iterpaths()
        _all_files = []
        count: int = 0
        if file_type == LibraryDocs.ALL:
            # Todos os tipos de arquivos
            for p in _paths:
                if not p.is_file():
                    continue
                _all_files.append(
                    File(os.path.abspath(p.absolute()))
                )
                count += 1
                if count >= self.maxFiles:
                    break
        else:
            # Arquivos especificados em LibraryDocs
            for p in _paths:
                if not p.is_file():
                    continue
                if (p.suffix is None) or (p.suffix == ''):
                    continue
                if p.suffix in file_type.value:
                    _all_files.append(
                        File(os.path.abspath(p.absolute()))
                    )
                    count += 1
                if count >= self.maxFiles:
                    break
        if sort:
            _all_files.sort(key=File.absolute)
        return _all_files

    def __get_files_no_recursive(self, *, file_type: LibraryDocs, sort: bool) -> list[File]:
        _content_files: list[File] = self.input_dir.content_files(recursive=False)
        _all_files: list[File] = []
        count: int = 0

        if file_type == LibraryDocs.ALL:
            # Todos os tipos de arquivos
            for file in _content_files:
                _all_files.append(file)
                count += 1
                if count == self.maxFiles:
                    break
        else:
            # Arquivos especificados em LibraryDocs
            for file in _content_files:
                if file.extension() in file_type.value:
                    _all_files.append(file)
                    count += 1
                    if count == self.maxFiles:
                        break
        if sort:
            _all_files.sort(key=File.absolute)
        return _all_files

    def get_files(
                self, *,
                file_type: LibraryDocs = LibraryDocs.ALL_DOCUMENTS,
                sort: bool = True,
                recursive: bool = True
            ) -> list[File]:
        """
            Retorna uma lista de File() de acordo com o tipo de arquivo
        especificado.
        - LibraryDocs.ALL_DOCUMENTS => Retorna todos os documentos do diretório.
        - LibraryDocs.EXCEL         => Retorna arquivos que são planilhas excel.
        - ...
        
        """
        if recursive:
            return self.__get_files_recursive(file_type=file_type, sort=sort)    
        return self.__get_files_no_recursive(file_type=file_type, sort=sort)


class JsonData(object):
    """
        Representação de um dado JSON apartir de uma string python.
    """
    def __init__(self, string:str):
        if not isinstance(string, str):
            raise ValueError(f'{__class__.__name__} o JSON informado precisa ser do tipo string, não {type(string)}')
        self.jsonString:str = string
        
    def is_null(self) -> bool:
        if (self.jsonString is None) or (self.jsonString == ''):
            return True
        return False
       
    def to_string(self) -> str:
        return self.jsonString
        
    def to_dict(self) -> dict[str, object]:
        """
            Exportar/Converter o dado atual em um dicionário python.
        """
        return json.loads(self.jsonString)

    def to_file(self, f:File):
        """Exportar o dado atual para um arquivo .json"""
        _data:str = json.loads(self.jsonString)
        with open(f.absolute(), "w", encoding="utf-8") as file:
            json.dump(_data, file, indent=4, ensure_ascii=False)


class JsonConvert(object):
    """
        Conversão de um dado JSON em dados python
    """
    def __init__(self, jsonData: JsonData):
        self.jsonData: JsonData = jsonData
        
    def to_json_data(self) -> JsonData:
        return self.jsonData
    
    @classmethod
    def from_file(cls, file: File) -> JsonConvert:
        """
            Gerar um dado JsonData apartir de um arquivo .json
        """
        # Ler o arquivo e carregar o JSON em um dicionário Python
        data = None
        try:
            with open(file.absolute(), "r", encoding="utf-8") as fp:
                data: str = json.load(fp)
        except Exception as e:
            print(f'{__class__.__name__}\n{e}')
            return cls(JsonData(''))
        else:
            return cls(JsonData(json.dumps(data, indent=4, ensure_ascii=False, sort_keys=True)))
    
    @classmethod
    def from_string_json(cls, data: str) -> JsonConvert:
        """
            Gerar um dado JsonData apartir de uma string.
        """
        json_string = json.dumps(data, indent=4, ensure_ascii=False, sort_keys=True)
        return cls(JsonData(json_string))

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> JsonConvert:
        """
            Converte um dicionário em objeto JSON/JsonData.
        """
        if not isinstance(data, dict):
            raise ValueError(f'{__class__.__name__} Informe um JSON em formato dict, não {type(data)}')
        json_string = json.dumps(data, indent=4, ensure_ascii=False, sort_keys=True)
        return cls(JsonData(json_string))
    

class UserFileSystem(object):
    """
        Diretórios comuns para cache e configurações de usuário.
    """
    def __init__(self, base_home: Directory = Directory(os.path.abspath(Path().home()))):
        self.baseHome:Directory = base_home
        self.userDownloads:Directory = self.baseHome.concat('Downloads', create=True)
        self.userVarDir:Directory = self.baseHome.concat('var', create=True)
        
    def config_dir(self) -> Directory:
        return self.userVarDir.concat('config', create=True)
    
    def cache_dir(self) -> Directory:
        return self.userVarDir.concat('cache', create=True)
    
    
class UserAppDir(object):
    """
        Diretório comun para cache e configurações do aplicativo.
    """
    def __init__(self, appname: str, *, user_file_system: UserFileSystem = UserFileSystem()):
        self.appname = appname
        self.userFileSystem: UserFileSystem = user_file_system
        self.workspaceDirApp: Directory = self.userFileSystem.userDownloads.concat(self.appname, create=True)
        self.installDir: Directory = self.userFileSystem.userVarDir.concat('opt').concat(self.appname, create=True)
        
    def cache_dir_app(self) -> Directory:
        return self.userFileSystem.cache_dir().concat(self.appname, create=True)
    
    def config_dir_app(self) -> Directory:
        return self.userFileSystem.config_dir().concat(self.appname, create=True)
    
