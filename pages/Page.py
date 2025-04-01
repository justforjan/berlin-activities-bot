from abc import ABC, abstractmethod
from datetime import date as _date
from logging import Logger

from bs4 import BeautifulSoup
import requests
from sqlalchemy import exists, insert
from sqlalchemy.orm import Session

from models.conversion import event_extract_to_event_create
from models.models import EventDB, EventCreate
from AI.structured_output import get_embedding, get_structured_event_data


class PageLoader(ABC):

    def __init__(self, base_url: str, engine, logger: Logger):
        self.base_url = base_url
        self.engine = engine
        self.logger = logger


    def load(self, date: _date):

        self.logger.info(f"Retreiving data of {date} for {self.base_url}")

        # Check, if date of source is in database
        with Session(self.engine) as session:
            date_exists_in_db = session.query(exists().where(EventDB.date_from == date)).scalar()
            session.commit()


        if date_exists_in_db:
            self.logger.info(f"Data for date {date} already exists in the database. No further action needed")
            return True

        self.logger.info(f"Data for date {date} does not yet exists in the database. Data will be pulled for {self.base_url}")

        # Get list of all event Urls
        date_path =  self.create_date_path(date)
        print(date_path)
        raw_html = requests.get(f"{self.base_url}/{date_path}").content
        soup = BeautifulSoup(raw_html, 'html.parser')
        soup = self.strip_unnecessary_parts(soup)
        events_urls = self.get_urls_of_all_events(soup)

        self.logger.debug(f'Found {len(events_urls)} event urls on {date}:\n{events_urls[:5]}...')


        # IF NOT date in database:
        #   FOR all event Urls:
        #       loadEvent(eventUrl)

        self.load_events_into_db(events_urls[:5], date)


        # ELSE:
        #   FOR eventUrl:
        #       IF NOT eventUrl in database: (per Cache?)
        #           loadEvent(eventUrl)
        # return True if it worked


        # def loadEvent(eventUrl)
        #   load event html (strip unnecessary html)
        #   get structured information of event
        #   get embeddings
        #   load everyting into database (bulk import perhaps)


    @abstractmethod
    def create_date_path(self, date: _date) -> str:
        pass

    @abstractmethod
    def strip_unnecessary_parts(self, soup: BeautifulSoup):
        pass

    @abstractmethod
    def get_urls_of_all_events(self, soup: BeautifulSoup) -> list[str]:
        pass

    def load_events_into_db(self, events_urls: list[str], date: _date):
        events_as_dict: list[dict] = []

        self.logger.debug('Start loading events data')
        for event_url in events_urls:
            event = self.load_event(event_url)
            if event:
                if event.date_from is None:
                    event.date_from = date
                events_as_dict.append(event.model_dump())

        self.logger.debug(f'Writing {len(events_as_dict)} events into the database')

        with Session(self.engine) as session:
            session.execute(insert(EventDB).returning(EventDB.id), events_as_dict)
            session.commit()

        self.logger.debug(f'Wrote events to db')


    def load_event(self, event_url: str) -> EventCreate | None:
        event_content = self.get_event_html(event_url)
        if event_content:
            # get structured output with langchain
            extracted_event = get_structured_event_data(event_content)
            self.logger.debug(f'Structured Event: {extracted_event}')
            # get embedding with langchain
            embedding = get_embedding(event_content)
            self.logger.debug(f'Embeddings for {event_url}: {embedding[:5]}...')
            return event_extract_to_event_create(extracted_event, self.base_url, event_url, event_content, embedding)
        return None




    @abstractmethod
    def get_event_html(self, event_url) -> str:
        pass


