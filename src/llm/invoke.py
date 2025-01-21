from .model import llm
from .prompts import RAG_PROMPT
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


def get_response_message(context, question):
    qa_lcel = (
        RunnablePassthrough()
        | RAG_PROMPT
        | llm
        | StrOutputParser()
    )
    result = qa_lcel.invoke({
        "context": context, "question": question
    })
    return result
