# YouTube Summarizer Streamlit App

This is a simple Streamlit application that allows you to summarize YouTube videos by providing their URL. The app fetches the video content, processes it, and generates a concise summary of the video's key points.

## Requirements

pip install -r requirements.txt

### Set up the Environment Variables

The app requires an API key for interacting with YouTube and other services. To keep these values secure, you should use an `.env` file.

1. **Create a `.env` file:**

   Navigate to the `src/config/` directory and create a `.env` file.

2. **Add your API keys:**

   In your `.env` file, add the necessary keys. For example:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

   Replace the placeholder values with your actual API keys.

### Directory Structure

The directory structure of the project is as follows:

```
youtube-summarizer/
│
├── src/
│   ├──              # Streamlit app entry point
│   ├── config/
│   │   └── .env            # Environment configuration file
│   ├── llm/                # Initialize LLM model and embedding
│   ├── loader/             # Initialize YouTube Data Handler
│   ├── vectorDB/           # Initialize vector DB
│   └── utils/              # Helper functions
├── requirements.txt        # Required Python packages
└── app.py                  # Application executor
└── README.md               # This README file
```

## Running the Application

Once everything is set up, you can run the application with Streamlit.

```bash
streamlit run app.py
```

This will start a local Streamlit server, and you should see a URL printed in your terminal. Open that URL in your web browser to interact with the YouTube Summarizer app.
