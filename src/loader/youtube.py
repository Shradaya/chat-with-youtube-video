import os
import shutil
import whisper
import requests
import yt_dlp as youtube_dl
from bs4 import BeautifulSoup
from .constants import OUTPUT_PATH
from langchain_text_splitters import CharacterTextSplitter
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled


class YoutubeLoader:
    def __init__(self, url, video_id, title, local=False, language=["en"], translation=["en"]):
        self.url = url
        self.video_id = video_id
        self.language = language
        self.translation = translation
        self.local = local
        self.title = title
        self.sub_title = ""

    @staticmethod
    def extract_video_id(youtube_url: str) -> str:
        """Extract video ID from common YouTube URLs."""
        video_id = youtube_url.split("=")[-1]
        if not video_id:
            raise ValueError(
                f'Could not determine the video ID for the URL "{youtube_url}".'
            )
        return video_id

    @staticmethod
    def get_title(video_url: str):
        """Extract title of the YouTube video"""
        r = requests.get(video_url)
        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.find_all(name="title")[0]
        title = str(title)
        title = title.replace("<title>", "").replace("</title>", "")
        return title

    @classmethod
    def from_youtube_url(cls, youtube_url: str, **kwargs: dict):
        """
        Creates an instance of the class from a YouTube URL.

        Validates the URL to ensure it is from a supported YouTube domain and 
        extracts the video ID and title. The extracted information is passed 
        as arguments to initialize the class instance.

        Args:
            youtube_url (str): The YouTube video URL.
            **kwargs (dict): Additional keyword arguments to be passed to the class constructor.

        Returns:
            cls: An instance of the class initialized with the YouTube URL, video ID, and additional data.

        Raises:
            ValueError: If the URL is not from a supported YouTube domain.
        """
        ALLOWED_NETLOCS = {
            "youtu.be",
            "m.youtube.com",
            "youtube.com",
            "www.youtube.com",
            "www.youtube-nocookie.com"
        }
        allowed_url = [
            True for netlocs in ALLOWED_NETLOCS if netlocs in youtube_url]
        if True not in allowed_url:
            raise ValueError(
                "The URL provided isn\'t of supported format."
            )
        video_id = cls.extract_video_id(youtube_url)
        kwargs.update({"title": cls.get_title(youtube_url)})
        return cls(youtube_url, video_id, **kwargs)

    @classmethod
    def from_local_file_path(cls, uploaded_file, **kwargs: dict):
        """
        Creates an instance of the class from a YouTube URL.

        Validates the URL to ensure it is from a supported YouTube domain and 
        extracts the video ID and title. The extracted information is passed 
        as arguments to initialize the class instance.

        Args:
            youtube_url (str): The YouTube video URL.
            **kwargs (dict): Additional keyword arguments to be passed to the class constructor.

        Returns:
            cls: An instance of the class initialized with the YouTube URL, video ID, and additional data.

        Raises:
            ValueError: If the URL is not from a supported YouTube domain.
        """
        file_id = uploaded_file.file_id
        audio_output_path = f"{OUTPUT_PATH}/{file_id}.mp3"
        with open(audio_output_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        kwargs.update({
            "url": audio_output_path,
            "video_id": file_id,
            "title": uploaded_file.name,
            "local": True
        })
        return cls(**kwargs)

    def __create_or_empty_directory(self, directory_path):
        """
        Creates a new directory if it doesn't exist, or empties the existing directory.

        If the specified directory exists, it removes all files and subdirectories inside it. 
        If the directory doesn't exist, it creates the directory.

        Args:
            directory_path (str): The path to the directory to create or empty.

        """
        if os.path.exists(directory_path):
            for filename in os.listdir(directory_path):
                file_path = os.path.join(directory_path, filename)
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
        else:
            os.makedirs(directory_path)

    def __download_audio_from_video(self):
        """
        Downloads the audio from a YouTube video and saves it as an MP3 file.

        This method attempts to download the audio from the video URL using the 
        `pytube` library. If that fails, it falls back to using `youtube_dl` to 
        download the audio in `.webm` format. The resulting audio file is saved 
        in a predefined output directory.

        Returns:
            str: The path to the downloaded audio file (MP3 or .webm).

        Raises:
            Exception: If unable to download the audio.
        """
        self.__create_or_empty_directory(OUTPUT_PATH)
        try:
            output_path = f'{OUTPUT_PATH}\output.webm'
            options = {
                'format': 'bestaudio/best',
                'keepvideo': False,
                'outtmpl': output_path,
                'restrictfilenames': True,
                'noplaylist': True,
                'nocheckcertificate': True,
                'ignoreerrors': False,
                'logtostderr': False,
                'quiet': True,
                'no_warnings': True,
                'default_search': 'auto',
                'source_address': '0.0.0.0'
            }

            with youtube_dl.YoutubeDL(options) as ydl:
                ydl.download([self.url])

            print("Download complete... {}".format(output_path))
            return output_path
        except Exception as e:
            return

    def __self_transcribe_audio(self, audio_path):
        """
        Transcribes the audio from a given file using the Whisper model.

        This method loads the Whisper model and attempts to transcribe the audio 
        from the specified file. If an error occurs during the transcription process, 
        it prints a message and returns `None`.

        Args:
            audio_path (str): The file path of the audio to transcribe.

        Returns:
            dict or None: The transcription result as a dictionary if successful, 
                        or None if transcription fails or there is an error.

        Raises:
            Exception: If the transcription process fails due to invalid audio file or model loading issue.
        """
        try:
            model = whisper.load_model("base")
            result = model.transcribe(audio_path)
            if not result:
                print("Audio Not Found in the provided file")
                return None
            return result
        except Exception as e:
            print(f"An error occurred during transcription: {e}")
            return None

    def load(self):
        """
        Loads the YouTube transcript or transcribes the audio if no transcript is available.

        This method first attempts to retrieve the transcript of the YouTube video using 
        the YouTube Transcript API. If the transcript is not available or disabled, it 
        falls back to downloading the audio from the video, transcribing it using Whisper, 
        and storing the transcription text.

        The resulting transcript (either from the YouTube API or Whisper) is stored in 
        the `sub_title` attribute of the class.

        Raises:
            Exception: If both transcript retrieval and audio transcription fail.
        """
        if not self.local:
            try:
                # Attempt to get the transcript from the YouTube Transcript API
                sub = YouTubeTranscriptApi.get_transcript(self.video_id)
                self.sub_title = " ".join([x['text'] for x in sub])
            except TranscriptsDisabled:
                # If transcripts are disabled for this video, notify and try to transcribe audio
                print(
                    "Transcripts are disabled for this video. Processing can take extra time.")
            except Exception as e:
                # Catch any other errors related to transcript retrieval
                print(f"Error retrieving transcript: {e}")
        if not self.sub_title:
            try:
                # If subtitle is not set, download audio and transcribe it
                audio_path = self.url if self.local else self.__download_audio_from_video()
                if not audio_path:
                    return
                result = self.__self_transcribe_audio(audio_path)
                if result:
                    self.sub_title = result.get("text", "")
                    print(self.sub_title)
            except Exception as e:
                print(f"Error in audio extraction or transcription: {e}")
                print("Audio could not be extracted or transcribed.")

    def divide_into_chunks(self):
        if not self.sub_title:
            raise Exception("No Subtitle Found.")

        text_splitter = CharacterTextSplitter(
            separator="\n\n",
            chunk_size=500,
            length_function=len,
            is_separator_regex=False,
        )
        splitted_text = text_splitter.create_documents([self.sub_title])
        return splitted_text
