import pandas as pd
from dash import html
from geopy.geocoders import Nominatim
import numpy as np

geolocator = Nominatim(user_agent="maps")

def michelin_star_list(number: int) -> list:
    return [html.Img(src="assets/images/32px-MichelinStar.svg.png", style={'height':'18px','width':'18px'}) ] * number

def bib_gourmand() -> list:
    return [html.Img(src="assets/images/bib_gourmand.png", style={'height': '18px', 'width': '18px'})]

def euro(number: int) -> list:
    return [html.Img(src="assets/images/euro.svg", style={'height':'18px','width':'18px'}) ] * number

def map_styles() -> list:
    """Returns a list with the possible values for the map-style attribute in a plotly tile map"""
    return ["basic","carto-darkmatter","carto-darkmatter-nolabels","carto-positron","carto-positron-nolabels",
            "carto-voyager","carto-voyager-nolabels","dark","light","open-street-map","outdoors",
            "satellite","satellite-streets","streets"]

def zoom_from_location(location_string: str) -> float:
    """Returns the zoom needed for a plotly tile map figure, based on the location detected"""
    location = geolocator.geocode(location_string)
    height = np.abs(float(location.raw['boundingbox'][1]) - float(location.raw['boundingbox'][0]))
    width = np.abs(float(location.raw['boundingbox'][3]) - float(location.raw['boundingbox'][2]))
    area = height * width
    zoom = np.interp(x=area,
                     xp=[0, 5 ** -10, 4 ** -10, 3 ** -10, 2 ** -10, 1 ** -10, 1 ** -5],
                     fp=[20, 17, 16, 15, 14, 7, 5])
    return zoom

def apply_filters(df: pd.DataFrame, price: list, stars: list, cuisine: list, services: list) -> pd.DataFrame:
    """Applies the filters to the dataframe with the michelin stars data"""
    dff = df.loc[df.Price.isin(price)]
    dff = dff.loc[dff.Award.isin(stars)]
    if len(cuisine) > 0:
        mask_cuisine = dff.Cuisine.apply(lambda x: any(v in cuisine for v in x.split(', ')))
        dff = dff[mask_cuisine]
    if len(services) > 0:
        mask_services = dff.FacilitiesAndServices.apply(lambda x: any(v in services for v in x.split(', ')))
        dff = dff[mask_services]
    return dff


def size_mapping(award: str) -> int:
    """Returns different values depending on the award type that is given to the restaurante"""
    if award == '3 Stars':
        return 30
    elif award == '2 Stars':
        return 15
    elif award == '1 Star':
        return 10
    elif award == 'Bib Gourmand':
        return 5
    else:
        return 2

def load_data():
    """Loads the michelin stars database and performs the needed transformations"""
    df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/michelin_by_Jerry_Ng.csv")
    df.Cuisine = df.Cuisine.astype(str)
    df.FacilitiesAndServices = df.FacilitiesAndServices.astype(str)
    df['City'] = df['Location'].str.split(',', expand=True)[0]
    df['Price'] = df['Price'].str.len()
    df['award_size'] = df['Award'].apply(size_mapping)
    return df





if __name__ == '__main__':
    df = load_data()
    dff = apply_filters(df, [1,2], [2,3],[],[])