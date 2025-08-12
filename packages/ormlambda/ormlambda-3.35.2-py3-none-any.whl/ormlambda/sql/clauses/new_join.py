from __future__ import annotations
from collections import defaultdict
from typing import override, Optional, TYPE_CHECKING, Type


from ormlambda.util.module_tree.dfs_traversal import DFSTraversal
from ormlambda.common.interfaces.IQueryCommand import IQuery
from ormlambda import JoinType
from ormlambda.sql.clause_info import ClauseInfo
from ormlambda.sql.comparer import Comparer
from ormlambda.sql.elements import ClauseElement


# TODOL [x]: Try to import Table module without circular import Error
if TYPE_CHECKING:
    from ormlambda.dialects import Dialect


class Join(ClauseElement):
    __visit_name__ = "join"
    __slots__: tuple = (
        "comparer",
        "alias",
        "from_clause",
        "left_clause",
        "right_clause",
        "by",
        "_dialect",
    )

    DEFAULT_TABLE: str = "{table}"

    @override
    def __repr__(self) -> str:
        return f"{IQuery.__name__}: {self.query(self._dialect)}"

    def __init__(
        self,
        comparer: Comparer,
        right_alias: Optional[str] = DEFAULT_TABLE,
        left_alias: Optional[str] = DEFAULT_TABLE,
        by: JoinType = JoinType.LEFT_EXCLUSIVE,
        *,
        dialect: Dialect,
        **kw,
    ) -> None:
        self.comparer = comparer
        self._dialect = dialect
        self.by = by

        # COMMENT: When multiple columns reference the same table, we need to create an alias to maintain clear references.
        self.alias: Optional[str] = right_alias
        self.left_clause: ClauseInfo = comparer.left_condition(dialect)
        self.left_clause.alias_table = left_alias if left_alias is not None else self.DEFAULT_TABLE

        self.right_clause: ClauseInfo = comparer.right_condition(dialect)
        self.right_clause.alias_table = right_alias if right_alias is not None else self.DEFAULT_TABLE
        self.from_clause = ClauseInfo(self.right_clause.table, None, alias_table=self.alias, dialect=dialect)

    def __eq__(self, __value: Join) -> bool:
        return isinstance(__value, Join) and self.__hash__() == __value.__hash__()

    def __hash__(self) -> int:
        return hash(
            (
                self.by,
                self.left_clause.query(self._dialect),
                self.right_clause.query(self._dialect),
                self.from_clause.query(self._dialect),
            )
        )

    @classmethod
    def join_selectors(cls, dialect: Dialect, *args: Join) -> str:
        return "\n".join([x.query(dialect) for x in args])

    def query(self, dialect: Dialect) -> str:
        list_ = [
            self.by.value,  # inner join
            self.from_clause.query(dialect),
            "ON",
            self.left_clause.query(dialect),
            "=",
            self.right_clause.query(dialect),
        ]
        return " ".join([x for x in list_ if x is not None])

    @classmethod
    def sort_join_selectors(cls, joins: set[Join]) -> tuple[Join]:
        # FIXME [x]: How to sort when needed because it's not necessary at this point. It is for testing purpouse
        if len(joins) == 1:
            return tuple(joins)

        # create graph and sort it using 'Depth First Search' algorithm
        graph: dict[str, list[str]] = defaultdict(list)
        for join in joins:
            graph[join.left_clause.alias_table].append(join.right_clause.alias_table)

        sorted_graph = DFSTraversal.sort(graph)[::-1]

        if not sorted_graph:
            return tuple(joins)

        # Mapped Join class using his unique alias
        join_object_map: dict[str, Join] = {}
        for obj in joins:
            join_object_map[obj.alias] = obj

        res = []
        for table in sorted_graph:
            tables = join_object_map.get(table, None)

            if not tables:
                continue
            res.append(tables)
        return res


__all__ = ["Join"]
