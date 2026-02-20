import pandas as pd
import numpy as np
import argparse
import sys
import os

def generate_analysis(input_csv, output_html):
    try:
        # 1. Load the CSV
        if not os.path.exists(input_csv):
            print(f"Error: File '{input_csv}' not found.")
            return

        df = pd.read_csv(input_csv)
        
        # 2. Data Preprocessing
        # Filter for executed trades with profit data and exclude XAGUSD
        trades = df[df['Profit'].notnull()].copy()
        trades = trades[trades['Symbol'] != 'XAGUSD']
        
        if trades.empty:
            print("No valid trade data found after filtering.")
            return

        # Calculate Net Profit
        trades['Update Time'] = pd.to_datetime(trades['Update Time'])
        trades['Commission'] = trades['Commission'].fillna(0)
        trades['Net Profit'] = trades['Profit'] + trades['Commission']
        
        # 3. Metrics Calculation
        total_trades = len(trades)
        avg_pl = trades['Net Profit'].mean()
        wins = trades[trades['Net Profit'] > 0]
        losses = trades[trades['Net Profit'] <= 0]
        winrate = (len(wins) / total_trades * 100) if total_trades > 0 else 0
        
        gross_profit = wins['Net Profit'].sum()
        gross_loss = abs(losses['Net Profit'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss != 0 else np.inf
        
        max_profit = trades['Net Profit'].max()
        max_loss = trades['Net Profit'].min()
        
        # 4. Weekly Aggregation
        trades['Year'] = trades['Update Time'].dt.year
        trades['Week'] = trades['Update Time'].dt.isocalendar().week
        weekly_stats = trades.groupby(['Year', 'Week']).agg(
            Trade_Count=('Net Profit', 'count'),
            Weekly_Profit=('Net Profit', 'sum')
        ).reset_index().sort_values(['Year', 'Week'], ascending=False)

        # 5. Build HTML Report
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Trading Performance Report</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 30px; background-color: #f4f7f6; }}
                .container {{ max-width: 1100px; margin: auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
                h1 {{ color: #2c3e50; text-align: center; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                .kpi-wrapper {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 30px 0; }}
                .kpi-card {{ background: #fff; border: 1px solid #e1e4e8; padding: 20px; border-radius: 10px; text-align: center; transition: transform 0.2s; }}
                .kpi-card:hover {{ transform: translateY(-5px); box-shadow: 0 5px 15px rgba(0,0,0,0.05); }}
                .kpi-card h3 {{ margin: 0; color: #7f8c8d; font-size: 0.85rem; text-transform: uppercase; }}
                .kpi-card p {{ margin: 10px 0 0; font-size: 1.6rem; font-weight: bold; color: #2c3e50; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ padding: 15px; text-align: left; border-bottom: 1px solid #edf2f7; }}
                th {{ background-color: #f8fafc; color: #4a5568; }}
                .win {{ color: #2f855a; font-weight: bold; }}
                .loss {{ color: #c53030; font-weight: bold; }}
                .calendar {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }}
                .week-box {{ background: #fff; padding: 15px; border-radius: 8px; border-left: 5px solid #3498db; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Execution Analysis: {os.path.basename(input_csv)}</h1>
                
                <div class="kpi-wrapper">
                    <div class="kpi-card"><h3>Trades Executed</h3><p>{total_trades}</p></div>
                    <div class="kpi-card"><h3>Average P&L</h3><p>${avg_pl:.2f}</p></div>
                    <div class="kpi-card"><h3>Winrate</h3><p>{winrate:.2f}%</p></div>
                    <div class="kpi-card"><h3>Profit Factor</h3><p>{profit_factor:.2f}</p></div>
                </div>

                <h2>Summary Statistics</h2>
                <table>
                    <tr><td>Total Number of Trades</td><td>{total_trades}</td></tr>
                    <tr><td>Highest Profitable Trade</td><td class="win">${max_profit:.2f}</td></tr>
                    <tr><td>Highest Loss</td><td class="loss">${max_loss:.2f}</td></tr>
                </table>

                <h2>Weekly Execution Calendar</h2>
                <div class="calendar">
                    {''.join([f'''
                    <div class="week-box">
                        <strong>Week {int(r.Week)}, {int(r.Year)}</strong><br>
                        Trades: {int(r.Trade_Count)}<br>
                        Net P&L: <span class="{'win' if r.Weekly_Profit >= 0 else 'loss'}">${r.Weekly_Profit:.2f}</span>
                    </div>
                    ''' for _, r in weekly_stats.iterrows()])}
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(output_html, "w") as f:
            f.write(html_content)
            
        print(f"Analysis complete. Dashboard saved to: {output_html}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate an HTML trade analysis report from a CSV file.")
    parser.add_argument("input", help="Path to the input CSV file")
    parser.add_argument("-o", "--output", default="analysis_report.html", help="Path for the output HTML file (default: analysis_report.html)")
    
    args = parser.parse_args()
    generate_analysis(args.input, args.output)