#!/usr/bin/env python3
"""
Quick web-based data viewer for SF urban data
Better than pgAdmin, shows spatial data nicely
"""

import psycopg2
import json
from flask import Flask, render_template_string, jsonify
import sys

app = Flask(__name__)

# Simple HTML template with Tailwind CSS for beautiful styling
VIEWER_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Urban-Infra Data Viewer</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
</head>
<body class="bg-gray-100">
    <div class="container mx-auto p-6">
        <h1 class="text-3xl font-bold text-gray-800 mb-6">🏙️ Urban-Infra SF Data</h1>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {% for neighborhood in neighborhoods %}
            <div class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
                <h3 class="text-xl font-semibold text-blue-600 mb-2">{{ neighborhood.name }}</h3>
                <div class="space-y-2">
                    <p class="text-sm"><span class="font-medium">Type:</span> {{ neighborhood.area_type }}</p>
                    <p class="text-sm"><span class="font-medium">Zoning:</span> 
                        <span class="bg-blue-100 px-2 py-1 rounded text-blue-800">
                            {{ neighborhood.data.zoning }}
                        </span>
                    </p>
                    <p class="text-sm"><span class="font-medium">Transit:</span> {{ neighborhood.data.transit_access }}</p>
                    
                    <div class="flex flex-wrap gap-1 mt-2">
                        {% for char in neighborhood.data.characteristics %}
                        <span class="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">{{ char }}</span>
                        {% endfor %}
                    </div>
                    
                    {% if neighborhood.data.flood_risk %}
                    <p class="text-sm text-red-600"><span class="font-medium">⚠️ Flood Risk:</span> {{ neighborhood.data.flood_risk }}</p>
                    {% endif %}
                    
                    {% if neighborhood.data.displacement_risk %}
                    <p class="text-sm text-orange-600"><span class="font-medium">📊 Displacement Risk:</span> {{ neighborhood.data.displacement_risk }}</p>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
        
        <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-2xl font-semibold mb-4">📊 Data Summary</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="text-center">
                    <div class="text-3xl font-bold text-blue-600">{{ neighborhoods|length }}</div>
                    <div class="text-gray-600">Neighborhoods</div>
                </div>
                <div class="text-center">
                    <div class="text-3xl font-bold text-green-600">{{ zoning_types|length }}</div>
                    <div class="text-gray-600">Zoning Types</div>
                </div>
                <div class="text-center">
                    <div class="text-3xl font-bold text-purple-600">3</div>
                    <div class="text-gray-600">Transit Levels</div>
                </div>
            </div>
        </div>
        
        <div class="mt-6 bg-white rounded-lg shadow-md p-6">
            <h2 class="text-2xl font-semibold mb-4">🗺️ Next: Add Real Spatial Data</h2>
            <p class="text-gray-600 mb-4">Ready to load actual SF parcels, zoning boundaries, and transit data from SF Open Data Portal.</p>
            <button class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors">
                Load Real SF Data →
            </button>
        </div>
    </div>
</body>
</html>
"""

def get_neighborhoods():
    """Get neighborhood data from database"""
    try:
        conn = psycopg2.connect(
            host="localhost", port=5434, database="urban_infra",
            user="postgres", password="password"
        )
        
        with conn.cursor() as cur:
            cur.execute("SELECT name, area_type, data FROM sf_neighborhoods;")
            rows = cur.fetchall()
            
            neighborhoods = []
            zoning_types = set()
            
            for name, area_type, data in rows:
                neighborhoods.append({
                    'name': name,
                    'area_type': area_type,
                    'data': data
                })
                if 'zoning' in data:
                    zoning_types.add(data['zoning'])
        
        conn.close()
        return neighborhoods, list(zoning_types)
        
    except Exception as e:
        print(f"Database error: {e}")
        return [], []

@app.route('/')
def view_data():
    neighborhoods, zoning_types = get_neighborhoods()
    return render_template_string(
        VIEWER_TEMPLATE, 
        neighborhoods=neighborhoods, 
        zoning_types=zoning_types
    )

@app.route('/api/neighborhoods')
def api_neighborhoods():
    neighborhoods, _ = get_neighborhoods()
    return jsonify(neighborhoods)

if __name__ == "__main__":
    print("🚀 Starting Urban-Infra Data Viewer...")
    print("📍 Visit: http://localhost:5001")
    print("💾 Viewing SF neighborhoods from PostGIS database")
    
    try:
        app.run(host='0.0.0.0', port=5001, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Data viewer stopped")