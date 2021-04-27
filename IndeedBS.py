import requests
from bs4 import BeautifulSoup as soup
import sys
import pandas as pd


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
if len(user_input) < 2:
	raise Exception("You must provide at least one argument!")
else:
	for arg in user_keys:
		if arg in user_input:
			filters[user_keys[arg]] = user_input[user_input.index(arg) + 1]

url = 'https://pl.indeed.com/praca?' + "&".join(
	[x+y.replace(' ', '+') for x, y in filters.items() if y]
)

output_csv = False if '-O' not in user_input else user_input[user_input.index('-O') + 1]
if not output_csv:
	raise Exception("You must provide the -O wildcard with the output name!")

request = requests.get(url)
response = soup(request.text, 'html.parser')
pages_count = response.find(id='searchCountPages')
pagination = response.select("ul[class='pagination-list'] > li")[:-1]

if "-city" in user_input:
	city = [user_input[user_input.index("-city") + 1]]
else:
	city = response.select("span[class^='location'],div[class^='location']")

#PAGINATION IS ['&start=10,20,30,40...']
if pages_count is None:
	raise Exception("No result found for your job search. Please change your criteria.")
else:
	def make_hyperlink(value):
		if len(value) < 256:
		    url = 'https://pl.indeed.com{}'
		    return '=HYPERLINK("%s", "%s")' % (url.format(value), 'CLICK HERE')

	df = pd.DataFrame(columns=["Job Title","Company","Description","Published on", "City", "Link"])
	for page in ['00'] + ['10', '20', '30', '40'][:len(pagination)]:
		current_page = '&start=' + page
		url += current_page
		request = requests.get(url)
		response = soup(request.text, 'html.parser')
		jobtitle = response.select("a[data-tn-element='jobTitle']")
		links = map(lambda x: make_hyperlink(x['href']), jobtitle)
		company = response.select("span[class='company']")
		description = response.select("div[class='summary']")
		published_on = response.select("span[class='date date-a11y']")
		city = city*len(jobtitle) if len(city) == 1 else city
		for el in zip(jobtitle, company, description, published_on, city):
			df.loc[len(df)] = list(map(lambda x: x.text.replace('\n', ''), el)) + [next(links)]

		request.close()
		url = url[:len(url)-len(current_page)]

	if len(df) > 0:
		df.to_csv(output_csv, index=False) if output_csv.endswith(".csv") else df.to_excel(output_csv, index=False)
	else:
		print("No results Found!")