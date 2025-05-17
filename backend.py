from flask import Flask, jsonify, send_from_directory, render_template
from flask_cors import CORS
import pandas as pd
import os
import numpy as np
from datetime import datetime

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for all routes and origins

# Define the path to your CSV file
data_path = os.path.join(os.path.dirname(__file__), 'data', 'indian_energy_data.csv')

# Load data once at startup
def load_data():
    try:
        df = pd.read_csv(data_path)
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        # Convert numeric columns to float
        df['consumption'] = df['consumption'].astype(float)
        return df
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return None

# Load data at startup
df = load_data()

@app.route('/')
def home():
    return send_from_directory('frontend', 'index.html')

@app.route('/pages/<path:path>')
def serve_page(path):
    return send_from_directory('frontend/pages', path)

@app.route('/api/consumption')
def get_consumption():
    try:
        if df is None:
            return jsonify({"error": "Data not loaded"}), 500
            
        # Convert timestamp to string for JSON serialization
        result_df = df.copy()
        result_df['timestamp'] = result_df['timestamp'].astype(str)
        
        return jsonify(result_df.to_dict('records'))
    except Exception as e:
        print(f"Error: {str(e)}")  # Log the error on the server
        return jsonify({"error": str(e)}), 500

@app.route('/api/daily-average')
def get_daily_average():
    try:
        if df is None:
            return jsonify({"error": "Data not loaded"}), 500
            
        # Calculate daily average consumption
        daily_avg = df.groupby(df['timestamp'].dt.date)['consumption'].mean().reset_index()
        daily_avg['timestamp'] = daily_avg['timestamp'].astype(str)
        
        return jsonify(daily_avg.to_dict('records'))
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/appliance-usage')
def get_appliance_usage():
    try:
        if df is None:
            return jsonify({"error": "Data not loaded"}), 500
            
        # Extract individual appliances
        all_appliances = []
        for appliances in df['appliance'].dropna():
            all_appliances.extend([app.strip() for app in appliances.split(',')])
        
        # Count occurrences of each appliance
        appliance_counts = pd.Series(all_appliances).value_counts().reset_index()
        appliance_counts.columns = ['appliance', 'count']
        
        # Calculate average consumption per appliance
        appliance_consumption = {}
        for idx, row in df.iterrows():
            if pd.notna(row['appliance']):
                appliances = [app.strip() for app in row['appliance'].split(',')]
                for app in appliances:
                    if app not in appliance_consumption:
                        appliance_consumption[app] = []
                    appliance_consumption[app].append(row['consumption'])
        
        # Calculate average consumption for each appliance
        appliance_avg_consumption = {app: np.mean(consumptions) for app, consumptions in appliance_consumption.items()}
        
        # Add average consumption to the dataframe
        appliance_counts['avg_consumption'] = appliance_counts['appliance'].map(appliance_avg_consumption)
        
        # Sort by average consumption (highest to lowest)
        appliance_counts = appliance_counts.sort_values('avg_consumption', ascending=False)
        
        return jsonify(appliance_counts.to_dict('records'))
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/energy-saving-tips')
def get_energy_saving_tips():
    try:
        if df is None:
            return jsonify({"error": "Data not loaded"}), 500
            
        # Get the top 3 appliances by consumption
        all_appliances = []
        for appliances in df['appliance'].dropna():
            all_appliances.extend([app.strip() for app in appliances.split(',')])
        
        appliance_counts = pd.Series(all_appliances).value_counts().reset_index()
        appliance_counts.columns = ['appliance', 'count']
        
        appliance_consumption = {}
        for idx, row in df.iterrows():
            if pd.notna(row['appliance']):
                appliances = [app.strip() for app in row['appliance'].split(',')]
                for app in appliances:
                    if app not in appliance_consumption:
                        appliance_consumption[app] = []
                    appliance_consumption[app].append(row['consumption'])
        
        appliance_avg_consumption = {app: np.mean(consumptions) for app, consumptions in appliance_consumption.items()}
        appliance_counts['avg_consumption'] = appliance_counts['appliance'].map(appliance_avg_consumption)
        appliance_counts = appliance_counts.sort_values('avg_consumption', ascending=False)
        
        top_appliances = appliance_counts.head(3)['appliance'].tolist()
        
        # Generate energy saving tips based on the top appliances
        tips = {
            "AC": [
                "Set your thermostat to 24-26°C for optimal comfort and energy savings",
                "Clean or replace air filters regularly to improve efficiency",
                "Use ceiling fans to help circulate cool air and reduce AC workload",
                "Close curtains or blinds during the hottest part of the day"
            ],
            "Fridge": [
                "Keep your refrigerator temperature between 2-4°C and freezer at -18°C",
                "Ensure the door seals are clean and tight",
                "Don't leave the door open longer than necessary",
                "Defrost your freezer regularly if it's not frost-free"
            ],
            "Geyser": [
                "Set your water heater temperature to 50°C instead of 60°C",
                "Install a timer to heat water only when needed",
                "Take shorter showers to reduce hot water usage",
                "Fix any leaking hot water taps immediately"
            ],
            "TV": [
                "Use the energy-saving mode on your TV",
                "Turn off the TV when not in use (not just standby mode)",
                "Reduce screen brightness to save energy",
                "Consider using a smart power strip to cut power when not in use"
            ],
            "Computer": [
                "Enable sleep mode after 10-15 minutes of inactivity",
                "Turn off your computer when not in use",
                "Use a laptop instead of a desktop when possible",
                "Unplug chargers when not in use"
            ],
            "Washing Machine": [
                "Wash clothes in cold water when possible",
                "Run full loads instead of partial loads",
                "Use the appropriate water level for the load size",
                "Clean the lint filter regularly"
            ],
            "Oven": [
                "Preheat the oven only when necessary",
                "Use the microwave for small meals instead of the oven",
                "Keep the oven door closed while cooking",
                "Clean the oven regularly to maintain efficiency"
            ]
        }
        
        # Get tips for the top appliances
        appliance_tips = {}
        for app in top_appliances:
            if app in tips:
                appliance_tips[app] = tips[app]
            else:
                appliance_tips[app] = [
                    "Turn off when not in use",
                    "Maintain and clean regularly",
                    "Use energy-efficient settings",
                    "Consider upgrading to a more energy-efficient model"
                ]
        
        return jsonify({
            "top_appliances": top_appliances,
            "tips": appliance_tips
        })
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/predict-consumption')
def predict_consumption():
    try:
        if df is None:
            return jsonify({"error": "Data not loaded"}), 500
            
        # Get prediction for next hour
        prediction = predictor.predict(df)
        
        return jsonify({
            "prediction": float(prediction),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/model-performance')
def get_model_performance():
    try:
        if df is None:
            return jsonify({"error": "Data not loaded"}), 500
            
        # Evaluate model performance
        loss = predictor.evaluate(df)
        
        return jsonify({
            "loss": float(loss),
            "model_type": "LSTM Neural Network",
            "sequence_length": predictor.sequence_length
        })
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
