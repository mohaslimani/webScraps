from http.client import responses
from seleniumwire import webdriver  # Import from seleniumwire
import time
import json
from seleniumwire.utils import decode

options = webdriver.ChromeOptions()
wire_options = {
    'proxy': {
        'https': 'http://192.168.99.100:8118',
        'no_proxy': 'localhost,127.0.0.1'
    }
}

driver = webdriver.Chrome(executable_path='/Users/msoulaim/Desktop/selenium/chromedriver-mac', 
    options=options, seleniumwire_options=wire_options)


def interceptor(request):
    if 'autocomplete' in request.url:
        print('OUIIIIIIIIIII')
        params = request.params
        params['keyword'] = 'p'
        params['limit'] = 100
        request.params = params

driver.request_interceptor = interceptor
driver.get('https://food.grab.com/ph/en/restaurants')
time.sleep(5)
search_input = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[2]/div[2]/div/div/div/div[2]/div/div/div[2]/div/div/div')
search_input.click()
search_input = driver.find_element_by_id('location-input')
search_input.send_keys('n')
time.sleep(5)
for request in driver.requests:
    if 'autocomplete' in request.url:
        body = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
        body = body.decode('utf-8')
        body = json.loads(body)
        for place in body['places']:
            print(f"Adresse: {place['address']}")
            print(f"location: {place['location']}")

time.sleep(50000)
