import requests
from bs4 import BeautifulSoup as soup


#FILTERS
position = 'data scientist'
city = 'gdansk'
days_filter = ''

#q 				JOB TITLE
#l 				CITY
#jt 			TYPE OF CONTRACT
#fromage 		HOW OLD THE JOB POSTING

filters = {
	'q=': 'data science',
	'l=': 'warszawa',
	'jt=': '',
	'fromage=': ''
}

url = 'https://pl.indeed.com/praca?' + "&".join(
	[x+y.replace(' ', '+') for x, y in filters.items() if y]
)
print(url)
request = requests.get(url)
response = soup(request.text, 'html.parser')
pages_count = response.find(id='searchCountPages')
pagination = response.select("ul[class='pagination-list'] > li")[:-1]
#PAGINATION IS ['&start=10,20,30,40...']

for page in ['00'] + ['10', '20', '30', '40'][:len(pagination)]:
	current_page = '&start=' + page #TO HANDLE
	url += current_page
	request = requests.get(url)
	response = soup(request.text, 'html.parser')
	jobtitle = response.select("a[data-tn-element='jobTitle']")
	company = response.select("span[class='company']")
	description = response.select("div[class='summary']")
	published_on = response.select("span[class='date date-a11y']")
	for el in zip(jobtitle, company, description, published_on):
		print(','.join(list(map(lambda x: x.text.replace('\n', ''), el))))
