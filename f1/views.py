from django.shortcuts import render

import requests
from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime
from django.http import HttpResponse

# Funzione per ottenere la prossima gara
def get_next_race(request):
    try:
        url = 'https://api.jolpi.ca/ergast/f1/current/next.json'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Controllo se ci sono gare disponibili
        races = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
        if not races:
            return HttpResponse('<h1>Nessuna gara disponibile</h1>', status=404)

        race = races[0]

        # Preparazione dati
        race_date = (
            datetime.fromisoformat(f"{race['date']}T{race['time']}".replace("Z", ""))  # Rimuove Z
            .strftime('%A %d %B %Y %H:%M')
            if 'date' in race and 'time' in race
            else 'Data non disponibile'
        )

        qual_date = (
            datetime.fromisoformat(f"{race['Qualifying']['date']}T{race['Qualifying']['time']}".replace("Z", ""))
            .strftime('%A %d %B %Y %H:%M')
            if 'Qualifying' in race and 'date' in race['Qualifying'] and 'time' in race['Qualifying']
            else 'Orario non disponibile'
        )

        circuit = race.get('Circuit', {})
        latitude = circuit.get('Location', {}).get('lat', 'Non disponibile')
        longitude = circuit.get('Location', {}).get('long', 'Non disponibile')
        country = circuit.get('Location', {}).get('country', 'Non disponibile')
        circuit_name = circuit.get('circuitName', 'Nome circuito non disponibile')

        # Mapping manuale per ottenere l'immagine del circuito
        circuit_images = {
            'Albert Park Grand Prix Circuit': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Albert_Park_Circuit_2021.svg/800px-Albert_Park_Circuit_2021.svg.png',
            'Bahrain International Circuit': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Bahrain_International_Circuit--Grand_Prix_Layout.svg/1024px-Bahrain_International_Circuit--Grand_Prix_Layout.svg.png',
            'Circuit de Barcelona-Catalunya': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Circuit_de_Catalunya_moto_2021.svg/1920px-Circuit_de_Catalunya_moto_2021.svg.png',
            'Circuit de Monaco': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Monte_Carlo_Formula_1_track_map.svg/1920px-Monte_Carlo_Formula_1_track_map.svg.png',
            'Circuit Gilles Villeneuve': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Circuit_Gilles_Villeneuve.svg/1920px-Circuit_Gilles_Villeneuve.svg.png',
            'Circuit of the Americas': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Austin_circuit.svg/1920px-Austin_circuit.svg.png',
            'Hungaroring': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Hungaroring.svg/1920px-Hungaroring.svg.png',
            'Imola Circuit': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Imola_2009.svg/2560px-Imola_2009.svg.png',
            'Interlagos': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Aut%C3%B3dromo_Jos%C3%A9_Carlos_Pace_%28AKA_Interlagos%29_track_map.svg/2560px-Aut%C3%B3dromo_Jos%C3%A9_Carlos_Pace_%28AKA_Interlagos%29_track_map.svg.png',
            'Jeddah Street Circuit': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Jeddah_Street_Circuit_2021.svg/1920px-Jeddah_Street_Circuit_2021.svg.png',
            'Marina Bay Street Circuit': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Marina_Bay_circuit_2023.svg/1920px-Marina_Bay_circuit_2023.svg.png',
            'Miami International Autodrome': 'https://example.com/miami.jpg',
            'Monza Circuit': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Monza_Map-2021.png/1920px-Monza_Map-2021.png',
            'Red Bull Ring': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Circuit_Red_Bull_Ring.svg/1920px-Circuit_Red_Bull_Ring.svg.png',
            'Shanghai International Circuit': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Shanghai_International_Racing_Circuit_track_map.svg/1920px-Shanghai_International_Racing_Circuit_track_map.svg.png',
            'Silverstone Circuit': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Circuit_Silverstone_2011.svg/1920px-Circuit_Silverstone_2011.svg.png',
            'Sochi Autodrom': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Circuit_Sochi.svg/1920px-Circuit_Sochi.svg.png',
            'Spa-Francorchamps': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Spa-Francorchamps_of_Belgium.svg/1920px-Spa-Francorchamps_of_Belgium.svg.png',
            'Suzuka Circuit': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Suzuka_circuit_map--2005.svg/1920px-Suzuka_circuit_map--2005.svg.png',
            'Yas Marina Circuit': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Yas_Marina_Circuit.png/1920px-Yas_Marina_Circuit.png',
            # Aggiungere altri circuiti se necessario
        }
        flag_images = {
            'Australia': 'https://flagcdn.com/au.svg',
            'Bahrain': 'https://flagcdn.com/bh.svg',
            'China': 'https://flagcdn.com/cn.svg',
            'Europe': 'https://flagcdn.com/eu.svg',  # Europe is a continent, not a country
            'France': 'https://flagcdn.com/fr.svg',
            'Germany': 'https://flagcdn.com/de.svg',
            'Hungary': 'https://flagcdn.com/hu.svg',
            'Italy': 'https://flagcdn.com/it.svg',
            'Japan': 'https://flagcdn.com/jp.svg',
            'Malaysia': 'https://flagcdn.com/my.svg',
            'Mexico': 'https://flagcdn.com/mx.svg',
            'Monaco': 'https://flagcdn.com/mc.svg',
            'Netherlands': 'https://flagcdn.com/nl.svg',
            'Saudi Arabia': 'https://flagcdn.com/sa.svg',
            'Singapore': 'https://flagcdn.com/sg.svg',
            'South Africa': 'https://flagcdn.com/za.svg',
            'South Korea': 'https://flagcdn.com/kr.svg',
            'Spain': 'https://flagcdn.com/es.svg',
            'United Arab Emirates': 'https://flagcdn.com/ae.svg',
            'United States': 'https://flagcdn.com/us.svg',
            'United Kingdom': 'https://flagcdn.com/gb.svg',
            'Canada': 'https://flagcdn.com/ca.svg',
            'Austria': 'https://flagcdn.com/at.svg',
            'Brazil': 'https://flagcdn.com/br.svg',
            'Portugal': 'https://flagcdn.com/pt.svg',
            'Russia': 'https://flagcdn.com/ru.svg',
            'Turkey': 'https://flagcdn.com/tr.svg',
            'Vietnam': 'https://flagcdn.com/vn.svg'
        }


        circuit_image_url = circuit_images.get(circuit_name, 'https://link-a-default-image.com/default.jpg')
        flag_image = flag_images.get(country, 'https://example.com/flags/default_flag.png')

        context = {
            'race_name': race.get('raceName', 'Gara non disponibile'),
            'race_date': race_date,
            'qual_date': qual_date,
            'latitude': latitude,
            'longitude': longitude,
            'country': country,
            'circuit_name': circuit_name,
            'circuit_image_url': circuit_image_url,
            'flag_image': flag_image,
        }

        return render(request, 'next_race.html', context)

    except requests.exceptions.RequestException as e:
        return HttpResponse(f"<h1>Errore API: {e}</h1>", status=500)

    except Exception as e:
        return HttpResponse(f"<h1>Errore interno: {e}</h1>", status=500)



