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


def get_open_ai_answer(prompt):
    """Get result from OpenAI."""
    openai_key = Variable.get("openai_key")
    openai.api_key = openai_key
    resp = openai.Completion.create(
        model="text-davinci-003",
        max_tokens=200,
        prompt=prompt,
        n=1,
    )
    return resp["choices"][0]["text"].strip()
