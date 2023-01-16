import json
from seleniumwire import webdriver
from seleniumwire.utils import decode
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

c = 'ph'

wireOptions = {
    'proxy': {
        'http': 'http://172.17.0.2:8118',
        'https': 'http://172.17.0.2:8118',
        'no_proxy': 'localhost,127.0.0.1'
    },
	'headless': True
}
selectedInformations = ['latlng', 'address']
query = '14.586682909876544,121.04927248148148'
searchFilter = 'search'
resultNumber = 1

def printArrayKey(arr, keyword):
	for i in arr:
		print(i[keyword], end = " \n")

def interceptor_search(request, myFilter=searchFilter, num=resultNumber):
	if myFilter in request.url and request.method == 'POST':
		print(f'{myFilter}-filter intercepted success: you are searching for the latlong: {query} :: {request.body}')
		params = json.loads(request.body)
		params['offset'] = int(8 * num)
		params['latlng'] = query
		# params['pageSize'] = int(32 * num)
		request.body = json.dumps(params).encode('utf-8')
		print(request.body)
		del request.headers['Content-Length']
		request.headers['Content-Length'] = str(len(request.body))

def seleniumWireConfig():
	option = Options()
	# option.add_argument("--headless") # Runs Chrome in headless mode.
	# option.add_argument('--no-sandbox') # # Bypass OS security model
	# option.add_argument('start-maximized')
	# option.add_argument('disable-infobars')
	# option.add_argument("--disable-extensions")
	chrome = webdriver.Chrome(seleniumwire_options=wireOptions, options=option)
	# chrome = webdriver.Chrome(seleniumwire_options=wireOptions)
	chrome.request_interceptor = interceptor_search
	return chrome

def seleniumStart(chrome):
	chrome.get(f'https://food.grab.com/{c}/en/restaurants')
	queryRes = getData(chrome)
	printOption(queryRes, selectedInformations)
	# queryRes = getData(chrome)
	# global selectedInformations
	# printOption(queryRes, selectedInformations, resultNumber)

def getData(driver):
	# search = driver.find_element_by_tag_name('button')
	search = driver.find_element(By.XPATH, '//*[@id="page-content"]/div[4]/div/div/div[4]/div/button')
	chrome.execute_script("window.scrollTo(0,document.body.scrollHeight)")
	delay = 3 # seconds
	try:
		myElem = WebDriverWait(chrome, delay).until(EC.presence_of_element_located((By.ID, 'location-input')))
		print("Page is ready!")
	except TimeoutException:
		print("Loading took too much time!")
	search.click()
	driver.wait_for_request('https://portal.grab.com/foodweb/v2/search').response
	for request in driver.requests:
		if searchFilter in request.url:
			print(f'{searchFilter} listening starts to = {request.url}')
			body = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
			body = body.decode('utf-8')
			body = json.loads(body)
			# print(body['searchResult']['searchMerchants'])
			return body['searchResult']['searchMerchants']

def printOption(options, keys, lineNum=100):
	i = int(1)
	for place in options:
		if i > lineNum: break
		else: i = i + 1
		for key in keys:
			print(f"{key}: {place[key]}")

if __name__ == '__main__':
	chrome = seleniumWireConfig()
	seleniumStart(chrome)
	chrome.close()
	# resultNumber = resultNumber + 1
	# chrome = seleniumWireConfig()
	# seleniumStart(chrome)