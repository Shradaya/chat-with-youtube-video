from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

llm = ChatOpenAI(model="gpt-4o-mini")
embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")