def get_last_race_results(request):
    url = 'https://api.jolpi.ca/ergast/f1/current/last/results.json'
    response = requests.get(url)
    data = response.json()
    results = data['MRData']['RaceTable']['Races'][0]['Results'] if data['MRData']['RaceTable']['Races'] else []
    return render(request, 'last_race_results.html', {'results': results})

# Funzione per ottenere la classifica piloti
def get_driver_standings(request):
    url = 'https://api.jolpi.ca/ergast/f1/current/driverStandings.json'
    response = requests.get(url)
    data = response.json()
    standings = data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']

    driver_standings_with_teams = [
        {
            'position': standing['position'],
            'driver': standing['Driver'],
            'constructor': standing['Constructors'][0],
            'points': standing['points']
        }
        for standing in standings
    ]
    
    

    return render(request, 'driver_standings.html', {'driver_standings': driver_standings_with_teams})


# Funzione per ottenere la classifica costruttori
def get_constructor_standings(request):
    url = 'https://api.jolpi.ca/ergast/f1/current/constructorStandings.json'
    response = requests.get(url)
    data = response.json()
    standings = data['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']
    
    # Passa i dati della classifica dei costruttori al template
    return render(request, 'constructor_standings.html', {'constructor_standings': standings})

def get_constructor_info(request, constructor_id):
    url = f'https://api.jolpi.ca/ergast/f1/constructors/{constructor_id}.json'
    response = requests.get(url)
    data = response.json()
    constructor = data['MRData']['ConstructorTable']['Constructors'][0]
    return JsonResponse(constructor)

