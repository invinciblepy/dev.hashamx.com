import time
import random
from user_agent import generate_user_agent
from ..wlw.wrapper import fetch_url


class europages:
    def __init__(self, keyword):
        self.base_url = 'https://www.europages.co.uk/search-frontend/alibaba-api/online.company.search'
        self.headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': generate_user_agent()
        }
        self.languages = {"en":"co.uk", "fr":"fr", "de":"de", "it":"it", "es":"es", "nl":"nl", 
                          "pl":"pl", "tr":".com.tr", "cz":"cz", "dk":"dk", "ee":"ee", "gr": "gr",
                          "lt":"lt", "hu":"co.hu", "no":"no", "pt":"pt", "ro":"ro", "si":"si",
                          "fi":"fi", "se":"se", "bg":"bg"}
        self.total_companies = 0
        self.items = []
        self.keyword = keyword

    def scrape(self, page=1):
        params = {
            'query': self.keyword,
            'lang': "en",
            'country': "gb",
            'site': 'ep',
            'cityExtractionRadius': '50km',
            'userLatitude': random.uniform(48.0, 54.0),
            'userLongitude': random.uniform(6.0, 15.0),
            'shuffle': 'true',
            'verified': 'false',
            'limit': '9',
            'sort': 'responsiveness',
            'goodResponders': 'true',
            'scene': 'topResponders',
            'page': 1
        }
        self.headers['referer'] = f"https://www.europages.co.uk/en/search?q={self.keyword}"
        response = fetch_url(self.base_url, params=params, headers=self.headers)
        code = response.get('code')
        if code != 200:
            print("[X] Error: {}".format(code))
            return 
        data = response.get('data')
        self.total_companies = data.get('paging').get('total')
        for company in data.get('companies'):
            self.items.append({
                "name": company.get('name'),
                "phone": company.get('phone_number'),
                "website": company.get('homepage'),
                "street": company.get('street'),
                "country": company.get('country_code'),
                "zipcode": company.get('zipcode'),
                "city": company.get('city'),
                "acronym": company.get('acronym'),
                "description": company.get('description'),
                "distribution_area": company.get('distribution_area'),
                "average_response_time": company.get('average_response_time'),
                "founding_year": company.get('founding_year'),
                "employee_count": company.get('employee_count')
            })
            time.sleep(0.5)
        return self.total_companies, self.items
