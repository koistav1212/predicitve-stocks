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

# STEP 1: Use weighted sentiment (recent news higher weight)
df_news["weight"] = 1 / (df_news.groupby("Ticker").cumcount() + 1)
df_news["Weighted_Sentiment"] = df_news["Sentiment_Score"] * df_news["weight"]

# STEP 2: Aggregate with multiple signals
news_grouped = df_news.groupby("Ticker").agg(
    Sentiment_Mean=('Sentiment_Score', 'mean'),
    Sentiment_Std=('Sentiment_Score', 'std'),
    Positive_Count=('Sentiment_Label', lambda x: (x == 'Bullish').sum()),
    Negative_Count=('Sentiment_Label', lambda x: (x == 'Bearish').sum()),
    News_Count=('Sentiment_Score', 'count'),
    Weighted_Sentiment=('Weighted_Sentiment', 'sum')
).reset_index()

# STEP 3: Build richer sentiment signal
news_grouped["Sentiment_Raw"] = (
    news_grouped["Sentiment_Mean"] * 0.5
    + (news_grouped["Positive_Count"] - news_grouped["Negative_Count"]) / news_grouped["News_Count"] * 0.3
    + news_grouped["Sentiment_Std"].fillna(0) * 0.2
)

# STEP 4: Normalize properly (Min-Max to 0-100)
min_s = news_grouped["Sentiment_Raw"].min()
max_s = news_grouped["Sentiment_Raw"].max()

news_grouped["Sentiment_Final"] = (
    (news_grouped["Sentiment_Raw"] - min_s) / (max_s - min_s)
) * 100

# STEP 5: Sharpening (scaled to preserve 0-100 boundary)
news_grouped["Sentiment_Final"] = (news_grouped["Sentiment_Final"] / 100) ** 1.2 * 100

# Merge with final_stock_summary.csv
df_summary = pd.read_csv("final_stock_summary.csv")

if "Sentiment_Final" in df_summary.columns:
    df_summary = df_summary.drop(columns=["Sentiment_Final"])

df_summary = df_summary.merge(news_grouped[["Ticker", "Sentiment_Final"]], on="Ticker", how="left")

# Save back
df_summary.to_csv("final_stock_summary.csv", index=False)
print("Updated final_stock_summary.csv successfully with Multi-Signal Sentiment_Final.")
