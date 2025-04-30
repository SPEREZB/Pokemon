from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class IPokemonSprite:
    sprite: str
    back_default: Optional[str]
    official_artwork: Optional[str]
    front_shiny: Optional[str]
    front_default_gif: Optional[str]

@dataclass
class IPokemon:
    id: int
    name: str
    sprites: IPokemonSprite
    height: float
    weight: float
    types: List[str]
    abilities: List[str]
    stats: Dict[str, int]
    color: str
    habitat: str
    description: str
    moves: List[str]
