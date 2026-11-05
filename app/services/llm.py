from langchain_groq import ChatGroq

from app.core.config import settings


llm = ChatGroq(
    model=settings.groq_model,
    api_key=settings.groq_api_key,
    temperature=0,
)