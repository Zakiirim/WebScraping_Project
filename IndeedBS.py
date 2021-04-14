import requests
from bs4 import BeautifulSoup as soup
import sys


#FILTERS
#q 				JOB TITLE
#l 				CITY
#jt 			TYPE OF CONTRACT
#fromage 		HOW OLD THE JOB POSTING

user_keys = {
	'-job': 'q=',
	'-city': 'l=',
	'-contract': 'jt=',
	'-maxold': 'fromage='
}

filters = {
	'q=': '',
	'l=': '',
	'jt=': '',
	'fromage=': ''
}

user_input = sys.argv
print(user_input)
if len(user_input) < 2:
	raise Exception("You must provide at least one argument!")
else:
	for arg in user_keys:
		if arg in user_input:
			filters[user_keys[arg]] = user_input[user_input.index(arg) + 1]

url = 'https://pl.indeed.com/praca?' + "&".join(
	[x+y.replace(' ', '+') for x, y in filters.items() if y]
)
request = requests.get(url)
response = soup(request.text, 'html.parser')
pages_count = response.find(id='searchCountPages')
pagination = response.select("ul[class='pagination-list'] > li")[:-1]
#PAGINATION IS ['&start=10,20,30,40...']
if pages_count is None:
	raise Exception("No result found for your job search. Please change your criteria.")
else:
	print("Job Title,Company,Description,Published on")
	for page in ['00'] + ['10', '20', '30', '40'][:len(pagination)]:
		current_page = '&start=' + page
		url += current_page
		request = requests.get(url)
		response = soup(request.text, 'html.parser')
		jobtitle = response.select("a[data-tn-element='jobTitle']")
		company = response.select("span[class='company']")
		description = response.select("div[class='summary']")
		published_on = response.select("span[class='date date-a11y']")
		for el in zip(jobtitle, company, description, published_on):
			print(','.join(list(map(lambda x: x.text.replace('\n', ''), el))))

		request.close()
		url = url[:len(url)-len(current_page)]
