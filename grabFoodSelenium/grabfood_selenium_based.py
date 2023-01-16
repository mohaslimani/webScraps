import json
from seleniumwire import webdriver
from seleniumwire.utils import decode
import time

options = webdriver.ChromeOptions()
options.add_argument("--log-level=3")
driver = webdriver.Chrome(options=options)


def type_str(str, apply):
    '''
        simulate user typing
    '''
    for char in str:
        apply(char)
        time.sleep(1)
    time.sleep(2)


def click(elem):
    '''
    handling element click using js
    '''
    driver.execute_script("arguments[0].click();", elem)


def search(query, countryCode="ph"):
    '''
        get the available places based on query represent the address location
    '''
    driver.get(f"https://food.grab.com/ph/{countryCode}/")
    locationInput = driver.find_element_by_id("location-input")
    type_str(query, locationInput.send_keys)
    places = driver.find_elements_by_tag_name(
        'ul')[3].find_elements_by_tag_name('li')
    _places = []
    for place in places:
        _places.append((place, place.text))
    return _places


def getPlaces():
    '''
        get nearest places based on selected location
    '''
    # check if load more exist
    try:
        loadMore = driver.find_element_by_tag_name("button")
    except:
        return [], 0
    click(loadMore)
    # wait for the api give a response
    response = driver.wait_for_request(
        f'https://portal.grab.com/foodweb/v2/search').response
    # parsing the data
    body = decode(response.body, response.headers.get(
        'Content-Encoding', 'identity'))
    jsonBody = body.decode()
    data = json.loads(jsonBody)
    searchResult = data['searchResult'] if 'searchResult' in data else {}
    places = searchResult['searchMerchants'] if 'searchMerchants' in searchResult else [
    ]
    _places = []
    for place in places:
        location = place['latlng']
        address = place['address']
        _places.append((
            address['name'],
            location['latitude'],
            location['longitude']
        ))
    totalCount = searchResult['totalCount'] if 'totalCount' in searchResult else 0
    return _places, totalCount


def interact():
    '''
        an interact program help you set your location
        and get's the nerest places
    '''
    # for selecting country
    print("availbale countries:")
    print("1: Indonesia")
    print("2: Philippines")
    print("3: Thailand")
    print("4: Vietnam")
    print("5: Singapore")
    print("6: Malaysia")
    print("7: Myanmar")
    countryCode = ["id", "ph", "th", "vn", "sg", "my",
                   "mm"][int(input("Please select a country: ")) - 1]
    # for searching using autocompelete api
    query = input("Please enter search value: ")
    places = search(query, countryCode=countryCode)
    # print availble places based on search query
    for i, place in enumerate(places):
        _, name = place
        print(f'{i+1}: {name}')
    choice = int(input("Please select place: ")) - 1
    # for clikcing on the selected place
    elem = places[choice][0]
    click(elem)
    # for clicking on search button
    searchBtn = driver.find_element_by_class_name(
        'searchContainer___3M35s').find_element_by_tag_name("button")
    searchBtn.click()
    # for waiting until redirection complete
    driver.wait_for_request(f'/{countryCode}/en/restaurants')
    # for getting places based on a given location
    # notice that the api can only provide 32 results as max
    # - get the first 32 results
    # - ask the user for results amounts
    # - get more results and combine them
    places, totalCount = getPlaces()
    if totalCount == 0 or len(places) == 0:
        return print(f"Nothing came back, Try another search term")
    print(f"There is {totalCount} results")
    if totalCount > 32:
        total = int(
            input(f"Please choose result amount [32 - {totalCount}]: "))
        for _ in range((total - 32) // 32):
            _places, _ = getPlaces()
            places += _places
            time.sleep(2)
        rest = (total - 32) % 32
        if rest > 0:
            _places, _ = getPlaces()
            places += _places
    for i, place in enumerate(places):
        address, lat, lon = place
        print(f'{i+1}: {address}, ({lat}, {lon})')
    driver.quit()


if __name__ == '__main__':
    interact()
