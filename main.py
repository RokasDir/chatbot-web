import asyncio
import os
import streamlit as st
from agents import Agent, Runner, function_tool
from duckduckgo_search import DDGS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check if the OpenAI API key is set, stop the app if not
def check_openai_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OPENAI_API_KEY not found! Please set it in your .env file or environment.")
        st.stop()

# Tool for web search using DuckDuckGo, returns formatted results with clickable sources
@function_tool
def web_search(query: str) -> str:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            if not results:
                return f"No search results found for: {query}"
            answer_lines = []
            for i, r in enumerate(results):
                url = r.get('href', '').strip()
                if url:
                    answer_lines.append(
                        f"{i+1}. **{r.get('title', '')}**\n{r.get('body', '')}\n[Šaltinis: {url}]({url})"
                    )
                else:
                    answer_lines.append(
                        f"{i+1}. **{r.get('title', '')}**\n{r.get('body', '')}\n(šaltinio nuoroda nerasta)"
                    )
            answer = "\n\n".join(answer_lines)
            return answer
    except Exception as e:
        return f"Error performing web search: {e!s}"

# Detect if the prompt is in Lithuanian (for Lithuanian responses)
def is_lithuanian(prompt: str) -> bool:
    lithuanian_letters = "ąčęėįšųūž"
    if any(char in prompt.lower() for char in lithuanian_letters):
        return True
    common_words = ["krepšinis", "rezultatai", "komanda", "žaidėjas", "lyga", "lietuva", "lkl", "eurolyga"]
    if any(word in prompt.lower() for word in common_words):
        return True
    return False

# Detect if the prompt is about basketball (and not other sports)
def is_basketball_question(prompt: str) -> bool:
    other_sports = [
        "football", "soccer", "tennis", "hockey", "baseball", "golf", "cricket", "rugby", "volleyball", "swimming", "cycling", "skiing", "boxing", "mma", "ufc", "f1", "formula 1", "motorsport", "athletics", "track and field", "badminton", "table tennis", "ping pong", "handball", "wrestling", "gymnastics", "rowing", "sailing", "surfing", "skateboarding", "snowboarding", "ice skating", "karate", "judo", "taekwondo", "martial arts"
    ]
    basketball_keywords = [
        "basketball", "nba", "euroleague", "zalgiris", "rytas", "lkl", "lietuvos rytas", "lietkabelis", "neptunas", "siauliai", "jonava", "kedainiai", "dzukija", "pieno zvaigzdes", "prienai", "wolves vilnius", "lietuvos krepsinis", "lithuanian basketball", "lithuania basketball", "lietuvos krepsinio lyga"
    ]
    prompt_lower = prompt.lower()
    if any(word in prompt_lower for word in basketball_keywords):
        return True
    for sport in other_sports:
        if sport in prompt_lower:
            return False
    return True

# Get a response from the agent, using the last 3 user messages as context
async def get_agent_response(messages: list[dict[str, str]]) -> str:
    try:
        # Collect the last 3 user messages (or fewer if less than 3)
        user_messages = [msg["content"] for msg in messages if msg["role"] == "user"]
        # Join the last 3 messages into a single context string
        context = "\n".join(user_messages[-3:])

        # Set agent instructions based on language of the context
        if is_lithuanian(context):
            instructions = (
                "Tu esi naudingas asistentas, specializuojiesi krepšinyje, ypač Lietuvos krepšinio lygoje (LKL), Eurolygoje ir NBA. "
                "Atsakyk lietuviškai. Jei nežinai atsakymo, naudok web_search įrankį. Cituok šaltinius."
            )
        else:
            instructions = (
                "You are a helpful assistant specialized in basketball, especially Lithuanian basketball (LKL), Euroleague, and NBA. "
                "For every answer, always use the web_search tool to find and cite a source, even if you think you know the answer. "
                "Cite sources as clickable links."
            )
        # Create the agent with the appropriate instructions
        agent = Agent(
            name="BasketballAssistant",
            instructions=instructions,
            model="gpt-4o-mini",
            tools=[web_search],
        )
        # Pass the combined context to the agent as input
        result = await Runner.run(starting_agent=agent, input=context)
        return result.final_output or ""
    except Exception as e:
        st.error(f"Error calling OpenAI Agent: {e!s}")
        return ""

# Main Streamlit app logic
def main():
    st.title("🏀 Basketball Results Search Chatbot")
    st.caption("Ask about basketball game results, scores, and news!")
    check_openai_api_key()

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]

    # Display previous chat messages (except system message)
    for message in st.session_state.messages[1:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle user input and assistant response
    if prompt := st.chat_input("Ask about basketball results, scores, or news!"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        # Only answer basketball-related questions
        if not is_basketball_question(prompt):
            response = "Sorry, I am only a basketball fanatic and can only answer basketball-related questions."
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            with st.chat_message("assistant"), st.spinner("Searching and thinking..."):
                response = asyncio.run(get_agent_response(st.session_state.messages))
                st.markdown(response)
            if response:
                st.session_state.messages.append({"role": "assistant", "content": response})

    # Sidebar controls for chat history and instructions
    with st.sidebar:
        st.header("Chat Controls")
        if st.button("Clear Chat History"):
            st.session_state.messages = [
                {"role": "system", "content": "You are a helpful assistant."}
            ]
            st.rerun()
        st.markdown("---")
        st.markdown("### Instructions")
        st.markdown("1. Create a `.env` file with `OPENAI_API_KEY=your_key_here`")
        st.markdown("2. Type your message in the chat input")
        st.markdown("3. Press Enter to send")
        st.markdown("4. The assistant can search the web for current information!")
        st.markdown("5. Ask about the Lithuanian Basketball League (LKL), Euroleague, NBA, or Lithuanian teams!")
        st.markdown("---")
        st.markdown("### Features")
        st.markdown("✅ **Web Search**: Ask about current basketball news and results")
        st.markdown("✅ **Lithuanian Basketball**: Special focus on LKL and Lithuanian teams")
        st.markdown("✅ **Intelligent Routing**: Only answers basketball-related questions")
        st.markdown("✅ **Source Citations**: Clickable sources in responses")

if __name__ == "__main__":
    main()
