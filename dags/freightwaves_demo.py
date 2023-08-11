import json
from datetime import datetime, timedelta

from airflow.models import DAG, Variable
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from demo.models import SentimentArticles, SentimentKeywords, SentimentValues
from demo.utils import db_conn, get_article_title_from_id, get_open_ai_answer
from newsapi import NewsApiClient


def get_articles():
    """Get news headlines from API and persist to db."""
    news_key = Variable.get("news_key")
    sources = Variable.get("news_sources", deserialize_json=True)
    newsapi = NewsApiClient(api_key=news_key)
    today = datetime.now()
    yesterday = today + timedelta(days=-2)

    articles = newsapi.get_everything(
        q="politics",
        sources=",".join(sources),
        from_param=yesterday.strftime("%Y-%m-%d"),
        to=today.strftime("%Y-%m-%d"),
    )
    session = db_conn()
    ids = []
    for headline in articles["articles"]:
        url = headline["url"]
        title = headline["title"]
        source = headline["source"]["id"]
        article = SentimentArticles(url=url, title=title, source=source)
        session.add(article)
        session.commit()
        ids.append(article.id)
    session.close()
    return [min(ids), max(ids)]


default_args = dict(
    start_date=datetime(2021, 1, 1),
)


def get_keywords(**kwargs):
    """Based on news headlines get openai keywords for articles and persist to db."""
    ti = kwargs["ti"]
    article_id_range = ti.xcom_pull(task_ids="get_articles")
    prompt = """Based on the news headline,
                 provide the most important word bubble
                 terms associated with who or what the article is about.
                 If the term is a name, provider only the last name.
                 Provide a json list.

                 Desired Format: json list

                 Headline: {headline}

                 Answer:
               """
    session = db_conn()
    for _id in range(article_id_range[0], article_id_range[1] + 1):
        title = get_article_title_from_id(_id)
        prompt_updated = prompt.format(headline=title)
        openai_resp = get_open_ai_answer(prompt_updated)
        try:
            data = json.loads(openai_resp)
        except json.decoder.JSONDecodeError:
            keyword = SentimentKeywords(article_id=_id, keyword=None)
            session.add(keyword)
            continue
        for key in data:
            keyword = SentimentKeywords(article_id=_id, keyword=key)
            session.add(keyword)
    session.commit()
    session.close()


def get_sentiment(**kwargs):
    """Based on news headlines get openai sentiment values for articles and persist to db."""
    ti = kwargs["ti"]
    article_id_range = ti.xcom_pull(task_ids="get_articles")
    prompt = """
            Based on the news article headline provide a sentiment
            between 0 and 100 where 0 is the most negative and 100 is
            the most positive.
            Desired Format: an integer

            Headline: {headline}

            Sentiment:
    """
    session = db_conn()
    for _id in range(article_id_range[0], article_id_range[1] + 1):
        title = get_article_title_from_id(_id)
        prompt_updated = prompt.format(headline=title)
        openai_resp = get_open_ai_answer(prompt_updated)
        try:
            value = int(openai_resp)
        except ValueError:
            sentiment = SentimentValues(article_id=_id, sentiment=None)
            session.add(sentiment)
            continue
        sentiment = SentimentValues(article_id=_id, sentiment=value)
        session.add(sentiment)
    session.commit()
    session.close()


with DAG(
    "freightwaves_demo",
    schedule_interval=None,
    default_args=default_args,
    catchup=False,
) as dag:
    get_articles_task = PythonOperator(
        task_id="get_articles", python_callable=get_articles
    )

    get_keywords_task = PythonOperator(
        task_id="get_keywords", python_callable=get_keywords
    )

    get_sentiment_task = PythonOperator(
        task_id="get_sentiment", python_callable=get_sentiment
    )

    complete_task = DummyOperator(task_id="complete")

get_articles_task >> [get_keywords_task, get_sentiment_task] >> complete_task
