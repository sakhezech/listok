import dataclasses
import datetime
import os
import sqlite3
import typing
from sqlite3 import Connection
from types import NoneType
from typing import Annotated, Any, ClassVar, TypeGuard

type_to_sqlite_type: dict[Any, str] = {
    NoneType: 'NULL',
    int: 'INTEGER',
    float: 'REAL',
    str: 'TEXT',
    bytes: 'BLOB',
}


def _datetime_converter(data: bytes) -> datetime.datetime:
    return datetime.datetime.fromisoformat(data.decode())


type_to_sqlite_type[datetime.datetime] = 'DATETIME'
sqlite3.register_converter('DATETIME', _datetime_converter)
sqlite3.register_adapter(datetime.datetime, datetime.datetime.isoformat)


def _is_annotated(val: Any) -> TypeGuard[type[Annotated]]:
    return typing.get_origin(val) is Annotated


class _Meta(type):
    __table_name__: ClassVar[str | None] = None

    def __str__(self) -> str:
        return self.__table_name__ or self.__name__.lower()


@typing.dataclass_transform(kw_only_default=True)
@dataclasses.dataclass
class _Table(metaclass=_Meta):
    def __init_subclass__(cls) -> None:
        dataclasses.dataclass(kw_only=True)(cls)
        fields = dataclasses.fields(cls)
        for field in fields:
            setattr(cls, field.name, f'{cls}.{field.name}')


class Model(_Table):
    @classmethod
    def __init_table__(cls, conn: Connection) -> None:
        fields = dataclasses.fields(cls)
        key = fields[0]
        # TODO: support some Annotated magic
        sql = f""" CREATE TABLE {cls}(
                 {key.name} {type_to_sqlite_type[key.type]}
                 PRIMARY KEY
              """
        if len(fields) > 1:
            columns = [
                f'{field.name} {type_to_sqlite_type[field.type]} NOT NULL'
                for field in fields[1:]
            ]
            sql += f',{','.join(columns)}'
        sql += ');'
        with conn:
            conn.execute(sql)

    def save(self, conn: Connection) -> None:
        fields = dataclasses.fields(self)
        key = fields[0]
        if len(fields) == 1:
            with conn:
                conn.execute(
                    f""" INSERT OR IGNORE INTO {self.__class__}
                         VALUES (:{key.name});
                    """,
                    self.__dict__,
                )
        else:
            con_name_list = ', '.join(field.name for field in fields[1:])
            param_list = ', '.join(f':{field.name}' for field in fields[1:])
            # TODO: if key is None insert without key
            with conn:
                res = conn.execute(
                    f""" INSERT INTO {self.__class__}
                             ({key.name}, {con_name_list})
                         VALUES (:{key.name}, {param_list})
                         ON CONFLICT ({key.name})
                         DO UPDATE SET ({con_name_list}) = ({param_list})
                         RETURNING {key.name};
                    """,
                    self.__dict__,
                ).fetchone()[0]
            setattr(self, key.name, res)


class Junction(_Table):
    @classmethod
    def __init_table__(cls, conn: Connection) -> None:
        fields = dataclasses.fields(cls)
        if len(fields) != 2:
            raise ValueError

        field_first = fields[0]
        field_second = fields[1]

        if not _is_annotated(field_first.type) or not _is_annotated(
            field_second.type
        ):
            raise ValueError

        TableFirst = field_first.type.__metadata__[0]
        TableSecond = field_second.type.__metadata__[0]
        key_first = dataclasses.fields(TableFirst)[0]
        key_second = dataclasses.fields(TableSecond)[0]

        with conn:
            conn.execute(
                f""" CREATE TABLE {cls}(
                     {field_first.name}
                         {type_to_sqlite_type[key_first.type]},
                     {field_second.name}
                         {type_to_sqlite_type[key_second.type]},
                     UNIQUE({field_first.name}, {field_second.name}),
                     FOREIGN KEY({field_first.name})
                         REFERENCES {TableFirst}({key_first.name})
                         ON DELETE CASCADE,
                     FOREIGN KEY({field_second.name})
                         REFERENCES {TableSecond}({key_second.name})
                         ON DELETE CASCADE
                );
                """
            )

    def save(self, conn: Connection) -> None:
        fields = dataclasses.fields(self)
        field_first = fields[0]
        field_second = fields[1]
        with conn:
            conn.execute(
                f""" INSERT OR IGNORE INTO {self.__class__}
                        ({field_first.name}, {field_second.name})
                     VALUES (:{field_first.name}, :{field_second.name});
                """,
                self.__dict__,
            )


type StrPath = str | os.PathLike[str]


def create_connection(db_path: StrPath) -> Connection:
    SHOULD_INIT_DB = not os.path.exists(db_path)
    detect_options = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES

    conn = sqlite3.connect(db_path, detect_types=detect_options)
    conn.execute('PRAGMA foreign_keys = ON;')
    conn.row_factory = sqlite3.Row

    if SHOULD_INIT_DB:
        init_tables(conn)

    return conn


def init_tables(conn: Connection) -> None:
    for table in Model.__subclasses__() + Junction.__subclasses__():
        table.__init_table__(conn)
