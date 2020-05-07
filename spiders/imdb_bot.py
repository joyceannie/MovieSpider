import scrapy
import time
import random
import logging

class Imdbspider(scrapy.Spider):
    name = 'imdb_bot'

    start_urls = [
        'http://www.imdb.com/search/title/?title_type=feature&release_date=1950-01-01,2020-04-30&user_rating=1.0,10.0'
        ]
    imdbhome = 'http://www.imdb.com'
    
    # obtain the movie hrefs and next page's href
    def parse(self,response):
        logging.basicConfig()
        logger = logging.getLogger('imdb')
        logger.setLevel(logging.INFO)
        i = 1
        movie_hrefs = [self.imdbhome + ele for ele in response.selector.xpath('//h3[@class="lister-item-header"][1]/a/@href').extract()]
        #next_page = response.selector.xpath('(//a[@class="lister-page-next next-page"])[position()<last()]/@href').get()
        for movie in movie_hrefs:
            yield scrapy.Request(movie,callback=self.parse_movie)
            # sleep random 2 to 4 seconds
            time.sleep (random.randint(1,3))


    # obtain the needed data from a movie page and sent to ElasticSearch
    def parse_movie(self, response):
        title = response.selector.xpath('//div[@class="title_wrapper"]/h1/text()').extract_first()
        datePublished = response.selector.xpath('//div[@class="subtext"]/a[last()]/text()').extract_first()
        summary = response.selector.xpath('//div[@class="summary_text"]/text()').extract_first()
        genres = response.xpath("(//div[@class='subtext']//a)[position()<last()]/text()").extract()
        director = response.xpath("//*[@id='title-overview-widget']/div[2]/div[1]/div[2]/a/text()").extract()
        writer = response.xpath("//*[@id='title-overview-widget']/div[2]/div[1]/div[3]/a/text()").extract()
        main_cast_members = response.xpath("(//*[@id='title-overview-widget']/div[2]/div[1]/div[4]/a)[position()<last()]/text()").extract()
        rating = response.xpath("//div[@class='ratingValue']/strong/span/text()").extract()
        plot_keywords = response.xpath("//div[@class='see-more inline canwrap'][1]/a/@href").extract()
        rating = response.xpath("//div[@class='ratingValue']//span[@itemprop='ratingValue']/text()").extract_first()
        country = response.xpath("//div[h4[text() = 'Country:']]/a/text()").extract()
        language = response.xpath("//div[h4[text() = 'Language:']]/a/text()").extract()
        poster = response.xpath("//div[@class='poster']//img/@src").extract_first()
        yield {'title': self.normalize_string(title),
               'datePublished': self.normalize_string(datePublished),
               'summary': self.normalize_string(summary),
               'genres': genres,
               'director': director,
               'writer': writer,
               'main_cast_members': main_cast_members,
               'rating': self.normalized_float(rating),
               'plot_keywords': self.normalise_plot_keywords(plot_keywords),
               'country': country,
               'languages': language,
               'poster': poster}




    def normalized_float(self,num):
        return float(num)

    def normalize_string(self,s):
        return s.strip()


    def normalize_integer(self,num):
        return int(filter(lambda x: x.isdigit(), num))

    def normalise_plot_keywords(self, plot_keyword):
        keywords = []
        for keyword in plot_keyword:
            keywords.append(keyword.replace("/search/keyword?keywords=", ""))
        return keywords
    