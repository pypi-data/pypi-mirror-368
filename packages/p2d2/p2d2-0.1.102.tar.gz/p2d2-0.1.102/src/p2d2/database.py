import pickle
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from functools import cached_property
from pathlib import Path
from types import SimpleNamespace, MethodType
from typing import Type, Any, List, Dict, Generator

import pandas as pd
from fastj2 import FastJ2
from loguru import logger as log
from pandas import DataFrame
from toomanyconfigs import CWD, TOMLConfig
from toomanysessions import SessionedServer


@property
def row_count(self):
    return len(self)

def empty_dataframe_from_type(typ: Type, defvals: list = None):
    a = typ.__annotations__
    if not defvals: defvals = ["id", "created_on", "created_by" "modified_on", "modified_by"]
    for col in a:
        for name in defvals:
            if col == name: raise KeyError(f"Your database class cannot contain default values: {defvals}")
    df = pd.DataFrame(columns=a.keys()).astype(a)  # type: ignore
    return df

def get_title(self, index):
    return self.at[index, self.title]

def get_subtitle(self, index):
    return self.at[index, self.subtitle]

class Config(TOMLConfig):
    password: str = None


class PickleChangelog:
    def __init__(self, path: Path):
        self.path = path
        self._changelog: List[Dict] = []
        self.fetch()

    def __repr__(self):
        return f"[{self.path.name}]"

    def fetch(self):
        try:
            with open(self.path, 'rb') as f:
                self._changelog = pickle.load(f)
            log.debug(f"{self}: Loaded {len(self._changelog)} change records")
        except (FileNotFoundError, EOFError):
            # File doesn't exist or is empty
            self._changelog = []
            log.debug("No existing changelog found or empty file, starting fresh")

    def commit(self):
        with open(self.path, 'wb') as f:
            pickle.dump(self._changelog, f)
        log.debug(f"{self}: Saved {len(self._changelog)} change records to {self.path}")

    def log_change(self, table_name: str, change_type: str, signature: str, details: str = ""):
        change_record = {
            "timestamp": datetime.now().isoformat(),
            "table": table_name,
            "change_type": change_type,
            "signature": signature,
            "details": details
        }
        self._changelog.append(change_record)
        self.commit()

    def get_changelog(self, table_name: str = None, signature: str = None, change_type: str = None):
        filtered = self._changelog
        if table_name:
            filtered = [c for c in filtered if c["table"] == table_name]
        if signature:
            filtered = [c for c in filtered if c["signature"] == signature]
        if change_type:
            filtered = [c for c in filtered if c["change_type"] == change_type]
        return pd.DataFrame(filtered)


README = "Database backups are made once per day!"

class TableIndex(dict):
    list: list = []
    def __init__(self):
        super().__init__()

class TableProxy:
    def __init__(self, df, database, name, signature="system"):
        self.df = df
        self.db = database
        self.name = name
        self.signature = signature

    def create(self, signature = None, **kwargs):
        signature = signature or self.signature
        self.df = self.db.create(self.df, signature=signature, **kwargs)
        return self

    def update(self, updates: dict, signature = None, **conditions):
        signature = signature or self.signature
        self.df = self.db.update(self.df, updates, signature=signature, **conditions)
        return self

    def delete(self, **conditions):
        self.df = self.db.delete(self.df, **conditions)
        return self

    def read(self, **conditions):
        return self.db.read(self.df, **conditions)

