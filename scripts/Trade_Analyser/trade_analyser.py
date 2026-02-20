import pandas as pd
import numpy as np
from datetime import datetime

def analyze_trades(file_path, output_html="trade_analysis.html"):
    try:
        # 1. Load the CSV
        df = pd.read_csv(file_path)
        
        # 2. Data Cleaning & Filtering
        # We only care about executed trades with a recorded profit
        trades = df[df['Profit'].notnull()].copy()
        
        # Remove XAGUSD as requested in previous analysis
        trades = trades[trades['Symbol'] != 'XAGUSD']
        
        # Convert time and calculate Net Profit
        trades['Update Time'] = pd.to_datetime(trades['Update Time'])
        trades['Commission'] = trades['Commission'].fillna(0)
        trades['Net Profit'] = trades['Profit'] + trades['Commission']
        
        # 3. Metric Calculations
        total_trades = len(trades)
        avg_pl = trades['Net Profit'].mean()
        
        wins = trades[trades['Net Profit'] > 0]
        losses = trades[trades['Net Profit'] <= 0]
        winrate = (len(wins) / total_trades * 100) if total_trades > 0 else 0
        
        gross_profit = wins['Net Profit'].sum()
        gross_loss = abs(losses['Net Profit'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss != 0 else np.inf
        
        highest_profit = trades['Net Profit'].max()
        highest_loss = trades['Net Profit'].min()
        
        # 4. Weekly Grouping
        trades['Year'] = trades['Update Time'].dt.year
        trades['Week'] = trades['Update Time'].dt.isocalendar().week
        weekly_stats = trades.groupby(['Year', 'Week']).agg(
            Trade_Count=('Net Profit', 'count'),
            Weekly_Profit=('Net Profit', 'sum')
        ).reset_index().sort_values(['Year', 'Week'], ascending=False)

        # 5. Generate HTML Content
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Trade Analysis Report</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background-color: #f0f2f5; }}
                .container {{ max-width: 1000px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
                h1, h2 {{ color: #1a73e8; text-align: center; }}
                .metrics-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 30px 0; }}
                .card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid #e0e0e0; }}
                .card h3 {{ margin: 0; font-size: 0.9em; color: #5f6368; }}
                .card p {{ margin: 10px 0 0; font-size: 1.5em; font-weight: bold; color: #202124; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
                th {{ background-color: #f1f3f4; color: #5f6368; }}
                .pos {{ color: #1e8e3e; font-weight: bold; }}
                .neg {{ color: #d93025; font-weight: bold; }}
                .week-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 15px; margin-top: 20px; }}
                .week-card {{ padding: 15px; border-radius: 8px; border: 1px solid #ddd; background: #fff; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Trading Execution Analysis</h1>
                
                <div class="metrics-grid">
                    <div class="card"><h3>Total Trades</h3><p>{total_trades}</p></div>
                    <div class="card"><h3>Average P&L</h3><p>${avg_pl:.2f}</p></div>
                    <div class="card"><h3>Winrate</h3><p>{winrate:.2f}%</p></div>
                    <div class="card"><h3>Profit Factor</h3><p>{profit_factor:.2f}</p></div>
                </div>

                <h2>Summary Statistics</h2>
                <table>
                    <tr><td>Total Number of Trades</td><td>{total_trades}</td></tr>
                    <tr><td>Highest Profitable Trade</td><td class="pos">${highest_profit:.2f}</td></tr>
                    <tr><td>Highest Loss</td><td class="neg">${highest_loss:.2f}</td></tr>
                </table>

                <h2>Weekly Activity Calendar</h2>
                <div class="week-grid">
                    {''.join([f'''
                    <div class="week-card">
                        <strong>Year {int(r.Year)} Week {int(r.Week)}</strong><br>
                        Trades: {int(r.Trade_Count)}<br>
                        P&L: <span class="{'pos' if r.Weekly_Profit >= 0 else 'neg'}">${r.Weekly_Profit:.2f}</span>
                    </div>
                    ''' for _, r in weekly_stats.iterrows()])}
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(output_html, "w") as f:
            f.write(html_template)
            
        print(f"Success! Analysis generated in: {output_html}")

    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    # Ensure your CSV file is named 'trading_history.csv' or change the name below
    analyze_trades("fusion-markets-order-history-all-2026-02-20T13_42_53.497Z_d4381.csv")
