# redaqt/theme/context.py
from dataclasses import dataclass
from typing import Dict

@dataclass
class ThemeContext:
    theme: str                     # current theme name
    colors: Dict[str,str]          # current palette
    all_palettes: Dict[str,Dict]