def get_driver_info(request, driver_id):
    url = f'https://api.jolpi.ca/ergast/f1/drivers/{driver_id}.json'
    response = requests.get(url)
    data = response.json()
    driver = data['MRData']['DriverTable']['Drivers'][0]
    return JsonResponse(driver)


# Function to get all drivers from the API for the 2024 season
def get_all_drivers(request):
    # Step 1: Fetch all drivers' information for the 2024 season
    url = 'https://api.jolpi.ca/ergast/f1/2025/drivers.json'
    response = requests.get(url)
    data = response.json()
    
    # Step 2: Get the list of drivers from the API response
    drivers = data['MRData']['DriverTable']['Drivers']

    # Step 3: Get stats for all drivers
    driver_stats = get_all_drivers_stats(drivers)

    # Step 4: Combine the driver data and stats
    for driver in drivers:
        driver_id = driver['driverId']
        # Add the stats to each driver object
        if driver_id in driver_stats:
            driver['stats'] = driver_stats[driver_id]
        else:
            driver['stats'] = {'wins': 0, 'podiums': 0, 'poles': 0, 'championships': 0}

    # Step 5: Sort drivers by wins in descending order
    drivers.sort(key=lambda x: x['stats']['wins'], reverse=True)

    # Step 6: Render the template and pass both drivers and stats
    return render(request, 'drivers_card.html', {'drivers': drivers})

# Function to get stats for all drivers (now accepts the list of drivers)
def get_all_drivers_stats(drivers):
    driver_stats = {}

    # Get stats for each driver based on driverId from the passed drivers
    for driver in drivers:
        driver_id = driver['driverId']
        driver_stats[driver_id] = get_driver_stats(driver_id)

    return driver_stats

# Function to get individual driver stats
def get_driver_stats(driver_id):
    wins = 0
    podiums = 0
    poles = 0
    championships = 0

    # Step 1: Get results for the 2024 season
    season = "2025"
    season_response = requests.get(f'https://api.jolpi.ca/ergast/f1/{season}/drivers/{driver_id}/results.json')
    season_data = season_response.json()
    races = season_data['MRData']['RaceTable']['Races']

    for race in races:
        # Ignore sprint races
        if 'sprint' in race['raceName'].lower():
            continue

        position = int(race['Results'][0]['position'])
        qualifying_position = int(race['Results'][0]['grid'])

        if position == 1:
            wins += 1
        if 1 <= position <= 3:
            podiums += 1
        if qualifying_position == 1:
            poles += 1

    # Step 2: Get standings for the 2024 season to check if the driver won the championship
    standings_response = requests.get(f'https://api.jolpi.ca/ergast/f1/{season}/drivers/{driver_id}/driverStandings.json')
    standings_data = standings_response.json()
    standings_list = standings_data['MRData']['StandingsTable']['StandingsLists']

    # Check if standings_list is non-empty and the expected position exists
    if standings_list:
        driver_standings = standings_list[0].get('DriverStandings', [])
        if driver_standings and driver_standings[0].get('position') == '1':
            championships += 1

    return {
        'wins': wins,
        'podiums': podiums,
        'poles': poles,
        'championships': championships
    }



