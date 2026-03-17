import os
from flask import Flask, render_template_string, request

app = Flask(__name__)

# -----------------------------
# Appliances
# -----------------------------
APPLIANCES = {
    "light": {"label": "💡 Light", "watts": 10},
    "fan": {"label": "🌀 Fan", "watts": 75},
    "ac": {"label": "❄️ AC", "watts": 1500},
    "refrigerator": {"label": "🧊 Fridge", "watts": 200},
    "tv": {"label": "📺 TV", "watts": 100},
    "washing_machine": {"label": "🫧 Washing Machine", "watts": 500},
    "custom": {"label": "🔧 Custom", "watts": 0},
}

# -----------------------------
# Billing
# -----------------------------
def calculate_tneb_bill(units):
    bill = 0

    slab1 = min(units, 100)
    units -= slab1

    if units > 0:
        s = min(units, 100)
        bill += s * 1.5
        units -= s

    if units > 0:
        s = min(units, 300)
        bill += s * 3
        units -= s

    if units > 0:
        bill += units * 5

    fixed = 30
    return bill, fixed, bill + fixed


# -----------------------------
# UI
# -----------------------------
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>⚡ Smart EB Calculator</title>

<style>
body {
    font-family: 'Segoe UI';
    background: linear-gradient(135deg,#0f0c29,#302b63);
    color:white;
    margin:0;
}

/* HEADER */
.header {
    text-align:center;
    padding:20px;
}

/* GRID */
.grid {
    display:grid;
    grid-template-columns: repeat(auto-fit,minmax(250px,1fr));
    gap:15px;
    padding:20px;
}

/* CARD */
.card {
    background: rgba(255,255,255,0.08);
    padding:15px;
    border-radius:15px;
    transition:0.3s;
}

/* TOGGLE SWITCH */
.switch {
    float:right;
}

input[type=checkbox] {
    transform: scale(1.3);
}

/* INPUT BOX */
.inputs {
    margin-top:10px;
    display:none;
}

.inputs input {
    width:100%;
    padding:8px;
    margin:5px 0;
    border-radius:8px;
    border:none;
}

/* ACTIVE */
.card.active {
    border:2px solid #a78bfa;
}

/* BUTTON */
button {
    display:block;
    margin:20px auto;
    padding:12px;
    width:90%;
    border:none;
    border-radius:10px;
    background:linear-gradient(135deg,#a78bfa,#60a5fa);
    font-weight:bold;
    cursor:pointer;
}

/* RESULT */
.result {
    background: rgba(255,255,255,0.08);
    margin:20px;
    padding:20px;
    border-radius:15px;
}
</style>
</head>

<body>

<div class="header">
<h1>⚡ Smart Electricity Calculator</h1>
<p>Select appliances & calculate usage</p>
</div>

<form method="POST">

<div class="grid">

{% for key,data in appliances.items() %}
<div class="card" id="card_{{key}}">

    <label>
        <input type="checkbox" name="appliance" value="{{key}}" onchange="toggleBox('{{key}}', this)">
        <b>{{data.label}}</b>
    </label>

    <div class="inputs" id="box_{{key}}">
        Qty:
        <input type="number" name="qty_{{key}}" value="1" min="1">

        Hours/day:
        <input type="number" step="0.1" name="hrs_{{key}}" value="1">

        Watts:
        <input type="number" name="watts_{{key}}" value="{{data.watts}}">
    </div>

</div>
{% endfor %}

</div>

<button>⚡ Calculate</button>

</form>

{% if result %}
<div class="result">

<h2>⚡ Usage</h2>
<p>Daily: {{result.daily}} kWh</p>
<p>Monthly: {{result.monthly}} kWh</p>
<p>Yearly: {{result.yearly}} kWh</p>

<h3>📊 Breakdown</h3>
<ul>
{% for b in result.breakdown %}
<li>{{b}}</li>
{% endfor %}
</ul>

<h3>💰 Bill</h3>
<p>Energy: ₹ {{result.energy}}</p>
<p>Fixed: ₹ {{result.fixed}}</p>
<h2>Total: ₹ {{result.total}}</h2>

</div>
{% endif %}

<script>
function toggleBox(id, el){
    let box = document.getElementById("box_"+id);
    let card = document.getElementById("card_"+id);

    if(el.checked){
        box.style.display = "block";
        card.classList.add("active");
    } else {
        box.style.display = "none";
        card.classList.remove("active");
    }
}
</script>

</body>
</html>
"""

# -----------------------------
# Route
# -----------------------------
@app.route("/", methods=["GET","POST"])
def index():

    result = None

    if request.method == "POST":
        selected = request.form.getlist("appliance")

        total_daily = 0
        breakdown = []

        for app_name in selected:
            qty = float(request.form.get(f"qty_{app_name}", 1))
            hrs = float(request.form.get(f"hrs_{app_name}", 1))
            watts = float(request.form.get(
                f"watts_{app_name}",
                APPLIANCES[app_name]["watts"]
            ))

            kwh = (watts * hrs * qty) / 1000
            total_daily += kwh

            breakdown.append(f"{APPLIANCES[app_name]['label']} → {kwh:.2f} kWh/day")

        monthly = total_daily * 30
        yearly = total_daily * 365

        energy, fixed, total = calculate_tneb_bill(monthly)

        result = {
            "daily": round(total_daily,2),
            "monthly": round(monthly,1),
            "yearly": round(yearly,0),
            "breakdown": breakdown,
            "energy": round(energy,2),
            "fixed": fixed,
            "total": round(total,2)
        }

    return render_template_string(HTML, appliances=APPLIANCES, result=result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)