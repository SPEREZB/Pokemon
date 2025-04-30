from django.shortcuts import render

# Create your views here.
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
import concurrent.futures

from .constants import POKE_API
from .interfaces.detail_interface import IPokemon
from .utils.parseJson import parse_api_response_to_pokemon, parse_api_response_to_pokemon_list


class PokemonListView(APIView):

    def get(self, request):
        search = request.GET.get('search', '').lower()[:25]
        page = int(request.GET.get('page', 1))

        cache_key = f"pokemon_list_{search}_{page}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        all_pokemon = cache.get('full_pokemon_list')
        if not all_pokemon:
            response = requests.get(f"{POKE_API}?limit=1000", timeout=10)
            if response.status_code != 200:
                return Response({"error": "No se pudo obtener la lista de Pokémon"}, status=503)
            all_pokemon = response.json()['results']
            cache.set('full_pokemon_list', all_pokemon, 86400)

        filtered = [
            p for p in all_pokemon
            if search in p['name'].lower()
        ] if search else all_pokemon

        page_size = 10
        start = (page - 1) * page_size
        paginated = filtered[start:start + page_size]

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(self._get_basic_details, paginated))

        response_data = {
            'count': len(filtered),
            'results': [r for r in results if r],
            'next': page + 1 if len(filtered) > start + page_size else None,
            'previous': page - 1 if page > 1 else None
        }

        cache.set(cache_key, response_data, 3600)
        return Response(response_data)

    def _get_basic_details(self, pokemon):
        """Obtiene solo los datos necesarios para la lista"""
        try:
            pokemon_id = int(pokemon['url'].split('/')[-2])
            details = cache.get(f'pokemon_basic_{pokemon_id}')
            if not details:
                response = requests.get(pokemon['url'], timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    details = {
                        'name': data['name'].capitalize(),
                        'pokemon_id': data['id'],
                        'sprite_url': data['sprites']['other']['showdown']['front_default'],
                        'abilities_count': len(data['abilities']),
                        'details_url': pokemon['url']
                    }
                    cache.set(f'pokemon_basic_{pokemon_id}', details, 86400)
            return details
        except:
            return None

    def pokemon_list_html_view(request):
        api_view = PokemonListView.as_view()
        api_response = api_view(request)

        if api_response.status_code != 200:
            return render(request, 'pokemon/error.html', {
                'error': api_response.data.get('error', 'Error desconocido')
            }, status=api_response.status_code)

        data = api_response.data

        context= parse_api_response_to_pokemon_list(data,request)

        return render(request, 'poke_temp/list.html', context)


class PokemonDetailView(APIView):
    def get(self, request, pokemon_id):
        cache_key = f"pokemon_full_{pokemon_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        url = f"{POKE_API}{'/'}{pokemon_id}"
        response = requests.get(url)

        if response.status_code != 200:
            return Response({"error": "Pokémon no encontrado"}, status=404)

        data = response.json()

        species_cache_key = f"pokemon_species_{pokemon_id}"
        species_data = cache.get(species_cache_key)
        if not species_data:
            species_response = requests.get(data['species']['url'])
            if species_response.status_code == 200:
                species_data = species_response.json()
                cache.set(species_cache_key, species_data, 86400)

        pokemon_obj: IPokemon = parse_api_response_to_pokemon(data, species_data)
        cache.set(cache_key, pokemon_obj, 86400)
        return Response(pokemon_obj.__dict__)

    def pokemon_detail_html_view(request, pokemon_id):
        api_view = PokemonDetailView.as_view()
        api_response = api_view(request, pokemon_id=pokemon_id)

        if api_response.status_code != 200:
            return render(request, 'pokemon/error.html', {
                'error': api_response.data.get('error', 'Pokémon no encontrado')
            }, status=api_response.status_code)

        pokemon = api_response.data

        return render(request, 'poke_temp/detail.html', {
            'pokemon': pokemon
        })
