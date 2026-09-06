from groq import Groq
import os
import uuid
from datetime import datetime
from memory import save_message, get_relevant_memory, get_all_facts
from tools.search import search_web
from dotenv import load_dotenv

load_dotenv()

JARVIS_PROMPT = """You are JARVIS, a helpful AI assistant for Mustafa.
- Address Mustafa as "Sir"
- Keep responses to 2 sentences maximum
- Be witty and slightly formal
- NEVER output JSON, functions, or code
- Just respond naturally in plain English"""

SEARCH_KEYWORDS = ["search", "find", "look up", "what is", "who is",
    "latest", "news", "current", "weather", "price", "tell me about"]
TIME_KEYWORDS = ["time", "date", "day", "clock"]
MATH_KEYWORDS = ["calculate", "multiply", "divide", "add", "subtract", "plus", "minus"]
MEMORY_KEYWORDS = ["remember", "know about me", "what do you know", "my facts"]

class JarvisAgentV2:
    def __init__(self):
        self.conversation_id = str(uuid.uuid4())
        self.history = []
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama3-8b-8192"

    async def chat(self, user_message: str, user_name: str = "Sir") -> str:
        msg_lower = user_message.lower()
        extra_context = ""

        # Time tool
        if any(k in msg_lower for k in TIME_KEYWORDS):
            now = datetime.now()
            time_str = now.strftime('%I:%M %p on %A, %B %d, %Y')
            extra_context = f"The current time is {time_str}."

        # Math tool
        elif any(k in msg_lower for k in MATH_KEYWORDS):
            import re
            nums = re.findall(r'\d+\.?\d*', user_message)
            if len(nums) >= 2:
                a, b = float(nums[0]), float(nums[1])
                if any(k in msg_lower for k in ["multiply", "times"]):
                    extra_context = f"The answer is {a * b}."
                elif any(k in msg_lower for k in ["add", "plus"]):
                    extra_context = f"The answer is {a + b}."
                elif any(k in msg_lower for k in ["subtract", "minus"]):
                    extra_context = f"The answer is {a - b}."
                elif any(k in msg_lower for k in ["divide", "divided"]):
                    extra_context = f"The answer is {a / b:.2f}."

        # Memory tool
        elif any(k in msg_lower for k in MEMORY_KEYWORDS):
            facts = get_all_facts()
            extra_context = facts if facts else "No facts stored yet."

        # Search tool
        elif any(k in msg_lower for k in SEARCH_KEYWORDS):
            extra_context = search_web(user_message)

        # Build system prompt
        system_content = JARVIS_PROMPT
        relevant_memory = get_relevant_memory(user_message)
        if relevant_memory:
            system_content += f"\n\nPast context:\n{relevant_memory}"
        if extra_context:
            system_content += f"\n\nUse this information to answer:\n{extra_context}"

        # Build messages for Groq
        messages = [{"role": "system", "content": system_content}]

        # Add history
        for msg in self.history[-6:]:
            if msg["role"] == "user":
                messages.append({"role": "user", "content": msg["content"]})
            else:
                messages.append({"role": "assistant", "content": msg["content"]})

        # Add current message
        messages.append({"role": "user", "content": user_message})

        # Call Groq API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )

        reply = response.choices[0].message.content

        # Save to history
        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": reply})

        # Save to memory
        save_message("user", user_message)
        save_message("jarvis", reply)

        return reply
