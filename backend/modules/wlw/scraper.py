import time
from urllib import parse
import user_agent
import random
from .wrapper import fetch_url


class wlw:
    def __init__(self, url=None):
        self.base_url = "https://www.wlw.de/de/suche"
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'user-agent': user_agent.generate_user_agent(),
        }
        self.url = url
        self.items = []
        self.total_items = 0

    def create_params(self, url):
        params = {}
        if "/products" in url:
            print("[x] Product Pages Not Supported")
            exit()
        else:
            parsed_url = parse.urlparse(url)
            query_params = parsed_url.query.replace("q=", "")
            tld = parsed_url.netloc.split(".")[-1]
            params["query"] = query_params
            params["lang"] = tld
            params["country"] = tld.upper()
            params["site"] = "wlw"
            params["top_level_domain"] = tld.upper()
            params["city_extraction_radius"] = "50km"
            params["sort"] = "responsiveness"
            params["userLatitude"] = random.uniform(48.0, 54.0)
            params["userLongitude"] = random.uniform(6.0, 15.0)
        return params

    def scrape(self, page=1):
        if "/products" in self.url:
            print("[x] Product Pages Not Supported")
            return
        params = self.create_params(self.url)
        params["page"] = page
        response = fetch_url("https://www.wlw.de/search-frontend/alibaba-api/online.company.search", params=params, headers=self.headers)
        companies = response.get("data", {}).get("companies", [])
        for company in companies:
            self.items.append({
                "name": company.get("name"),
                "street": company.get("street"),
                "city": company.get("city"),
                "zip_code": company.get("zipcode"),
                "country": company.get("country_code"),
                "supplier_types": ", ".join(company.get("supplier_types", [])),
                "phone_number": company.get("phone_number"),
                "homepage": company.get("homepage"),
                "slug": company.get("slug"),
                "description": company.get("highlightings", {}).get("secondary_description", ""),
                "employee_count": company.get("employee_count"),
                "product_count": company.get("product_count"),
                "distribution_area": company.get("distribution_area"),
                "founding_year": company.get("founding_year"),
                "average_response_time": company.get("average_response_time"),
            })
            time.sleep(0.5)
        return self.total_items,self.items
