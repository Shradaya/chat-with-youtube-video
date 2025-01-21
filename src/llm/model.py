from ..config import config
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

llm = ChatOpenAI(model="gpt-4o-mini", api_key=config.OPENAI_API_KEY)
embedding_model = OpenAIEmbeddings(
    model="text-embedding-ada-002", api_key=config.OPENAI_API_KEY)
