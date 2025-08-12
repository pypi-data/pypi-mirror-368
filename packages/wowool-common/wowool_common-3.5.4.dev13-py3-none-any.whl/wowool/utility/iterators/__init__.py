from typing import Iterator, Tuple, Any, List


def iterate_prv_nxt(my_list: List[Any]) -> Iterator[Tuple[int, Any, Any, Any]]:
    """Create an iterator that returns previous, current and next elements.

    Args:
        my_list: List to iterate over.

    Yields:
        Tuple of (index, previous_item, current_item, next_item).
    """
    prv, cur, nxt = None, iter(my_list), iter(my_list)
    next(nxt, None)
    idx = 0

    while True:
        try:
            if prv:
                yield idx, next(prv), next(cur), next(nxt, None)
            else:
                yield idx, None, next(cur), next(nxt, None)
                prv = iter(my_list)
            idx += 1
        except StopIteration:
            break


def iterate_nxt(my_list: List[Any]) -> Iterator[Tuple[int, Any, Any]]:
    """Create an iterator that returns current and next elements.

    Args:
        my_list: List to iterate over.

    Yields:
        Tuple of (index, current_item, next_item).
    """
    cur, nxt = iter(my_list), iter(my_list)
    next(nxt, None)
    idx = 0

    while True:
        try:
            yield idx, next(cur), next(nxt, None)
            idx += 1
        except StopIteration:
            break


def iterate_prv(my_list: List[Any]) -> Iterator[Tuple[int, Any, Any]]:
    """Create an iterator that returns previous and current elements.

    Args:
        my_list: List to iterate over.

    Yields:
        Tuple of (index, previous_item, current_item).
    """
    (
        prv,
        cur,
    ) = None, iter(my_list)

    idx = 0
    while True:
        try:
            if prv:
                yield idx, next(prv), next(cur)
            else:
                yield idx, None, next(cur)
                prv = iter(my_list)
            idx += 1
        except StopIteration:
            break
