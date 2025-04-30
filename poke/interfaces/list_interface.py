import string
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class IPagination:
    current_page: int
    has_next: bool
    has_previous: bool
    next_page: int | None
    previous_page: int | None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'current_page': self.current_page,
            'has_next': self.has_next,
            'has_previous': self.has_previous,
            'next_page': self.next_page,
            'previous_page': self.previous_page
        }


@dataclass
class IPokemonList:
    pokemon_list: list
    search_query: str
    pagination: IPagination

    def to_context_dict(self) -> Dict[str, Any]:
        return {
            'pokemon_list': self.pokemon_list,
            'search_query': self.search_query,
            'pagination': self.pagination.to_dict()
        }