class Database:
    def __init__(self,
            db_name=None
        ):
        try:
            _ = self.tables
        except KeyError:
            pass
        if db_name is None: db_name = "my_database"
        if not isinstance(db_name, str): raise RuntimeError
        self._name = db_name
        db = f"{self._name}.db"
        backups = "backups"
        self._cwd = CWD({
            f"{self._name}": {
                db: None,
                "changes.pkl": None,
                "config.toml": None,
                backups: {"README.md": README}
            }
        })
        self._path: Path = self._cwd.file_structure[0]
        self._backups: Path = self._cwd.cwd / self._name / backups
        self._default_columns = ["created_at", "created_by" "modified_at", "modified_by"]

        #initialize schema
        for item in self.__annotations__.items():
            a, t = item
            if a.startswith("_"): continue
            if hasattr(self, a): continue
            df = empty_dataframe_from_type(t, self._default_columns)
            df.insert(0, 'created_at', pd.Series(dtype='datetime64[ns]'))
            df.insert(1, 'created_by', pd.Series(dtype='str'))
            df.insert(2, 'modified_at', pd.Series(dtype='datetime64[ns]'))
            df.insert(3, 'modified_by', pd.Series(dtype='str'))
            setattr(self, a, df)

        self.fetch()
        _, _ = self._pkl, self._cfg
        self._api = API(self)

    def __repr__(self):
        return f"[{self._name}.db]"

    @cached_property
    def _cfg(self) -> Config:
        cfg = Config.create(self._cwd.file_structure[2])
        return cfg

    @cached_property
    def _pkl(self) -> PickleChangelog:
        path = self._cwd.file_structure[1]
        return PickleChangelog(path)

    @property
    def tables(self) -> TableIndex:
        index = TableIndex() #table index is a subclass of dict with a list attribute
        for attr_name, attr_type in self.__annotations__.items():
            if attr_name.startswith("_"): continue
            index[attr_name] = getattr(self, attr_name, None)
            if index[attr_name] is None: raise KeyError
        if index == {}: raise RuntimeError("Cannot initialize a database with no tables!")
        for item in index.keys():
            index.list.append(getattr(self, item))
        for item in index.list:
            metadata = {}
            metadata["row_count"] = len(item)
            metadata["column_count"] = len(item.columns)
            bytes_value = int(item.memory_usage(deep=True).sum())
            metadata["size_bytes"] = bytes_value
            metadata["size_kilobytes"] = round(bytes_value / 1024, 2)
            metadata["size_megabytes"] = round(bytes_value / (1024**2), 2)
            metadata["size_gigabytes"] = round(bytes_value / (1024**3), 6)
            analytics = SimpleNamespace(
                **metadata, as_dict=metadata
            )
            setattr(item, "analytics", analytics)

        return index

    def backup(self):
        today = date.today()
        folder = self._backups / str(today)

        if not any(self._backups.glob(f"{today}*")):
            log.warning(f"{self}: Backup not found for today! Creating...")
            folder.mkdir(exist_ok=True)
            if folder.exists():
                log.success(f"{self}: Successfully created backup folder at {folder}")
            else:
                raise FileNotFoundError

            for table_name, table_df in self.tables.items():
                backup_path = folder / f"{table_name}.parquet"
                table_df.to_parquet(backup_path)

    def peek(self):
        viewed = {}
        with sqlite3.connect(self._path) as conn:
            for table_name in self.tables.keys():
                try:
                    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
                    viewed[table_name] = df
                except pd.errors.DatabaseError:
                    # Table doesn't exist yet, use empty DataFrame
                    viewed[table_name] = self.tables[table_name]
        return viewed

    def fetch(self):
        with sqlite3.connect(self._path) as conn:
            successes = 0
            for table_name in self.tables.keys():
                try:
                    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
                    try:
                        setattr(df, "title", df.columns[4])
                        setattr(df, "get_title", MethodType(get_title, df))
                    except IndexError:
                        pass
                    try:
                        setattr(df, "subtitle", df.columns[5])
                        setattr(df, "get_subtitle", MethodType(get_subtitle, df))
                    except IndexError:
                        pass

                    setattr(self, table_name, df)
                    successes = successes + 1
                    log.debug(f"{self}: Read {table_name} from database")
                except pd.errors.DatabaseError:
                    log.debug(f"{self}: Table {table_name} doesn't exist, keeping empty DataFrame")

            if successes == 0:
                log.warning(f"{self}: No tables were successfully registered. "
                            f"This probably means the database is empty. Attempting to write...")
                self.commit(compare=False)
            else: log.success(f"{self}: Successfully loaded {successes} tables from {self._path}")

        self.backup()
        _ = self.tables

    def _compare(self, table_name: str, old: DataFrame, new: DataFrame, signature: str):
        """Compare old vs new DataFrame and log changes"""
        if old.equals(new):
            log.debug(f"{self}: No changes in {table_name}")
            self._pkl.log_change(table_name, "no_change", signature)
            return

        # Changes detected
        if old.shape == new.shape and (old.columns == new.columns).all():
            # Same structure, show detailed diff
            diff = old.compare(new)
            if not diff.empty:
                log.info(f"{self}: Changes in {table_name}:")
                log.info(diff)
                self._pkl.log_change(table_name, "updated", signature, f"Cell changes: {len(diff)} rows")
        else:
            # Structure changed
            row_diff = new.shape[0] - old.shape[0]
            if row_diff > 0:
                change_type = "rows_added"
            elif row_diff < 0:
                change_type = "rows_deleted"
            else:
                change_type = "structure_changed"

            log.info(f"{self}: Shape/structure changed in {table_name}: {old.shape} -> {new.shape}")
            self._pkl.log_change(table_name, change_type, signature, f"{old.shape} -> {new.shape}")

    def commit(self, signature: str = "system", compare: bool = True):
        viewed = self.peek() if compare else {}

        with sqlite3.connect(self._path) as conn:
            for table_name, table_df in self.tables.items():
                if compare and table_name in viewed:
                    self._compare(table_name, viewed[table_name], table_df, signature)
                elif compare:
                    log.info(f"{self}: New table: {table_name}")
                    self._pkl.log_change(table_name, "created", signature)

                table_df.to_sql(table_name, conn, if_exists='replace', index=False)
                log.debug(f"{self}: Wrote {table_name} to database")

    @contextmanager
    def table(self, table: str | DataFrame | Any, signature: str = "system") -> Generator[TableProxy]:
        if isinstance(table, str):
            table_name = table
            if table in self.tables.keys():
                table = self.tables[table]
        elif isinstance(table, DataFrame):
            table_name = None
            for name, df in self.tables.items():
                if df.equals(table):
                    table_name = name
                    break
            if table_name is None: raise ValueError("DataFrame content doesn't match any database table")
        else:
            raise TypeError

        proxy = TableProxy(table, self, table_name, signature)
        try:
            yield proxy
        finally:
            setattr(self, table_name, proxy.df)
            self.commit(signature=signature)

    def create(self, table: pd.DataFrame | Any, signature: str = "system", **kwargs):
        # Auto-set timestamps and user for default columns
        now = pd.Timestamp.now()

        if 'created_at' in table.columns and 'created_at' not in kwargs:
            kwargs['created_at'] = now
        if 'created_by' in table.columns and 'created_by' not in kwargs:
            kwargs['created_by'] = signature
        if 'modified_at' in table.columns and 'modified_at' not in kwargs:
            kwargs['modified_at'] = now
        if 'modified_by' in table.columns and 'modified_by' not in kwargs:
            kwargs['modified_by'] = signature

        new_row = pd.DataFrame([kwargs])
        updated_df = pd.concat([table, new_row], ignore_index=True)
        log.debug(f"{self}: Added row with signature={signature}: {kwargs}")
        return updated_df

    def read(self, table: pd.DataFrame | Any, **conditions):
        if not conditions:
            return table

        mask = pd.Series([True] * len(table))
        for col, value in conditions.items():
            mask &= (table[col] == value)

        result = table[mask]
        log.debug(f"{self}: Read {len(result)} rows with conditions: {conditions}")
        return result

    def update(self, table: pd.DataFrame | Any, updates: dict, signature: str = "system", **conditions):
        df = table.copy()

        # Auto-update modified fields - use string instead of Timestamp
        from datetime import datetime
        now = datetime.now().isoformat()
        if 'modified_at' in df.columns and 'modified_at' not in updates:
            updates['modified_at'] = now
        if 'modified_by' in df.columns and 'modified_by' not in updates:
            updates['modified_by'] = signature

        mask = pd.Series([True] * len(df))
        for col, value in conditions.items():
            mask &= (df[col] == value)

        for col, value in updates.items():
            df.loc[mask, col] = value

        updated_count = mask.sum()
        log.debug(f"{self}: Updated {updated_count} rows by {signature}: {updates}")
        return df

    def delete(self, table: pd.DataFrame | Any, **conditions):
        mask = pd.Series([True] * len(table))
        for col, value in conditions.items():
            mask &= (table[col] == value)

        result = table[~mask].reset_index(drop=True)
        deleted_count = len(table) - len(result)
        log.debug(f"{self}: Deleted {deleted_count} rows")
        return result


Database.c = Database.create
Database.r = Database.read
Database.u = Database.update
Database.d = Database.delete


class API(SessionedServer):
    def __init__(self, db: Database):
        super().__init__(
            authentication_model="pass",
            user_model=None
        )
        self.db = db
        self.templater = FastJ2(error_method=self.renderer_error, cwd=Path(__file__).parent)
        self.include_router(self.admin_routes)
        self.include_router(self.json_routes)

    @cached_property
    def json_routes(self):
        from .routers import JSON
        return JSON(self)

    @cached_property
    def admin_routes(self):
        from .routers import Admin
        return Admin(self)