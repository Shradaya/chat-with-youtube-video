from .llm.graph import app
from .loader.youtube import YoutubeLoader
from .llm.invoke import get_response_message
from .llm.splitter import split_by_character
from .vectorDB.chroma import ChromaDBManager
from .utils.regex_utils import extract_youtube_url
from .constants import (
    COLLECTION_NAME,
    CHUNK_TYPE,
    SUMMARY_TYPE,
    NO_URL_RESPONSE,
    WRONG_URL_RESPONSE,
    EXTRACTION_FAILED_RESPONSE,
    URL_KEY_TERM,
    INITIAL_MESSAGE
)

loader = None
db_manager = ChromaDBManager(collection_name=COLLECTION_NAME)


def get_context(query: str, video_id: str) -> str:
    documents = db_manager.query(
        query=query,
        filter_query={
            "$and": [
                {
                    "type": CHUNK_TYPE
                },
                {
                    "id": video_id
                }
            ]
        })
    document_list = [document.page_content for document in documents]
    return " ".join(document_list)


def get_existing_summary(user_query: str, video_id: str) -> str:
    documents = db_manager.query(
        query=user_query,
        filter_query={
            "$and": [
                {
                    "type": SUMMARY_TYPE
                },
                {
                    "id": video_id
                }
            ]
        }, n_results=1)
    if documents:
        document = documents[0]
        return document.page_content


async def generate_summary(split_docs: list) -> str:
    async for step in app.astream(
        {"contents": [doc.page_content for doc in split_docs]},
        {"recursion_limit": 10},
    ):
        print(list(step.keys()))
    summary = step.get('generate_final_summary', {}).get('final_summary')
    return summary


async def execute(title: str):
    global loader

    import streamlit as st
    st.title(f"💬 {title}")
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": INITIAL_MESSAGE}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if user_input := st.chat_input():
        st.session_state.messages.append(
            {"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)
        if user_input:
            if not loader and URL_KEY_TERM not in user_input:
                response = NO_URL_RESPONSE
            elif URL_KEY_TERM in user_input:
                url = extract_youtube_url(user_input)
                if not url:
                    response = WRONG_URL_RESPONSE

                loader = YoutubeLoader.from_youtube_url(url)
                summary = get_existing_summary(user_input, loader.video_id)
                video_already_scraped = True if summary else False
                if video_already_scraped:
                    response = summary
                else:
                    loader.load()
                    if not loader.sub_title:
                        response = EXTRACTION_FAILED_RESPONSE
                    else:
                        summary_text_list = split_by_character(
                            loader.sub_title, chunk_size=5000)
                        text_list = split_by_character(
                            loader.sub_title, chunk_size=500)
                        response = await generate_summary(summary_text_list)
                        text_list.append(response)
                        metadata = {
                            "id": loader.video_id,
                            "title": loader.title,
                            "type": CHUNK_TYPE
                        }
                        await db_manager.add_documents(
                            text_list, metadata, has_summary=True)

            elif URL_KEY_TERM not in user_input:
                context = get_context(user_input, loader.video_id)
                response = get_response_message(context, user_input)
            print(loader.title)
            response = f"**{loader.title}**\n\n{response}"
            st.session_state.messages.append(
                {"role": "assistant", "content": response})
            st.chat_message("assistant").write(response)
