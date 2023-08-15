from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

BaseModel = declarative_base()


class SentimentArticles(BaseModel):

    """News API articles."""

    __tablename__ = "articles"
    __table_args__ = {"schema": "sentiment"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    source = Column(String, nullable=False)
    created = Column(DateTime(timezone=True), default=func.now())
    modified = Column(DateTime(timezone=True), nullable=True)

    def __str__(self):
        """Str."""
        return self.id

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"""<SentimentArticles({self.id})>"""


class SentimentKeywords(BaseModel):

    """OpenAI API article keywords."""

    __tablename__ = "keyword"
    __table_args__ = {"schema": "sentiment"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(ForeignKey("sentiment.articles.id"), nullable=False)
    keyword = Column(String, nullable=True)
    created = Column(DateTime(timezone=True), default=func.now())
    modified = Column(DateTime(timezone=True), nullable=True)

    def __str__(self):
        """Str."""
        return self.id

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"""<SentimentKeywords({self.id})>"""


class SentimentValues(BaseModel):

    """OpenAI API article sentiment values."""

    __tablename__ = "sentiment_values"
    __table_args__ = {"schema": "sentiment"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(ForeignKey("sentiment.articles.id"), nullable=False)
    sentiment = Column(Integer, nullable=True)
    created = Column(DateTime(timezone=True), default=func.now())
    modified = Column(DateTime(timezone=True), nullable=True)

    def __str__(self):
        """Str."""
        return self.id

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"""<SentimentValues({self.id})>"""
