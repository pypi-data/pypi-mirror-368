import hashlib
import json

from pancham.reporter import get_reporter
from .caching_database_search import DatabaseSearch, FilteredCachingDatabaseSearch, CachingDatabaseSearch, \
    SQLFileCachingDatabaseSearch
from .populating_database_search import PopulatingDatabaseSearch

__managed_db_cache: dict[str, DatabaseSearch] = {}

def get_database_search(
        table_name: str,
        search_col: str,
        value_col: str,
        filter: dict[str, str]|None = None,
        cast_search: None | str = None,
        cast_value: None | str = None,
        populate: bool = False,
        sql_file: str|None = None,
) -> DatabaseSearch:
    """
    Retrieve a cached instance of `CachingDatabaseSearch` for querying a database table.

    This function manages caching for database search operations. Each unique combination
    of table name, search column, value column, search column casting, and value column
    casting corresponds to a unique cache key. If no matching instance exists in the cache,
    a new `CachingDatabaseSearch` instance is created, stored in the cache, and returned.

    :param filter: Filters to be added to the query
    :param table_name: The name of the database table to query.
    :param search_col: The column name in the database table used for search criteria.
    :param value_col: The column name in the database table from which values will be retrieved.
    :param cast_search: Optional SQL type casting for the search column.
    :param cast_value: Optional SQL type casting for the value column.
    :return: A cached or newly instantiated `CachingDatabaseSearch` object.
    :rtype: CachingDatabaseSearch
    """
    global __managed_db_cache

    reporter = get_reporter()
    reporter.report_debug(f'Database search cache {__managed_db_cache}')
    reporter.report_debug(f'Database search using populate - {populate}, filter - {filter}, Sql file - {sql_file}')

    filter_key = ''
    if filter is not None:
        filter_key = json.dumps(filter, sort_keys=True)

    db_key_str = f"{table_name}_{search_col}_{value_col}_{cast_search}_{cast_value}_{populate}_{filter_key}_{sql_file}"
    db_key = hashlib.md5(db_key_str.encode()).hexdigest()

    if db_key not in __managed_db_cache:
        if populate:
            __managed_db_cache[db_key] = PopulatingDatabaseSearch(table_name, search_col, value_col, cast_search, cast_value)
        elif filter is not None:
            __managed_db_cache[db_key] = FilteredCachingDatabaseSearch(table_name, search_col, value_col, filter, cast_search, cast_value)
        elif sql_file is not None:
            __managed_db_cache[db_key] = SQLFileCachingDatabaseSearch(sql_file, cast_search, cast_value)
        else:
            __managed_db_cache[db_key] = CachingDatabaseSearch(table_name, search_col, value_col, cast_search, cast_value)

    return __managed_db_cache[db_key]
