import json, yaml
import os
from functools import wraps
from pathlib import Path
import inspect
from typing import Tuple

import pandas as pd
from jinja2 import FileSystemLoader, Environment, select_autoescape
from jinjasql import JinjaSql
from .filters import _inclause_str, _inclause

from mipi_datamanager import connection
from mipi_datamanager.core.common import dict_to_string
from mipi_datamanager.query import execute_sql_string

class JinjaLibrary:
    """
    Designates a directory to be a library of Jinja script templates, they can be executed using methods of this object.
    Leverages Jinja to insert parameters into the script and incorporate logic, this allows scripts to be highly modular.
    See [Jinja2 official documentation](https://jinja.palletsprojects.com/en/3.1.x/) for more details on Jinja syntax.

    Args:
        root_dir: Path to the directory to use as the workspace
    """

    def __init__(self, root_dir: str):

        # Jinja Envionment
        self.file_loader = FileSystemLoader(root_dir)
        self.environment = Environment(loader=self.file_loader,
                                       autoescape=select_autoescape(
                                           enabled_extensions=['html'],  # Enable autoescape for HTML
                                           disabled_extensions=['txt'],  # Disable autoescape for TXT
                                           default_for_string=False  # Disable autoescape for any other types by default
                                       ))

        # whitespace control
        self.environment.trim_blocks = True
        self.environment.lstrip_blocks = True
        self.environment.keep_trailing_newline = True

        # JinjaSql Env
        self.j = JinjaSql(env=self.environment, param_style='pyformat')
        self.j.env.filters['inclause_str'] = _inclause_str
        self.j.env.filters['inclause'] = _inclause

        # Constants
        self.temp_path = Path(__file__).parent.parent / "templates"  # TODO is this needed?
        self.dox_temp_path = self.temp_path/ "jinja_header.txt"  # TODO is this needed?

    def resolve_file(self, inner_path: str, jinja_parameters_dict: dict, header: bool = False) -> str:
        """
        Resolves a template file into a valid SQL string.

        Args:
            inner_path: path from the workspace root to the template file
            jinja_parameters_dict: dictionary of parameters to pass into the jinja tags
            header: If true adds a header to the resolved sql script including information about the parameters used

        Returns: SQL query string

        """

        if not jinja_parameters_dict:
            jinja_parameters_dict = {}

        template = self.environment.get_template(inner_path)

        query, bind_parms = self.j.prepare_query(template, jinja_parameters_dict)
        formatted_query = query % bind_parms

        if header is True:
            formatted_query = self._get_header(inner_path, jinja_parameters_dict, bind_parms) + formatted_query

        return formatted_query

    def execute_file(self, inner_path: str, connection: connection.Odbc,
                     jinja_parameters_dict: dict = None) -> pd.DataFrame:
        """
        Resolves the jinja query and executes it against the specified connection.

        Args:
            inner_path: Path to the template starting from root path
            jinja_parameters_dict: dictionary of jinja args. keys much match the tags in the jinja template
            connection: odbc connection object

        Returns: Pandas Dataframe

        """

        sql = self.resolve_file(inner_path, jinja_parameters_dict)
        return execute_sql_string(sql, connection)

    def _get_header(self, inner_path, jinja_parameters_dict: dict, bind_dict,
                    dox=None) -> str:

        """Creates a header for a jinja template, contains:
        - Header disclamer and best practice reminder
        - search path used for jinja env
        - jinja_parameters_dict assigned
        - bind_parms used for render"""

        search_path = self.file_loader.searchpath

        jinja_parameters_dict = dict_to_string(jinja_parameters_dict)
        bind_parms = dict_to_string(bind_dict)

        with open(self.dox_temp_path, "r") as f:
            header = f.read().format(search_path[0], jinja_parameters_dict, bind_parms, dox)

        return header

    def export_sql(self, inner_path: str, jinja_parameters_dict: dict, out_path: str) -> None:

        """
        Exports a resolved sql script to an external location.


        Args:
            inner_path: Path to the template, starting from the library root path
            jinja_parameters_dict: dictionary of jinja args. Keys much match the tags in the jinja template
            out_path: Path to export sql script to.

        Returns:

        """

        sql = self.resolve_file(str(inner_path), jinja_parameters_dict, header=True)

        with open(out_path, "w") as o:
            o.write(sql)

