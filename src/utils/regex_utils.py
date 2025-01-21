import re


def extract_youtube_url(text):
    youtube_pattern = r'(https?://(?:www\.)?(?:youtube|youtu|youtube-nocookie)\.(?:com|be)/(?:v/|e/|.*[?&]v=|.*[?&]embed=|.*[?&]watch\?v=|watch\?v=)([A-Za-z0-9_-]+))'

    youtube_urls = re.findall(youtube_pattern, text)

    urls = [url[0] for url in youtube_urls]

    if urls:
        return urls[0]

    return
