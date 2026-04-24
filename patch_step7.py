import nbformat
import os

def update_notebook():
    path = "market_news_scrapper.ipynb"
    with open(path, "r") as f:
        nb = nbformat.read(f, as_version=4)
        
    for cell in nb.cells:
        if cell.cell_type == "markdown":
            source = cell.source
            if "STEP 7: MODELING" in source:
                cell.source = "### STEP 7: MODELING\n\n**Input**: `stock_data_ohlcv.csv` (10,000+ rows) containing continuous historical OHLCV market patterns.\n\n**What is Happening**: The Machine Learning ensemble is trained *exclusively* on robust technical indicators (`Return_1D`, `Volatility_5D`, `Volume_Spike`, etc.) independently of scraped news. This avoids destroying the 3.3-year historical integrity since news only spans 2 weeks.\n\n**Result**: Evaluates the model globally across all stocks (`model_comparison.csv`), and subsequently iteratively trains and outputs predictions per-ticker independently (`model_comparison_per_stock.csv`)."
            elif "STEP 10, 11, 12:" in source:
                cell.source = "### STEP 10, 11, 12: EXPORTS AND UI RESOURCES\n\n**Input**: The complete merged dataset, clustering labels, and ML predictions per stock.\n\n**What is Happening**: Generating visualizations and iterating over all 15 targeted companies directly to build a highly organized file system.\n\n**Result**: Saves Price, Sentiment, and Volatility line plots inside dedicated folders per company (`static/stocks/TSLA/price.png`). Generates independent JSON APIs for dynamic loading in the HTML UI."

        if cell.cell_type == "code":
            source = "".join(cell.source)
            if "def train_evaluate(X, y_clf, y_reg" in source:
                cell.source = """from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error, mean_absolute_error, r2_score
import pandas as pd
import numpy as np

# Use EXCLUSIVELY stock_data_ohlcv.csv to preserve 3+ years of data
df_stock_ml = df_stock.copy().dropna(subset=['Return_1D', 'Volatility_5D', 'Volume_Spike', 'Momentum_3D'])

features = [
    'Return_1D',
    'Volatility_5D',
    'Volume_Spike',
    'Momentum_3D'
]

def train_evaluate(X, y_clf, y_reg, suffix=''):
    if len(X) < 10: return [], pd.DataFrame()
    X_train, X_test, y_clf_train, y_clf_test = train_test_split(X, y_clf, test_size=0.2, shuffle=False)
    _, _, y_reg_train, y_reg_test = train_test_split(X, y_reg, test_size=0.2, shuffle=False)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    models_clf = {
        'Decision Tree': DecisionTreeClassifier(random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'SVM': SVC(kernel='rbf', probability=True, random_state=42),
        'Naive Bayes': GaussianNB()
    }
    results = []
    preds_out = pd.DataFrame(index=X_test.index)
    for name, model in models_clf.items():
        if name == 'SVM':
            model.fit(X_train_scaled, y_clf_train)
            preds = model.predict(X_test_scaled)
        else:
            model.fit(X_train, y_clf_train)
            preds = model.predict(X_test)
        
        if name == 'Random Forest': preds_out['Pred_Random_Forest'] = preds
        acc = accuracy_score(y_clf_test, preds)
        prec = precision_score(y_clf_test, preds, zero_division=0)
        rec = recall_score(y_clf_test, preds, zero_division=0)
        f1 = f1_score(y_clf_test, preds, zero_division=0)
        results.append({
            'Model': name,
            'Ticker/Group': suffix,
            'Accuracy': round(acc, 4),
            'Precision': round(prec, 4),
            'Recall': round(rec, 4),
            'F1 Score': round(f1, 4)
        })
        
    models_reg = {'Linear Regression': LinearRegression(), 'Ridge': Ridge(random_state=42)}
    for name, model in models_reg.items():
        model.fit(X_train_scaled, y_reg_train)
        preds = model.predict(X_test_scaled)
        if name == 'Linear Regression': preds_out['Pred_Linear_Reg'] = preds
    return results, preds_out

X_all = df_stock_ml[features]
y_clf_all = df_stock_ml['Direction']
y_reg_all = df_stock_ml['Return_3D']

print("--- TRAINING OVERALL MODEL (USING 3+ YEARS OHLCV) ---")
all_results, preds_out_all = train_evaluate(X_all, y_clf_all, y_reg_all, suffix='ALL STOCKS')

all_results_df = pd.DataFrame(all_results)
all_results_df = all_results_df.sort_values(by='F1 Score', ascending=False)
all_results_df.to_csv('model_comparison.csv', index=False)
print(all_results_df.to_string(index=False))

print("\\n--- TRAINING PER-STOCK MODEL (USING 3+ YEARS OHLCV) ---")
per_stock_results = []
COMPANIES = ['TSLA','NVDA','AAPL','AMD','AMZN','MSFT','GOOGL','META','BAC','INTC','CSCO','KO','XOM','NFLX','NKE']
df_test_out = pd.DataFrame()

for ticker in COMPANIES:
    df_t = df_stock_ml[df_stock_ml['Ticker'] == ticker]
    if len(df_t) < 10: continue
    
    X_t = df_t[features]
    y_clf_t = df_t['Direction']
    y_reg_t = df_t['Return_3D']
    
    r, p = train_evaluate(X_t, y_clf_t, y_reg_t, suffix=ticker)
    per_stock_results.extend(r)
    
    df_t_test_out = df_t.loc[p.index].copy()
    df_t_test_out['Pred_Linear_Reg'] = p['Pred_Linear_Reg']
    df_t_test_out['Pred_Random_Forest'] = p['Pred_Random_Forest']
    df_test_out = pd.concat([df_test_out, df_t_test_out])

per_stock_results_df = pd.DataFrame(per_stock_results)
per_stock_results_df.to_csv('model_comparison_per_stock.csv', index=False)

print(f"\\nGenerated per-stock evaluation for {len(per_stock_results_df['Ticker/Group'].unique())} tickers.")
"""
            elif "Visualizations and JSON API exported!" in source:
                cell.source = """import os
import json
import matplotlib.pyplot as plt
import seaborn as sns

df_merged.to_csv("final_dataset.csv", index=False)
df_test_out.to_csv("model_predictions.csv", index=False)
# If cluster features are valid
if 'Cluster' in df_merged.columns:
    df_merged[['Date', 'Ticker', 'Cluster', 'Cluster_Label']].to_csv("clustering_output.csv", index=False)
if not rules.empty:
    rules.to_csv("association_rules.csv", index=False)

COMPANIES = ['TSLA','NVDA','AAPL','AMD','AMZN','MSFT','GOOGL','META','BAC','INTC','CSCO','KO','XOM','NFLX','NKE']

for ticker in COMPANIES:
    os.makedirs(f"static/stocks/{ticker}", exist_ok=True)
    td = df_merged[df_merged['Ticker'] == ticker].copy().sort_values('Date')
    
    if len(td) < 2:
        td = df_stock[df_stock['Ticker'] == ticker].copy().sort_values('Date')
        if 'Sentiment_Avg' not in td.columns: td['Sentiment_Avg'] = 0.0
    
    if len(td) < 2: continue
    
    plt.figure(figsize=(6,4)); sns.lineplot(x='Date', y='Close', data=td); plt.title(f"{ticker} Price"); plt.xticks(rotation=45); plt.tight_layout(); plt.savefig(f"static/stocks/{ticker}/price.png"); plt.close()
    plt.figure(figsize=(6,4)); sns.lineplot(x='Date', y='Sentiment_Avg', data=td); plt.title(f"{ticker} Sentiment"); plt.xticks(rotation=45); plt.tight_layout(); plt.savefig(f"static/stocks/{ticker}/sentiment.png"); plt.close()
    plt.figure(figsize=(6,4)); sns.lineplot(x='Date', y='Volatility_5D', data=td); plt.title(f"{ticker} Volatility"); plt.xticks(rotation=45); plt.tight_layout(); plt.savefig(f"static/stocks/{ticker}/volatility.png"); plt.close()
    
    latest = td.iloc[-1]
    t_rows = df_test_out[df_test_out['Ticker'] == ticker]
    p_3d = t_rows.iloc[-1].get('Pred_Linear_Reg', 0.0) if len(t_rows) > 0 else 0.0
    direction = ("UP" if t_rows.iloc[-1].get('Pred_Random_Forest', 0) == 1 else "DOWN") if len(t_rows) > 0 else "FLAT"
    trend = "Bullish" if latest.get('Sentiment_Avg', 0) > 0 else "Bearish"
    
    api_dict = {
      "ticker": ticker,
      "avg_sentiment": float(round(latest.get('Sentiment_Avg', 0.0), 4)),
      "trend": trend,
      "volatility": float(round(latest.get('Volatility_5D', 0.0), 4)),
      "prediction_next_3d": float(round(p_3d, 4)),
      "direction": direction
    }
    with open(f"static/data/{ticker}.json", "w") as f:
        json.dump(api_dict, f, indent=4)

print("Visualizations per stock and JSON API exported into isolated folders successfully!")
"""
    with open(path, "w") as f:
        nbformat.write(nb, f)

if __name__ == "__main__":
    update_notebook()
