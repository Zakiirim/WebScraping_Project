from selenium import webdriver as wd
from selenium.webdriver.chrome.options import Options
import time
import sys
import pandas as pd

"""
FILTERS:
q 				JOB TITLE
l 				CITY
jt 				TYPE OF CONTRACT
fromage 		HOW OLD THE JOB POSTING
"""

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

# user_input = sys.argv
user_input = ["python", "-job", "Data Scientist", "-O", "risultatoselenium.xlsx", "-h"]
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

options = Options()
if any(map(lambda x: x in user_input, ['-h', '-headless'])):
	options.headless = True
else:
	options.headless = False
browser = wd.Chrome("chromedriver.exe", options=options)
request = browser.get(url)
try:
	pages_count = browser.find_element_by_id('searchCountPages')
except Exception:
	browser.close()
	raise Exception("No results available for your search")

pagination = browser.find_elements_by_css_selector("ul[class='pagination-list'] > li")[:-1]

if "-city" in user_input:
	city = [user_input[user_input.index("-city") + 1]]
else:
	city = list(map(lambda x: x.text, browser.find_elements_by_css_selector("span[class^='location'],div[class^='location']")))

# PAGINATION IS ['&start=10,20,30,40...']
if pages_count is None:
	raise Exception("No result found for your job search. Please change your criteria.")
else:
	def make_hyperlink(value):
		if len(value) < 256:
			return '=HYPERLINK("%s", "%s")' % (value, 'CLICK HERE')

	df = pd.DataFrame(columns=["Job Title", "Company", "Description", "Published on", "City", "Link"])
	c_page = 1
	page = iter(str(x) for x in range(10, 1000, 10))
	if not any(pagination):
		max_page = 2
	else:
		max_page = int(browser.find_elements_by_css_selector("ul[class='pagination-list'] > li")[-2].text)
	while c_page < max_page:
		current_page = '&start=' + next(page)
		url += current_page
		browser.get(url)
		try:
			browser.find_element_by_id("popover-x").click()
		except Exception:
			pass
		c_page += 1
		jobtitle = browser.find_elements_by_css_selector("a[data-tn-element='jobTitle']")
		links = list(map(lambda x: make_hyperlink(x.get_attribute('href')), jobtitle))
		jobtitle = browser.find_elements_by_css_selector("a[data-tn-element='jobTitle']")
		jobtitle = list(map(lambda x: x.text, jobtitle))
		company = list(map(lambda x: x.text, browser.find_elements_by_css_selector("span[class='company']")))
		description = list(map(lambda x: x.text, browser.find_elements_by_css_selector("div[class='summary']")))
		published_on = list(map(lambda x: x.text, browser.find_elements_by_css_selector("span[class='date date-a11y']")))
		city = city*len(jobtitle) if len(city) == 1 else city
		for el in zip(jobtitle, company, description, published_on, city, links):
			df.loc[len(df)] = list(el)

		url = url[:len(url)-len(current_page)]

	if len(df) > 0:
		df.to_csv(output_csv, index=False) if output_csv.endswith(".csv") else df.to_excel(output_csv, index=False)
	else:
		print("No results Found!")

	browser.close()
