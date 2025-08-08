from groq import Groq

client = Groq(api_key="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")

def get_qadrix(messages_):
    completion = client.chat.completions.create(
        model="llama3-70b-8192", 
        messages=messages_,
        temperature=0.9,
        max_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )
    abc = completion.choices[0].message.content
    return abc