# Function to get all constructors from the API for the 2024 season
def get_all_constructors(request):
    # Step 1: Fetch all constructors' information for the 2024 season
    url = 'https://api.jolpi.ca/ergast/f1/2025/constructors.json'
    response = requests.get(url)
    data = response.json()

    # Step 2: Get the list of constructors from the API response
    constructors = data['MRData']['ConstructorTable']['Constructors']

    # Step 3: Get stats for all constructors
    constructor_stats = get_all_constructors_stats(constructors)

    # Step 4: Combine the constructor data and stats
    for constructor in constructors:
        constructor_id = constructor['constructorId']
        # Add the stats to each constructor object
        if constructor_id in constructor_stats:
            constructor['stats'] = constructor_stats[constructor_id]
        else:
            constructor['stats'] = {'wins': 0, 'podiums': 0, 'poles': 0, 'championships': 0}

    # Step 5: Sort constructors by wins in descending order
    constructors.sort(key=lambda x: x['stats']['wins'], reverse=True)

    # Step 6: Render the template and pass both constructors and stats
    return render(request, 'constructors_card.html', {'constructors': constructors})

# Function to get stats for all constructors (now accepts the list of constructors)
def get_all_constructors_stats(constructors):
    constructor_stats = {}

    # Get stats for each constructor based on constructorId from the passed constructors
    for constructor in constructors:
        constructor_id = constructor['constructorId']
        constructor_stats[constructor_id] = get_constructor_stats(constructor_id)

    return constructor_stats

# Function to get individual constructor stats
def get_constructor_stats(constructor_id):
    wins = 0
    podiums = 0
    poles = 0
    championships = 0

    # Step 1: Get results for the 2024 season
    season = "2025"
    season_response = requests.get(f'https://api.jolpi.ca/ergast/f1/{season}/constructors/{constructor_id}/results.json')
    season_data = season_response.json()
    races = season_data['MRData']['RaceTable']['Races']

    for race in races:
        # Ignore sprint races
        if 'sprint' in race['raceName'].lower():
            continue

        position = int(race['Results'][0]['position'])
        qualifying_position = int(race['Results'][0]['grid'])

        if position == 1:
            wins += 1
        if 1 <= position <= 3:
            podiums += 1
        if qualifying_position == 1:
            poles += 1

    # Step 2: Get standings for the 2024 season to check if the constructor won the championship
    standings_response = requests.get(f'https://api.jolpi.ca/ergast/f1/{season}/constructors/{constructor_id}/constructorStandings.json')
    standings_data = standings_response.json()
    standings_list = standings_data['MRData']['StandingsTable']['StandingsLists']

    # Check if standings_list is non-empty and the expected position exists
    if standings_list:
        constructor_standings = standings_list[0].get('ConstructorStandings', [])
        if constructor_standings and constructor_standings[0].get('position') == '1':
            championships += 1

    return {
        'wins': wins,
        'podiums': podiums,
        'poles': poles,
        'championships': championships
    }


def home(request):
    # API URLs
    driver_url = 'https://api.jolpi.ca/ergast/f1/2025/driverStandings.json'
    constructor_url = 'https://api.jolpi.ca/ergast/f1/2025/constructorStandings.json'
    last_race_url = 'https://api.jolpi.ca/ergast/f1/current/last/results.json'

    try:
        # Fetch driver standings
        driver_response = requests.get(driver_url)
        driver_response.raise_for_status()
        driver_data = driver_response.json()
        driver_standings = driver_data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']

        # Fetch constructor standings
        constructor_response = requests.get(constructor_url)
        constructor_response.raise_for_status()
        constructor_data = constructor_response.json()
        constructor_standings = constructor_data['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']

        # Fetch last race results
        last_race_response = requests.get(last_race_url)
        last_race_response.raise_for_status()
        last_race_data = last_race_response.json()
        last_race_results = (
            last_race_data['MRData']['RaceTable']['Races'][0]['Results']
            if last_race_data['MRData']['RaceTable']['Races'] else []
        )
    except requests.exceptions.RequestException as e:
        driver_standings = []
        constructor_standings = []
        last_race_results = []
        print(f"API Error: {e}")

    # Context for the template
    context = {
        'driver_standings': driver_standings,
        'constructor_standings': constructor_standings,
        'last_race_results': last_race_results,
    }
    return render(request, 'homef1.html', context)


