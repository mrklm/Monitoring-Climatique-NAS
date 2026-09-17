import json
import os

# Le script génère les fichiers dans le dossier courant pour être universel
BASE_DIR = './'

THEMES = {
    "[Sombre] Midnight Garage": {"BG": "#151515", "PANEL": "#1F1F1F", "FG": "#EAEAEA", "ACCENT": "#FF9800"},
    "[Sombre] AIR-KLM Night flight": {"BG": "#0B1E2D", "PANEL": "#102A3D", "FG": "#EAF6FF", "ACCENT": "#00A1DE"},
    "[Sombre] Café Serré": {"BG": "#1B120C", "PANEL": "#2A1C14", "FG": "#F2E6D8", "ACCENT": "#C28E5C"},
    "[Sombre] Matrix Déjà Vu": {"BG": "#000A00", "PANEL": "#001F00", "FG": "#00FF66", "ACCENT": "#00FF00"},
    "[Sombre] Miami Vice 1987": {"BG": "#14002E", "PANEL": "#2B0057", "FG": "#FFF0FF", "ACCENT": "#00FFD5"},
    "[Sombre] Cyber Licorne": {"BG": "#1A0026", "PANEL": "#2E004F", "FG": "#F6E7FF", "ACCENT": "#FF2CF7"},
    "[Clair] AIR-KLM Day flight": {"BG": "#EAF6FF", "PANEL": "#D6EEF9", "FG": "#0B2A3F", "ACCENT": "#00A1DE"},
    "[Clair] Matin Brumeux": {"BG": "#E6E7E8", "PANEL": "#D4D7DB", "FG": "#1E1F22", "ACCENT": "#6B7C93"},
    "[Clair] Latte Vanille": {"BG": "#FAF6F1", "PANEL": "#EFE6DC", "FG": "#3D2E22", "ACCENT": "#D8B892"},
    "[Clair] Miellerie La Divette": {"BG": "#E6B65C", "PANEL": "#F5E6CC", "FG": "#50371A", "ACCENT": "#F2B705"},
    "[Pouêt] Chewing-gum Océan": {"BG": "#00A6C8", "PANEL": "#0083A1", "FG": "#082026", "ACCENT": "#FF4FD8"},
    "[Pouêt] Pamplemousse": {"BG": "#FF4A1C", "PANEL": "#E63B10", "FG": "#1A0B00", "ACCENT": "#00E5FF"},
    "[Pouêt] Raisin Toxique": {"BG": "#7A00FF", "PANEL": "#5B00C9", "FG": "#0F001A", "ACCENT": "#39FF14"},
    "[Pouêt] Citron qui pique": {"BG": "#FFF200", "PANEL": "#E6D800", "FG": "#1A1A00", "ACCENT": "#0066FF"},
    "[Pouêt] Barbie Apocalypse": {"BG": "#FF1493", "PANEL": "#004D40", "FG": "#E8FFF8", "ACCENT": "#FFEB3B"},
    "[Pouêt] Compagnie Créole": {"BG": "#8B3A1A", "PANEL": "#F2C94C", "FG": "#5A2E0C", "ACCENT": "#8B3A1A"}
}

