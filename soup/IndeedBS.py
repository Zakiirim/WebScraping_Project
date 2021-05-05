import requests
from bs4 import BeautifulSoup as soup
import sys
import pandas as pd


limit_search = True

'''
FILTERS
q 				JOB TITLE
l 				CITY
jt 				TYPE OF CONTRACT
fromage 		HOW OLD THE JOB POSTING
'''

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

if "-city" in user_input:
	city = [user_input[user_input.index("-city") + 1]]
else:
	city = response.select("span[class^='location'],div[class^='location']")

# PAGINATION IS ['&start=10,20,30,40...']
if pages_count is None:
	raise Exception("No result found for your job search. Please change your criteria.")
else:

	def make_hyperlink(value):
		if len(value) < 256:
			base_url = 'https://pl.indeed.com{}'
			return '=HYPERLINK("%s", "%s")' % (base_url.format(value), 'CLICK HERE')

	pages_count = int(pages_count.text.split(" - ")[-1].split()[0])
	df = pd.DataFrame(columns=["Job Title", "Company", "Description", "Published on", "City", "Link"])
	c_page = 1

	if '-max' in user_input:
		max_page = int(user_input[user_input.index('-max') + 1])
		max_page = max_page if max_page <= pages_count else pages_count
	else:
		max_page = pages_count if not limit_search else 100
	page = iter(str(x) if len(str(x)) > 1 else "0" + str(x) for x in range(0, 100000, 10))
	request.close()

	while c_page <= max_page:
		current_page = '&start=' + next(page)
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
			df.loc[len(df)] = list(map(lambda x: x.text.replace('\n', '') if not isinstance(x, str) else x, el)) + [next(links)]

		request.close()
		url = url[:len(url)-len(current_page)]
		c_page += 1

	if len(df) > 0:
		df.to_csv(output_csv, index=False) if output_csv.endswith(".csv") else df.to_excel(output_csv, index=False)
	else:
		print("No results Found!")