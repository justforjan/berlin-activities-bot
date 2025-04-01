from logging import Logger

from pages.Page import PageLoader

from datetime import date as _date
from bs4 import BeautifulSoup
import requests

class GratisInBerlin(PageLoader):

    def __init__(self, engine, logger: Logger):
        super().__init__('https://www.gratis-in-berlin.de', engine ,logger)

    def create_date_path(self, date: _date):
        return f"kalender/tagestipps/{date.isoformat()}"

    def strip_unnecessary_parts(self, soup: BeautifulSoup):
        return soup.find("ul", class_="leadingblock")

    def get_urls_of_all_events(self, soup: BeautifulSoup) -> list[str]:
        events_html =  soup.select("ul.leadingblock li")
        events_urls: list[str] = []
        for event_html in events_html:
            a_tag =  event_html.find("h2", class_="overviewcontentheading").find("a")
            if a_tag:
                events_urls.append(self.base_url + a_tag["href"])
        return events_urls

    # async def fetch_event_html(self, session, url):
    #     async with session.get(url) as response:
    #         if response.status == 200:
    #             content = await response.text()
    #             eventHtml = BeautifulSoup(content, 'html.parser')
    #             eventHtml.find(class_='buttons').decompose()
    #             eventHtml.find(class_='comments').decompose()
    #             eventHtml = eventHtml.find(id='gib_tip')
    #             return eventHtml.get_text(" ", strip=True).replace('\t', '')
    #     return None

    # async def retreive_html_of_all_events(self):
    #     async with aiohttp.ClientSession() as session:
    #         tasks = [self.fetch_event_html(session, url) for url in self.eventsUrls[:10]]
    #         self.eventsElements = await asyncio.gather(*tasks)

    # def retreive_html_of_all_events(self):
    #     for eventUrl in self.eventsUrls:
    #         respone = requests.get(eventUrl)
    #         if respone.status_code == 200:
    #             eventHtml = BeautifulSoup(respone.content, 'html.parser')
    #             eventHtml = eventHtml.find(id='gib_tip')
    #             eventHtml.find(class_='buttons').decompose()
    #             eventHtml.find(class_='comments').decompose()
    #             self.eventsElements.append(eventHtml.get_text(" ", strip=True).replace('\t', ''))

    def get_event_html(self, event_url) -> str | None:
        response = requests.get(event_url)
        if response.status_code == 200:
            event_html = BeautifulSoup(response.content, 'html.parser')
            event_html = event_html.find(id='gib_tip')
            event_html.find(class_='buttons').decompose()
            event_html.find(class_='comments').decompose()
            return event_html.get_text(" ", strip=True).replace('\t', '')