def bind_to_default_config_jinja_parameters(func_):
    @wraps(func_)
    def _inner(*args, **kwargs):
        sig = inspect.signature(func_)
        bound = sig.bind_partial(*args, **kwargs)

        # get jinja_params from signature
        orig = bound.arguments.get("jinja_parameters_dict", None) or {}

        # get jinja_params_from_config
        jinjarepo:JinjaRepo = bound.arguments.get("self")

        inner_path = bound.arguments.get("inner_path")
        if inner_path is None:
            raise TypeError(f"{func_.__name__} missing required argument 'inner_path'")
        defaults = jinjarepo._get_default_jinja_params_from_config(inner_path) or {}

        merged = {**defaults, **orig}
        bound.arguments["jinja_parameters_dict"] = merged

        return func_(**bound.arguments)

    return _inner



class JinjaRepo(JinjaLibrary):
    """
    Declares a local directory to be a repository of Jinja Templates. The repo will contain a `master_config.yaml`,
    which stores meta data on each script. Scripts can be preconfigured based on their join keys and connection, and
    default jinja parameters. See below on how to auto generate dox on the repo templates.

    !!! tip "New User Tip"

        This is an advanced function. You do NOT need to use this for basic MiPi functions.
        We recommend starting by placing all sql scripts in a folder, then using the other constructors and joiners first
        (ie from_sql, join_from_jinja...).

    !!! TODO "TODO COMING SOON CLI Commands"
        - `mipi-build-dox` - Build markdown documentation.

    `master_config.yaml` Contents:

        - name: A descriptive DataManager frame name for developers.
        - join_key: Column from the DataManager Target population which will generate the temp table and insert into this script. (dimension script only).
        - insert_table_name: Jinja tag nam used to insert temp table
        - connection: Connection name in JinjaRepo.conn_dict
        - description: A description of the script used to generate documentation
        - population: true if a populaiton script else false. If false, a join_key and insert_table_name will be expected.
        - jinja_parameters_dict: Dictionary of default jinja parameters used to generate documentation.

    Args:
        root_dir: Root directory of the repo. Must contain master_config.yaml.
        conn_dict: Specifies MiPi connection objects available for use by this repo. Key is the connection name, that
            will be specified in master_config.yaml, and the value is the MiPi Connection object.

    Examples:
        Below is a python script which uses the jinja repository, it is followed by the corresponding yaml file, and
        finally the output!!

        # master_config.yaml
        ```yaml
            "population/transactions":
                "sales.sql":
                    "meta":
                        "name": "sales_transactions"
                        "join_key": null
                        "insert_table_name": null
                        "connection": "my_con1"
                        "description": "Returns a record of all sales and the product sold for a given date range. Primary key is 'TRANSACTION_ID'."
                        "population": true
                    "jinja_parameters_dict":
                        "start_date": "2023-01-01",
                        "end_date": "2023-12-31"
            "dimension/employees":
                "sale_price.sql":
                    "meta":
                        "name": "sale_price"
                        "join_key": "TRANSACTION_ID"
                        "insert_table_name": "MiPiTempTable"
                        "connection": "my_con2"
                        "description": "Returns the sales price for all 'TRANSACTION_ID's. Use 'apply_discount=True' for
                            discounted price else retail price will be shown."
                        "population": true
                    "jinja_parameters_dict":
                        "apply_discount": true
            "dimension/employees":
                "sales_person.sql":
                    "meta":
                        "name": "employee_credited_for_sale"
                        "join_key": "TRANSACTION_ID"
                        "insert_table_name": "MiPiTempTable"
                        "connection": "my_con2"
                        "description": "Returns the sales person credited with the sale of each 'TRANSACTION_ID's."
                        "population": true
                    "jinja_parameters_dict": null
        ```

        # main.py
        ```python
        from coopermipi.odbc import Odbc

        repo = JinjaRepo("C:/path/to/repo",
                         conn_dict={"my_con1": Odbc(dsn="my_dsn1"),
                                    "my_con2": Odbc(dsn="my_dsn2")})

        dm = DataManager.from_jinja_repo("population/transactions/sales.sql", repo,
                                         jinja_parameters_dict={"date_start": "2024-01-03",
                                                                "date_end": "2024-01-03"})
        dm.join_from_jinja_repo("dimension/transactions/sale_price.sql",
                                jinja_parameters_dict={use_sale_price = True})
        dm.join_from_jinja_repo("dimension/employees/sales_person.sql")
        ```

        # Results of the code
        | TRANSACTION_ID | product  | sale_price | sales_person |
        |----------------|----------|------------|--------------|
        | 1              | Ford     | $31,000    | Jeff         |
        | 2              | Kia      | $27,000    | Mary         |
        | 3              | Honda    | $21,000    | Joe          |

    See Also:
        - Connections
    """

    def __init__(self, root_dir: str, conn_dict:dict=None):

        if root_dir is None:
            _path = os.environ.get("JINJA_REPO_PATH")
        else:
            _path = root_dir

        self.root_dir = Path(_path)
        self.conn_dict = conn_dict

        # override dox template
        super().__init__(root_dir)
        self.master_config = self.pull_master_config()
        self.dox_temp_path = self.temp_path / "jinja_repo_header.txt"

    def _split_inner_path(self, path: Path | str) -> Tuple[Path, str]:
        _path = Path(path)
        return _path.parent, _path.name

    def _get_config(self, parent: Path, name: str):
        posix = parent.as_posix()
        return self.master_config[posix][name]

    def get_config(self, path: Path | str) -> dict:
        parent, file = self._split_inner_path(path)
        return self._get_config(parent, file)


    def _get_header(self, inner_path, jinja_parameters_dict: dict, bind_dict, dox=None) -> str:
        _path = Path(inner_path)
        return super()._get_header(inner_path, jinja_parameters_dict, bind_dict,
                                   dox=self.get_config(inner_path)["meta"]["description"])

    def _get_default_jinja_params_from_config(self, inner_path):
        _path = Path(inner_path)
        return self.get_config(inner_path).get("jinja_parameters_dict",{})

    @property
    def path_master_config(self):
        return self.root_dir / "master_config.yaml"

    def pull_master_config(self):
        with open(self.path_master_config, "r") as f:
            data = yaml.safe_load(f)
        return data

    def __repr__(self):
        return f"SQL repository at: {self.root_dir}"

    @bind_to_default_config_jinja_parameters
    def resolve_file(self, inner_path: str, jinja_parameters_dict: dict, header: bool = False) -> str:
        return super().resolve_file(inner_path, jinja_parameters_dict, header)

    @bind_to_default_config_jinja_parameters
    def execute_file(self, inner_path: str, connection: connection.Odbc = None, jinja_parameters_dict: dict = None) -> pd.DataFrame:
        if connection is None:
            _inner_path = Path(inner_path)
            _connection = self.get_config(inner_path)["meta"]["connection"]
            _connection = self.conn_dict[_connection]
        else:
            _connection = connection

        # note: merged dict is now in the right spot
        return super().execute_file(inner_path, _connection, jinja_parameters_dict)

    @bind_to_default_config_jinja_parameters
    def export_sql(self, inner_path: str, jinja_parameters_dict: dict, out_path: str) -> None:
        return super().export_sql(inner_path, jinja_parameters_dict, out_path)