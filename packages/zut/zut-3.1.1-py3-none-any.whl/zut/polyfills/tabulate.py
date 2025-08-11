from __future__ import annotations

from typing import TYPE_CHECKING, Mapping

if TYPE_CHECKING:
    from typing import Literal, Sequence, Iterable

try:
    from tabulate import tabulate  # type: ignore

except ModuleNotFoundError:
    def tabulate(tabular_data: Iterable[Iterable|Mapping], headers: Sequence[str]|Literal['keys']|None = None):
        if headers:
            if headers == 'keys':
                first_row = next(iter(tabular_data), None)
                if not isinstance(first_row, Mapping):
                    raise ValueError(f"First row must be a dict, got {type(first_row).__name__}")
                headers = [key for key in first_row]
            result = '\t'.join(str(header) for header in headers)
            result += '\n' + '\t'.join('-' * len(header) for header in headers)
        else:
            result = ''

        for row in tabular_data:
            if isinstance(row, Mapping):
                if not headers:
                    raise ValueError("Cannot use dict rows without headers. Specify headers='keys' to use keys of the first dict as headers.")
                row = {header: row.get(header) for header in headers}
            result += ('\n' if result else '') + '\t'.join(str(value) for value in row)

        return result

__all__ = ('tabulate',)