HTML_CONTENT = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Monitoring NAS</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root { --bg: #f5f5f5; --panel: #ffffff; --fg: #333333; --accent: #007bff; }
        body { background-color: var(--bg); color: var(--fg); font-family: Arial, sans-serif; margin: 20px; transition: all 0.3s ease; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .stats { display: flex; justify-content: space-around; margin-bottom: 20px; }
        .card { background-color: var(--panel); padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; flex: 1; margin: 0 10px; transition: all 0.3s; border: 2px solid transparent; }
        .card.alert { border-color: #FF0000; animation: pulse 1.5s infinite; }
        .card h2 { margin: 0; font-size: 2.5em; color: var(--accent); }
        .alert-text { color: #FF0000; font-weight: bold; margin-top: 10px; font-size: 1.1em; display: none; }
        .chart-container { background-color: var(--panel); padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: all 0.3s; }
        select { padding: 8px; border-radius: 4px; border: 1px solid var(--fg); background: var(--panel); color: var(--fg); font-size: 1em; cursor: pointer; }
        @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(255,0,0,0.7); } 70% { box-shadow: 0 0 0 10px rgba(255,0,0,0); } 100% { box-shadow: 0 0 0 0 rgba(255,0,0,0); } }
    </style>
</head>
<body>
    <div class="header">
        <h1>Monitoring Climatique NAS</h1>
        <select id="themeSelector"></select>
    </div>
    <div class="stats">
        <div class="card"><h2 id="temp">--</h2><p>Température (°C)</p></div>
        <div class="card" id="humCard"><h2 id="hum">--</h2><p>Humidité (%)</p></div>
    </div>
    <p class="alert-text" id="alertMsg">⚠️ Attention : Humidité importante !</p>
    <div class="chart-container"><canvas id="myChart"></canvas></div>

    <script>
        const THEMES = """ + json.dumps(THEMES) + """;
        const HUMIDITY_THRESHOLD = 80;
        let chart;
        function applyTheme(themeName) { const t = THEMES[themeName]; if (!t) return; document.documentElement.style.setProperty('--bg', t.BG); document.documentElement.style.setProperty('--panel', t.PANEL); document.documentElement.style.setProperty('--fg', t.FG); document.documentElement.style.setProperty('--accent', t.ACCENT); if (chart) { chart.data.datasets[0].borderColor = t.ACCENT; chart.data.datasets[1].borderColor = t.FG; chart.update(); } }
        function initThemes() { const selector = document.getElementById('themeSelector'); const keys = Object.keys(THEMES); keys.forEach(k => { let opt = document.createElement('option'); opt.value = k; opt.innerText = k; selector.appendChild(opt); }); const randomTheme = keys[Math.floor(Math.random() * keys.length)]; selector.value = randomTheme; applyTheme(randomTheme); selector.addEventListener('change', (e) => applyTheme(e.target.value)); }
        function checkAlert(hum) { const card = document.getElementById('humCard'); const msg = document.getElementById('alertMsg'); if (hum > HUMIDITY_THRESHOLD) { card.classList.add('alert'); msg.style.display = 'block'; } else { card.classList.remove('alert'); msg.style.display = 'none'; } }
        async function updateData() { let res = await fetch('/api'); let data = await res.json(); if (data.length > 0) { let last = data[data.length - 1]; document.getElementById('temp').innerText = last.temp + ' °C'; document.getElementById('hum').innerText = last.hum + ' %'; checkAlert(parseFloat(last.hum)); let labels = data.map(d => d.time.split(' ')[1]); let temps = data.map(d => parseFloat(d.temp)); let hums = data.map(d => parseFloat(d.hum)); if (chart) { chart.data.labels = labels; chart.data.datasets[0].data = temps; chart.data.datasets[1].data = hums; chart.update(); } else { let ctx = document.getElementById('myChart').getContext('2d'); chart = new Chart(ctx, { type: 'line', data: { labels: labels, datasets: [{ label: 'Température (°C)', data: temps, borderColor: 'var(--accent)', backgroundColor: 'rgba(0,0,0,0)', yAxisID: 'y', tension: 0.3, pointRadius: 3 }, { label: 'Humidité (%)', data: hums, borderColor: 'var(--fg)', backgroundColor: 'rgba(0,0,0,0)', yAxisID: 'y1', tension: 0.3, pointRadius: 3 }]}, options: { responsive: true, interaction: { mode: 'index', intersect: false }, scales: { y: { type: 'linear', display: true, position: 'left', min: 15, max: 35, title: { display: true, text: 'Temp (°C)', color: 'var(--fg)' }, ticks: { color: 'var(--fg)' } }, y1: { type: 'linear', display: true, position: 'right', min: 20, max: 80, title: { display: true, text: 'Hum (%)', color: 'var(--fg)' }, grid: { drawOnChartArea: false }, ticks: { color: 'var(--fg)' } }, x: { ticks: { color: 'var(--fg)', maxRotation: 45 } } } } }); } } }
        initThemes(); updateData(); setInterval(updateData, 5000);
    </script>
</body>
</html>"""

PYTHON_CONTENT = """from flask import Flask, jsonify, send_file
import csv
app = Flask(__name__)
# Le script cherche le fichier CSV dans le même dossier que lui
CSV_FILE = './climat.csv'
@app.route('/')
def index(): return send_file('index.html')
@app.route('/api')
def api():
    data = []
    try:
        with open(CSV_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader: data.append({'time': row['Date et Heure'], 'temp': row['Temperature_C'], 'hum': row['Humidite_Pct']})
    except Exception as e: print('Error:', e)
    return jsonify(data[-30:])
if __name__ == '__main__': app.run(host='0.0.0.0', port=5000)
"""

with open(BASE_DIR + 'index.html', 'w') as f: f.write(HTML_CONTENT)
with open(BASE_DIR + 'dashboard.py', 'w') as f: f.write(PYTHON_CONTENT)
print("✅ Dashboard et thèmes générés avec succès dans le dossier courant !")
