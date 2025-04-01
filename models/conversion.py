from models.models import EventCreate, EventDB, EventExtract


def event_extract_to_event_create(event_extract: EventExtract, source: str, url: str, description: str, embedding: list[float]) -> EventCreate:
    event: EventCreate = EventCreate(
        **event_extract.model_dump(),
        source=source,
        url=url,
        description=description,
        embedding=embedding
    )
    return event