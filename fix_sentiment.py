import pandas as pd
from textblob import TextBlob

# 1. Load News Data
df_news = pd.read_csv("multi_company_news.csv")
df_news["Ticker"] = df_news["ticker"].str.upper()

# 2. Compute Sentiment
def get_sentiment(text):
    return TextBlob(str(text)).sentiment.polarity

df_news["Sentiment_Score"] = df_news["title"].apply(get_sentiment)

def label_sentiment(x):
    if x > 0.3:
        return "Bullish"
    elif x < -0.3:
        return "Bearish"
    else:
        return "Neutral"

df_news["Sentiment_Label"] = df_news["Sentiment_Score"].apply(label_sentiment)

# 3. Aggregate
news_grouped = df_news.groupby("Ticker").agg(
    News_Count=('Sentiment_Score', 'count'),
    Positive_Count=('Sentiment_Label', lambda x: (x == 'Bullish').sum()),
    Negative_Count=('Sentiment_Label', lambda x: (x == 'Bearish').sum())
).reset_index()

# 4. Compute Sentiment_Final
news_grouped["Sentiment_Final"] = (news_grouped["Positive_Count"] - news_grouped["Negative_Count"]) / news_grouped["News_Count"]
news_grouped["Sentiment_Final"] = (news_grouped["Sentiment_Final"] + 1) * 50

# 5. Merge with final_stock_summary.csv
df_summary = pd.read_csv("final_stock_summary.csv")

# If Sentiment_Final already exists, drop it to avoid _x, _y columns
if "Sentiment_Final" in df_summary.columns:
    df_summary = df_summary.drop(columns=["Sentiment_Final"])

df_summary = df_summary.merge(news_grouped[["Ticker", "Sentiment_Final"]], on="Ticker", how="left")

# 6. Save back
df_summary.to_csv("final_stock_summary.csv", index=False)
print("Updated final_stock_summary.csv successfully with Sentiment_Final.")
