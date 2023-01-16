from http.client import responses
from seleniumwire import webdriver  # Import from seleniumwire
import time
import json

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
    if 'search' in request.url:
        print('OUIIIIIIIIIIIII')
        print(type(request.body))
        print(f'Before: {request.body}')
        body = request.body.decode('utf-8')
        print(f'Body: {body}')
        # Load the JSON
        data = json.loads(body)
        print(f'Data: {data}')
        # Add a new property
        data['offset'] = '32'
        # Set the JSON back on the request
        request.body = json.dumps(data).encode('utf-8')
        print(f'After: {request.body}')
        # Update the content length
        del request.headers['Content-Length']
        request.headers['Content-Length'] = str(len(request.body))

driver.request_interceptor = interceptor
driver.get('https://food.grab.com/ph/en/restaurants')
time.sleep(5)
load_more = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[3]/div[4]/div/div/div[4]/div/button')
driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
load_more.click()
time.sleep(5)
load_more = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[3]/div[4]/div/div/div[4]/div/button')
load_more.click()
driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
time.sleep(5)
for request in driver.requests:
    if request.response and 'search' in request.url:
        print(
            request.body
        )
time.sleep(50000)
