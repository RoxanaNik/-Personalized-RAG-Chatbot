# translate_tweets.py

import openai
import time
from tqdm import tqdm
from dotenv import load_dotenv
import os

# 🛠️ Load API key from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 1. Load original Persian tweets
with open('clean_tweets.txt', 'r', encoding='utf-8') as file:
    persian_tweets = file.read().splitlines()

# 🛠️ Clean: remove empty lines
persian_tweets = [t.strip() for t in persian_tweets if t.strip() != ""]

# 2. Batch translate function
def batch_translate(tweets, batch_size=50):
    translated = []
    for i in tqdm(range(0, len(tweets), batch_size), desc="🔵 Translating Tweets"):
        batch = tweets[i:i+batch_size]
        joined_text = "\n".join(batch)

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a translator. Translate the following Persian tweets into English. Translate each line separately and keep the order. Only provide the translations."},
                {"role": "user", "content": joined_text}
            ]
        )

        translated_batch = response.choices[0].message.content.strip().split("\n")
        translated.extend(translated_batch)
        time.sleep(1)  # Sleep a little between batches to avoid rate limits
    return translated

# 3. Translate all tweets
translated_tweets = batch_translate(persian_tweets)

# 4. Save to a new translated dataset
with open('translated_tweets.txt', 'w', encoding='utf-8') as f:
    for t in translated_tweets:
        f.write(t.strip() + "\n")

print("✅ Translation Done! Saved to translated_tweets.txt")



