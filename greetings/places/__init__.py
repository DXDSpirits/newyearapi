
from greetings.models import Place

from .data import PLACE_DATA


def import_places():
    for province_data in PLACE_DATA['provinces']:
        province = Place.objects.create(category='province', name=province_data['name'])
        for city_data in province_data['cities']:
            city = Place.objects.create(category='city', name=city_data['name'], parent=province)
            for district_data in city_data['areas']:
                Place.objects.create(category='district', name=district_data['name'], parent=city)
