"""Password generation utilities for PDF cracking.

This module provides functions for generating password combinations
within specified length ranges and character sets.
"""

import itertools
from typing import Iterator


def generate_passwords(min_len: int, max_len: int, charset: str) -> Iterator[str]:
    """Generate passwords within a given length range and character set.

    Args:
        min_len: Minimum password length to generate.
        max_len: Maximum password length to generate.
        charset: String containing all characters to use in password generation.

    Yields:
        str: Generated password strings.

    Example:
        >>> list(generate_passwords(1, 2, "ab"))
        ['a', 'b', 'aa', 'ab', 'ba', 'bb']
    """
    return (
        "".join(p_tuple)
        for length in range(min_len, max_len + 1)
        for p_tuple in itertools.product(charset, repeat=length)
    )
