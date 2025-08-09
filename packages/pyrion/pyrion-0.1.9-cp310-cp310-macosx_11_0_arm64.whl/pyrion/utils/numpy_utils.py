from typing import List

import numpy as np


def _vstack_safe(arrays: List[np.ndarray]) -> np.ndarray:
    non_empty = [a for a in arrays if a.size > 0]
    return np.vstack(non_empty) if non_empty else np.empty((0, 2), dtype=int)
