from langchain_text_splitters import CharacterTextSplitter


def split_by_character(text: str, chunk_size: int = 500) -> list:
    text_splitter = CharacterTextSplitter(
        separator=". ",
        chunk_size=chunk_size,
        length_function=len,
        is_separator_regex=False,
    )
    texts = text_splitter.create_documents([text])
    return texts
