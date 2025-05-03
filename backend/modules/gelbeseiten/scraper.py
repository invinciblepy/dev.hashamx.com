import os
import time
import random
import html
import user_agent
import logging
from bs4 import BeautifulSoup as bs
from .wrapper import fetch_url, post_form, post_multipart

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Create handler if not already configured
if not logger.handlers:
    # Create a file handler to log to a file
    log_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(log_dir, 'gelbeseiten_scraper.log')
    file_handler = logging.FileHandler(log_file)
    
    # Create a stream handler for console output
    stream_handler = logging.StreamHandler()
    
    # Create formatter and add to both handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    
    # Add both handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)



class gelbeseiten:
    def __init__(self, keyword, location):
        self.keyword = keyword
        self.location = location
        self.base_search_url = "https://www.gelbeseiten.de/suche"
        self.listings_url = "https://www.gelbeseiten.de/ajaxsuche"
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.gelbeseiten.de',
            'referer': 'https://www.gelbeseiten.de/',
            'user-agent': user_agent.generate_user_agent(),
        }
        self.per_page = 10
        self.current_position = 0
        self.items = []


    def scrape(self):
        payload = {
            "WAS": self.keyword,
            "WO": self.location,
        }
        response = post_form(self.base_search_url, data=payload, headers=self.headers)
        logger.info(f"Search Response: {response.status_code}")
        soup = bs(response.text, "lxml")
        if response.status_code != 200:
            logger.info("[x] No Companies found")
            return 0, []
        self.total_items = soup.find('span', {'id':'mod-TrefferlisteInfo'}).text
        if self.total_items and self.total_items.strip().isdigit():
            self.total_items = int(self.total_items)
            self.items = self.listing_ajax()
        else:
            self.total_items = 0
            logger.info("[x] No Companies found")
        logger.info(f"Total items: {self.total_items}")
        logger.info(f"Items: {self.items}")
        return self.total_items, self.items
        
    def listing_ajax(self):
        self.headers.pop('content-type')
        self.headers['path'] = '/ajaxsuche'
        
        files = {
            'umkreis': (None, '-1'),
            'verwandt': (None, 'false'),
            'WAS': (None, self.keyword),
            'WO': (None, self.location),
            'position': (None, str(self.current_position)),
            'anzahl': (None, str(self.per_page)),
            'sortierung': (None, 'relevanz'),
        }
        response = post_multipart(self.listings_url, files=files, headers=self.headers)
        logger.info(f"Listing AJAX Response: {response.status_code}")
        if response.status_code == 200:
            response = response.json()
            html_text = response.get('html')
            self.extract_from_html(html_text)
        return self.items

    def extract_from_html(self, html_text):
        html_text = html.unescape(html_text)
        soup = bs(html_text, "lxml")
        items = soup.find_all('article')
        for item in items:
            details = self.get_item_details(item.get('data-realid'))
            if details:
                self.items.append(details)


    def get_item_details(self, item_id):
        url = f"https://www.gelbeseiten.de/gsbiz/{item_id}"
        response = fetch_url(url, headers=self.headers)
        soup = bs(response.text, "lxml")
        item_details = {'name': '', 'category': '', 'rating': '', 'telephone': '', 'fax': '', 'website': '', 'email': '', 'address': ''}

        try:
            main = soup.find('main')
            content = main.find('div', id='content') if main else None
            if not content:
                return {}

            basic = content.find('div', class_='mod-TeilnehmerKopf__teilnehmerdaten-wrapper')
            name_wrap = basic.find('div', class_='mod-TeilnehmerKopf__Name-wrapper') if basic else None

            item_details['name'] = name_wrap.find('h1').text.strip() if name_wrap and name_wrap.find('h1') else ''
            item_details['category'] = (name_wrap.find('div', class_='mod-TeilnehmerKopf__branchen') or {}).text.strip() if name_wrap else ''
            ratings = name_wrap.find('a', class_='mod-TeilnehmerKopf__bewertungen') if name_wrap else None
            if ratings and ratings.find('span'):
                item_details['rating'] = ratings.find('span').text.strip()

            address_block = basic.find('div', class_='mod-TeilnehmerKopf__zusaetzliche-daten')
            address = address_block.find('address').text.strip() if address_block and address_block.find('address') else ''
            item_details['address'] = address.replace('\n', ' ').strip()

            email_tag = content.find('div', id='email_versenden')
            if email_tag and email_tag.get('data-link'):
                item_details['email'] = email_tag.get('data-link').split('?')[0].replace('mailto:', '')

            kontakt = content.find('section', id='kontaktdaten')
            kontakt_inner = kontakt.find('div', class_='mod-Kontaktdaten__container--inner') if kontakt else None

            if kontakt_inner:
                item_details['telephone'] = self.extract_kontakt_item(kontakt_inner, 'contains-icon-big-tel')
                item_details['fax'] = self.extract_kontakt_item(kontakt_inner, 'contains-icon-big-fax')
                item_details['website'] = self.extract_kontakt_item(kontakt_inner, 'contains-icon-big-homepage')
        except Exception as e:
            logger.error(f"[ERROR] Failed to parse item {item_id}: {e}")
        time.sleep(random.randint(1, 3))
        return item_details

    def extract_kontakt_item(self, section, class_name):
        item = section.find('div', class_=class_name)
        if item:
            anchor = item.find('a')
            if anchor and anchor.get('href'):
                return anchor['href'].replace('tel:', '').replace('https://', '').strip()
            return item.text.strip()
        return ''
