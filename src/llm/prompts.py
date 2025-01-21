from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate

map_prompt = ChatPromptTemplate.from_messages(
    [("system", "Write a concise summary of the following:\\n\\n{context}")]
)

reduce_prompt = ChatPromptTemplate([("human", """
The following is a set of summaries:
{docs}
Take these and distill it into a final, consolidated summary
of the main themes.
""")])


RAG_PROMPT = PromptTemplate(template="""
<rules>
Answer to the provided question with the given context.
Do not go beyond the context to answer the questions. Do not assume.
Answer casual greetings and conversation QUESTION.
  For example,
    Human: Hey!
    AI: Hello! How can I help?
</rules>
Always abide by the rules mentioned within the <rules></rules> above. 
The context is provided between three backticks.
The question is provided between three astreik.
```{context}```

***{question}***
""", input_variables=["context", "question"])
