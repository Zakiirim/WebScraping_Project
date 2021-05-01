# -*- coding: utf-8 -*-
import scrapy
import operator

#FILTERS
#q 				JOB TITLE
#l 				CITY
#jt 			TYPE OF CONTRACT
#fromage 		HOW OLD THE JOB POSTING

limit = True

class Offers(scrapy.Item):
    title = scrapy.Field()
    company = scrapy.Field()
    description = scrapy.Field()
    published = scrapy.Field()
    city = scrapy.Field()
    link = scrapy.Field()
    
class LinksSpider(scrapy.Spider):
    
    name = 'job_offers'
    lim = limit
    maximum = 100
    count = 0
    
    def __init__ (self, job='', city = '', contract = '', maxold = '', *args, **kwargs):
        super(LinksSpider, self).__init__(*args, **kwargs)
        self.allowed_domains = ['indeed.com']
        filters = {
            'q=': job, 
        	'l=': city,
        	'jt=': contract,
        	'fromage=': maxold}
        url = 'https://pl.indeed.com/praca?' + "&".join([x+y.replace(' ', '+') for x, y in filters.items() if y])
        self.start_urls = [url]

    
    def parse(self, response):
        o = Offers()
        
        title_xpath = '//h2/a/@title'
        company_xpath_1 = '//span[@class="company"]/text()'
        company_xpath_2 = '//span[@class="company"]/a[@class="turnstileLink"]/text()'
        published_xpath = '//span[@class="date date-a11y"]/text()'
        city_xpath_1 = '//span[@class="location accessible-contrast-color-location"]/text()'
        city_xpath_2 = '//div[@class="location accessible-contrast-color-location"]/text()'
        link_xpath = '//h2/a/@href'
        
        o['title'] = response.xpath(title_xpath).extract()
        pom = response.xpath(company_xpath_1 + " | " + company_xpath_2).extract()
        while True:
            try:
                pom.remove("\n")
            except ValueError:
                break
            
        o['company'] = pom
        o['description'] = map(operator.itemgetter(0), [ul.xpath("string()").extract() for ul in response.xpath('//div[@class="summary"]/ul')])
        o['published'] = response.xpath(published_xpath).extract()
        o['city'] = response.xpath(city_xpath_1 + " | " + city_xpath_2).extract()
        o['link'] = response.xpath(link_xpath).extract()
        self.count = self.count + 1
        
        for tit, comp, desc, pub, cit, li in zip(o['title'], o['company'], o['description'], o['published'], \
                                                 o['city'], o['link']):
            yield {'Job Title': tit.strip(), 'Company': comp.strip(), 'Description': desc.strip(), \
                   'Published on': pub.strip(), 'City': cit.strip(), 'Link': '=HYPERLINK("%s", "%s")' % ('https://pl.indeed.com' + li.strip(), 'CLICK HERE')}

        next_page_url = response.css('#resultsCol > nav > div > ul > li > a::attr(href)').extract()[-1]
        
        if self.lim == True:
            if self.count < self.maximum:    
                if next_page_url:
                    next_page_url = response.urljoin(next_page_url)
                    yield response.follow(next_page_url, callback=self.parse)
        else:
            if next_page_url:
                next_page_url = response.urljoin(next_page_url)
                yield response.follow(next_page_url, callback=self.parse)
