import os
import datetime
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chat_models import init_chat_model

from models.models import EventCreate, EventExtract

load_dotenv()

embeddings_model = HuggingFaceEmbeddings(model_name='ibm-granite/granite-embedding-278m-multilingual')

def get_embedding(text: str) -> list[float]:
    return embeddings_model.embed_query(text)


### Extract Structured Output From Pulled Data ###
llm = init_chat_model("claude-3-5-sonnet-latest", model_provider="anthropic", anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'))

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert extraction algorithm. "
            "Only extract relevant information from the text. "
            "If you do not know the value of an attribute asked to extract, "
            "return null for the attribute's value.",
        ),
        MessagesPlaceholder("examples"),
        ("human", "{text}")
    ]
)

examples = [
    (
        'MeineDeineFamilie - eine Komödie Hohenzollerndamm 177 10713 Berlin  - zum Stadtplan Montag 31.03.2025 bis Mittwoch 02.04.2025   - Anfangszeit: 19:30 Uhr Kategorie: Comedy & Theater Ein Theaterprojekt mit von Wohnungslosigkeit bedrohten jungen Menschen. Die Aufführungen sind am 31.03., 01.04. und 02.04. Im Coupé Theater am Fehrbelliner Platz in Wilmersdorf. von: Robert Mehr Infos im Internet: http://www.theater-ohne-etikett.de',
        EventExtract(name='MeineDeineFamilie - eine Komödie', urls=['http://www.theater-ohne-etikett.de'], categories=['Comedy', 'Theater'], date_from=datetime.date(2025, 3, 31), time_from=datetime.time(19, 30), date_to=datetime.date(2025, 4, 2), time_to=None, location='Coupé Theater, Hohenzollerndamm 177, 10713 Berlin', price=None, is_registration_necessary=None, location_url=None)
    )
]

structured_llm = llm.with_structured_output(schema=EventExtract)

def get_structured_event_data(text: str) -> EventCreate:
    prompt = prompt_template.invoke(({"text": text, "examples": []}))
    result: EventExtract = structured_llm.invoke(prompt)
    return result
