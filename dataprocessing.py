import json

# 1. Open and clean tweets.js
with open('tweets.js', 'r', encoding='utf-8') as f:
    raw = f.read()

# Remove the JavaScript header
raw = raw.replace('window.YTD.tweets.part0 = ', '')

# Load as JSON
tweets = json.loads(raw)

# 2. Extract and filter original tweets
original_tweets = []

for tweet_obj in tweets:
    tweet = tweet_obj['tweet']  # the actual tweet is under 'tweet'

    # Filter conditions:
    is_retweet = 'retweeted_status_id' in tweet
    is_reply = tweet.get('in_reply_to_status_id') is not None
    is_quote = 'quoted_status_id' in tweet

    if not is_retweet and not is_reply and not is_quote:
        text = tweet['full_text']
        original_tweets.append(text)

print(f"✅ Found {len(original_tweets)} original tweets (no replies, no retweets, no quotes).")

# 3. Save to a clean text file
with open('clean_tweets.txt', 'w', encoding='utf-8') as f:
    for t in original_tweets:
        f.write(t.strip() + '\n')
