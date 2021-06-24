from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

import csv
import geocoder
import json
import mercantile
import os
import pickle

"""
TODO

- Add city_key to output
- Dynamic filepaths from CLI

"""

class Geocoder():
    def __init__(self, API_KEY:str, region:str, file:str, z_low:int, z_high:int, top_n:int, outpath:str) -> None:
        self.API_KEY = API_KEY
        self.region = region
        self.file = file
        self.rng = range(z_low, z_high)
        self.top_n = top_n
        self.outpath = outpath

    def geocode(self) -> None:
        queries = self._read_data()
        self._process_queries(queries)
        tile_tree = self._iter_tiles()
        json.dump(tile_tree, open(f'{self.outpath}', 'w'))

    def _read_data(self) -> list:
        queries = []
        with open(f'{self.file}', newline='') as f:
            reader = csv.DictReader(f, delimiter=',')
            for i,row in enumerate(reader):
                if self.region == 'us':
                    city = row['city']
                    state = row['state_name']
                    county = row['county_name']
                    queries.append(f'{city}, {county} County, {state}, United States')
                elif self.region == 'can':
                    city = row['city']
                    province = row['province_name']
                    queries.append(f'{city}, {province}, Canada')
                if(i >= self.top_n):
                    break
        return queries

    def _process_queries(self, queries:list) -> None:
        self.city_tile_pairs = {}
        futures = []
        with ThreadPoolExecutor(max_workers=15) as executor:
            for q in queries:
                future = executor.submit(self._geocode, q)
                futures.append(future)

            for future in futures:
                try:
                    print(future.result())
                except Exception as e:
                    print(e)

    def _geocode(self, q:list) -> str:
        g = geocoder.google(f'metropolitan, {q}', key = self.API_KEY)
        self.city_tile_pairs[q] = self._tiles_from_bbox(g)
        msg = f"Finished geocoding city: {q}"
        return msg

    def _tiles_from_bbox(self, g:dict) -> list:
        wsen = [g.json['bbox']['southwest'][1],
                g.json['bbox']['southwest'][0],
                g.json['bbox']['northeast'][1],
                g.json['bbox']['northeast'][0]]
        tiles = mercantile.tiles(wsen[0],
                                 wsen[1],
                                 wsen[2],
                                 wsen[3],
                                 self.rng)
        return tiles

    def _iter_tiles(self) -> dict:
        tile_tree = {}
        for k in self.city_tile_pairs.keys():
            tiles = self.city_tile_pairs[k]
            tile_tree[k] = {}
            for tile in tiles:
                if tile.z not in tile_tree[k]:
                    tile_tree[k][tile.z] = list()
                    tile_tree[k][tile.z].append((tile.x, tile.y))
                else:
                    tile_tree[k][tile.z].append((tile.x, tile.y))
        return tile_tree
