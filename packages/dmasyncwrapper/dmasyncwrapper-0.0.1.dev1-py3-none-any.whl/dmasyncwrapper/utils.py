# -*- coding: UTF-8 -*-
import abc
import dataclasses
import functools
import inspect

from dmasyncwrapper import Pool, consts

_NAMED_POOL_DICT: dict[str, Pool] = dict()


async def init(
        *, pool_name: str, host: str, port: int, user: str, password: str,
        auto_commit: bool,
        local_code: consts.LocalCode = consts.LocalCode.PG_UTF8,
        min_size: int, max_size: int) -> None:
    pool = Pool(
        host=host, port=port, user=user, password=password,
        auto_commit=auto_commit, local_code=local_code,
        min_size=min_size, max_size=max_size)
    await pool.init()
    _NAMED_POOL_DICT[pool_name] = pool


async def close(*, pool_name: str) -> None:
    if pool_name not in _NAMED_POOL_DICT:
        raise ValueError(f'Pool with name {pool_name} does not exist')
    pool = _NAMED_POOL_DICT[pool_name]
    await pool.close()
    del _NAMED_POOL_DICT[pool_name]


async def close_all() -> None:
    for _, pool in _NAMED_POOL_DICT.items():
        await pool.close()
    _NAMED_POOL_DICT.clear()


def with_dm(*, name: str, transaction: bool = True):

    def wrapper(func):
        argspec = inspect.getfullargspec(func)
        if all(map(lambda x: 'cursor' not in x,
                   (argspec.args, argspec.kwonlyargs))):
            raise SyntaxError('`cursor` is a required argument')

        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            if name not in _NAMED_POOL_DICT:
                raise SyntaxError(f'Pool "{name}" not found')
            if 'cursor' in kwargs:
                raise SyntaxError('`cursor` is a reserved argument')
            async with _NAMED_POOL_DICT[name].acquire() as conn:
                async with conn.cursor() as cursor:
                    kwargs['cursor'] = cursor
                    result = await func(*args, **kwargs)
                    if transaction:
                        # TODO
                        pass
                    await conn.commit()
            return result

        return wrapped

    return wrapper


class SQLHelper:

    def __init__(self, base_model: type | None = None):
        try:
            assert dataclasses.is_dataclass(base_model) or base_model is None
        except AssertionError:
            raise SyntaxError(
                f'Base model "{base_model}" should be a dataclass or None')
        self._base_model = base_model

    def _gen_fields(self, dataclass: type) -> tuple[list[str], list[str]]:
        if issubclass(dataclass, self._base_model):
            default_fields = [
                i.strip('_')
                for i in inspect.get_annotations(self._base_model).keys()]
        else:
            default_fields = list()
        custom_fields = [
            i.strip('_') for i in inspect.get_annotations(dataclass).keys()]
        return default_fields, custom_fields

    def gen_select_base(self, *, dataclass: type, table_name: str) -> str:
        default_fields, custom_fields = self._gen_fields(dataclass)
        return (f'SELECT {", ".join(default_fields + custom_fields)} '
                f'FROM {table_name}')

    def gen_get(self, *, dataclass: type, table_name: str) -> str:
        default_fields, custom_fields = self._gen_fields(dataclass)
        return (
            f'SELECT {", ".join(default_fields + custom_fields)} '
            f'FROM {table_name} WHERE id=%s')

    def gen_insert(self, *, dataclass: type, table_name: str) -> str:
        _, custom_fields = self._gen_fields(dataclass)
        return (
            f'INSERT INTO {table_name} ({", ".join(custom_fields)}) '
            f'VALUES ({", ".join(["%s"] * len(custom_fields))})')

    def gen_insert_returning(
            self, *, dataclass: type, table_name: str) -> str:
        default_fields, custom_fields = self._gen_fields(dataclass)
        return (
            f'INSERT INTO {table_name} ({", ".join(custom_fields)}) '
            f'VALUES ({", ".join(["%s"] * len(custom_fields))}) '
            f'RETURNING {", ".join(default_fields + custom_fields)}')

    def gen_remove(self, *, table_name: str) -> str:
        return (
            f'UPDATE {table_name} SET removed=%s, updated_at=NOW() '
            f'WHERE id=%s AND removed=%s')


@dataclasses.dataclass(slots=True, kw_only=True)
class BaseInsertModel(metaclass=abc.ABCMeta):

    @property
    @abc.abstractmethod
    def as_sql_params(self) -> tuple:
        ...
