from flask import Flask, render_template

app = Flask(__name__)

reports = [
    {
        "issue": "Air Pollution",
        "location": "Kodagu",
        "description": "Industrial smoke stack emission levels exceeding AQI boundaries near NH275.",
        "risk_score": 92,
        "status": "Critical",
        "time": "2 mins ago",
        "img": "https://images.unsplash.com/photo-1532601224476-15c79f2f7a51?auto=format&fit=crop&q=80&w=60"
    },
    {
        "issue": "Garbage Dumping",
        "location": "Kodagu",
        "description": "Uncontrolled plastic waste build-up along the Cauvery river bank near the main ghat.",
        "risk_score": 82,
        "status": "High",
        "time": "15 mins ago",
        "img": "https://images.unsplash.com/photo-1611284446314-60a58ac0deb9?auto=format&fit=crop&q=80&w=60"
    },
    {
        "issue": "Water Contamination",
        "location": "Kodagu",
        "description": "Chemical runoff observed near southwestern drainage outlets of the Harangi reservoir.",
        "risk_score": 68,
        "status": "Medium",
        "time": "1 hour ago",
        "img": "https://images.unsplash.com/photo-1518837695005-2083093ee35b?auto=format&fit=crop&q=80&w=60"
    }
]

@app.route("/")
def home():
    return render_template("index.html", reports=reports)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)