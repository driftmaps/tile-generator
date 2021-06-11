from dotenv import load_dotenv
from src.tile_generator import TileGenerator
from src.city_geocoder import Geocoder

import click
import os

load_dotenv()

"""
TODO:
- Add arguments for filename & outpath, etc
- Add command for geocoding
- Add help

"""

@click.group()
def main():
    pass

@click.command()
@click.option("--region", type=click.Choice(['us', 'can']), required=True, help="Region to geocode.")
@click.option("--top-n", default=10, help="Number of cities to geocode.")
@click.option("--zlow", default=5, help="Lower bound of zoom.")
@click.option("--zhigh", default=15, help="Upper bound of zoom.")
@click.option("--datapath", default='data/cities/', help="Folder from which to read and write data.")
def gentiletree(region, top_n, zlow, zhigh, datapath):
    click.echo(f'Launching geocoder for region "{region}", with top {top_n} cities and zoom range {zlow}-{zhigh}.')
    API_KEY = os.environ.get("GOOGLE_MAPS_KEY")
    filename = f'{datapath}{region}cities.csv'
    outpath = f'{datapath}{region}_tile_tree.json'
    gc = Geocoder(API_KEY, region, filename, zlow, zhigh, top_n, outpath)
    gc.geocode()

@click.command()
@click.option("--city_key", default="atlanta", help="City to generated tiles for.")
def gentiles(city_key):
    click.echo(f'Launching tilegenerator for city key "{city_key}."')
    OMT = os.environ.get("OMT_URL")
    city_name = "Atlanta, Fulton County, Georgia, United States"
    filename = str(os.environ.get("DATA_PATH_CITY")) + "us_tile_tree.json"
    outpath = "data/tiles/"
    tg = TileGenerator(OMT,city_key,city_name,filename,outpath)
    tg.generate_tiles()

main.add_command(gentiletree)
main.add_command(gentiles)

if __name__ == '__main__':
    main()
