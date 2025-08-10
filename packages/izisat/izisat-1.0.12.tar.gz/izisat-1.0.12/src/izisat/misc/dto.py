from typing import Dict, Any, Optional, Literal
import numpy as np
from dataclasses import dataclass


@dataclass
class RasterBand:
    filepath: Optional[str] = None
    valid: bool = True
    array: np.ndarray = None
    profile: Optional[Dict[str, Any]] = None

@dataclass
class CompositeRaster:
    composition: Literal['rgb', 'ndvi', 'evi', 'cir', 'cloud']
    bands: dict[str, RasterBand]
    filepath: Optional[str] = None
    valid: bool = True