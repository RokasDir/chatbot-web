# 🏀 Basketball Results Search Chatbot

A Streamlit-powered chatbot specialized in basketball, with a focus on Lithuanian Basketball League (LKL), Euroleague, NBA, and Lithuanian teams. The assistant can answer questions in both English and Lithuanian, always citing sources for factual answers using web search.

## Features

- **Basketball Specialist:** Answers only basketball-related questions, with deep knowledge of LKL, Euroleague, NBA, and Lithuanian basketball teams.
- **Web Search Integration:** Uses DuckDuckGo search to find up-to-date information and always cites sources as clickable links.
- **Contextual Memory:** Remembers the last 3 user questions to provide context-aware answers, making follow-up questions more natural.
- **Lithuanian and English Support:** Detects if the question is in Lithuanian and responds in the same language.
- **Source Citations:** Every answer includes a clickable source link when information is retrieved from the web.
- **Streamlit UI:** Clean, interactive chat interface with chat history, memory clearing, and sidebar instructions.

## Setup Instructions

1. **Clone the repository:**
   ```sh
   git clone <your-repo-url>
   cd chatbot-web
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   pip install git+https://github.com/openai/openai-agents-python.git
   ```
3. **Set up your API key:**
   - Create a `.env` file in the project root with your OpenAI API key:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ```
4. **Run the app:**
   ```sh
   streamlit run main.py
   ```

## Usage
- Type your basketball-related question in English or Lithuanian.
- The chatbot will answer using its own knowledge and/or by searching the web, always citing sources.
- Only basketball-related questions are answered. For other sports, the assistant will politely refuse.
- The last 3 user questions are used as context for better follow-up answers.
- Use the sidebar to clear chat history and view instructions/features.

## Customization
- **Change context length:** Edit the number in `user_messages[-3:]` in `main.py` to remember more or fewer messages.
- **Expand basketball keywords:** Add more keywords to the `basketball_keywords` list for broader topic detection.
- **Language support:** The app can be extended to support more languages by updating the detection logic and instructions.

## Technologies Used
- [Streamlit](https://streamlit.io/) for the web UI
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) for agent orchestration
- [DuckDuckGo Search](https://pypi.org/project/duckduckgo-search/) for web search
- [python-dotenv](https://pypi.org/project/python-dotenv/) for environment variable management

## License
MIT License