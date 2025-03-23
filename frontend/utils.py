

def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)


def get_city_radìus(city_name):
    import geonamescache

    gc = geonamescache.GeonamesCache()

    cities = gc.search_cities(city_name, case_sensitive=False, contains_search=False)
    population = 0
    for city in cities:
        if city['population'] > population:
            population = city['population']
    radius = 2000
    if population > 2000000:
        radius = 15000
    elif population > 1000000:
        radius = 10000
    elif population > 500000:
        radius = 7000
    elif population > 150000:
        radius = 5000
    elif population > 25000:
        radius = 4000

    return radius


if __name__ == '__main__':
    print(rgb_to_hex(255, 0, 0))