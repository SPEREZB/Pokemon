from typing import Optional

from poke.interfaces.list_interface import IPagination, IPokemonList
from poke.interfaces.detail_interface import IPokemon, IPokemonSprite


def parse_api_response_to_pokemon(data: dict, species_data: Optional[dict] = None) -> IPokemon:
    sprites = IPokemonSprite(
        sprite=data['sprites']['front_default'],
        back_default=data['sprites'].get('back_default'),
        official_artwork=data['sprites']['other'].get('official-artwork', {}).get('front_default'),
        front_shiny=data['sprites'].get('front_shiny'),
        front_default_gif=data['sprites']['other']['showdown'].get('front_default')
    )

    description = 'No description available'
    color = 'unknown'
    habitat = 'unknown'

    if species_data:
        description = next(
            (entry['flavor_text'] for entry in species_data.get('flavor_text_entries', [])
             if entry['language']['name'] == 'en'),
            description
        )
        color = species_data.get('color', {}).get('name', color)
        habitat = species_data.get('habitat', {}).get('name', habitat)

    return IPokemon(
        id=data['id'],
        name=data['name'].capitalize(),
        sprites=sprites,
        height=data['height'] / 10,
        weight=data['weight'] / 10,
        types=[t['type']['name'] for t in data['types']],
        abilities=[a['ability']['name'] for a in data['abilities']],
        stats={s['stat']['name']: s['base_stat'] for s in data['stats']},
        color=color,
        habitat=habitat,
        description=description,
        moves=[m['move']['name'] for m in data['moves'][:10]]
    )

def parse_api_response_to_pokemon_list(data: dict, request) -> IPokemonList:
    pagination = IPagination(
        current_page= int(request.GET.get('page', 1)),
        has_next= data['next'] is not None,
        has_previous= data['previous'] is not None,
        next_page= int(request.GET.get('page', 1)) + 1 if data['next'] else None,
        previous_page= int(request.GET.get('page', 1)) - 1 if data['previous'] else None
    )

    pokemon_list= IPokemonList(
        pokemon_list=data['results'],
        search_query= request.GET.get('search', ''),
        pagination=pagination
    )
    return pokemon_list.to_context_dict()