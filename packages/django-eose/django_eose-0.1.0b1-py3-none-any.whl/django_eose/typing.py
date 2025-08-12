from typing import Callable, Sequence, Iterable

SearchFields = Sequence[str]
ItemIterator = Iterable
Processor = Callable[[object], int | None]
