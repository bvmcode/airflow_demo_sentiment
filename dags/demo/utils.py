import openai
from airflow.hooks.base import BaseHook
from airflow.models import Variable
from demo.models import SentimentArticles
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def db_conn():
    """Get DB connection."""
    conn = BaseHook.get_connection("freightwaves_rds")
    conn_url = f"postgresql+psycopg2://{conn.login}:{conn.password}@{conn.host}:{conn.port}/{conn.schema}"
    engine = create_engine(conn_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def get_article_title_from_id(_id):
    """Get article title from db from article id."""
    session = db_conn()
    record = (
        session.query(SentimentArticles).filter(SentimentArticles.id == _id).first()
    )
    session.close()
    return record.title


def get_keyword_prompt(headline):
    """Prompt for openai to get headline keywords."""
    return f"""Based on the news headline,
               provide the most important word bubble
               terms associated with who or what the article is about.
               If the term is a name, provider only the last name.
               Provide a json list.

                Desired Format: json list

                Headline: {headline}

                Answer:
               """


def get_sentiment_prompt(headline):
    """Prompt for openai to get headline sentiment value."""
    return f"""
            Based on the news article headline provide a sentiment
            between 0 and 100 where 0 is the most negative and 100 is
            the most positive.
            Desired Format: an integer

            Headline: {headline}

            Sentiment:
        """


def get_open_ai_answer(headline, prompt_type="keyword"):
    """Get result from OpenAI."""
    if prompt_type == "keyword":
        prompt = get_keyword_prompt(headline)
    elif prompt_type == "sentiment":
        prompt = get_sentiment_prompt(headline)
    else:
        raise ValueError(f"prompt_type `{prompt_type}` is invalid")
    openai_key = Variable.get("openai_key")
    openai.api_key = openai_key
    resp = openai.Completion.create(
        model="text-davinci-003",
        max_tokens=200,
        prompt=prompt,
        n=1,
    )
    return resp["choices"][0]["text"].strip()
