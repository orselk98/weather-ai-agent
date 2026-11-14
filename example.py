import os
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

chat_completion = client.chat.completions.create(
    messages=[
        {"role" : "user",
         "content" : "Write a short poem about the ocean.",
         }
    ],
    #temperature = 0,
    model="openai/gpt-oss-120b",
)
print(chat_completion.choices[0].message.content)
    
