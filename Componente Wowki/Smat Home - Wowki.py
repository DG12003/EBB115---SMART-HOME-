import dash
from dash import dcc, html, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import paho.mqtt.client as mqtt
import plotly.graph_objs as go
from datetime import datetime
import json

# MQTT config
BROKER = "broker.mqttdashboard.com"
PORT = 1883
TOPIC_SENSORES = "home/dashboard/sensores"
TOPIC_LED1 = "home/dashboard/led1"
TOPIC_LED2 = "home/dashboard/led2"
TOPIC_SERVO1 = "home/dashboard/servo1"
TOPIC_SERVO2 = "home/dashboard/servo2"
TOPIC_STEPPER1 = "home/dashboard/stepper1"
TOPIC_STEPPER2 = "home/dashboard/stepper2"

# Datos actuales
sensor_data = {"temp": "---", "hum": "---", "gas": "---", "dist": "---", "luz": "---", "pir": "---"}

# Historial de datos
tiempos = []
temperaturas = []
humedades = []
gases = []
luces = []
distancias = []
movimientos = []

# MQTT
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
        ahora = datetime.now().strftime("%H:%M:%S")
        sensor_data.update(data)
        tiempos.append(ahora)
        temperaturas.append(float(data.get("temp", 0)))
        humedades.append(float(data.get("hum", 0)))
        gases.append(int(data.get("gas", 0)))
        luces.append(float(data.get("luz", 0)))
        distancias.append(float(data.get("dist", 0)))
        if str(data.get("pir", "0")) == "1":
            movimientos.append(ahora)
    except Exception as e:
        print(f"Error al procesar mensaje MQTT: {e}")

mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect(BROKER, PORT)
mqtt_client.subscribe(TOPIC_SENSORES)
mqtt_client.loop_start()

# App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])
app.title = "Dashboard IoT"

app.layout = dbc.Container([
    html.H1("Proyecto de domótica con IoT y MQTT", style={"backgroundColor": "#CDBE84", "color": "black", "fontSize": "36px", "textAlign": "center"}),

    dbc.Alert("¡PELIGRO!: Nivel de gas elevado...", id="alerta-gas", color="danger", is_open=False),
    html.Div(id="estado-ventiladores", className="text-success fw-bold mb-3"),

    dbc.Row([
        dbc.Col(html.Div([
            html.H4("Temperatura: ", style={"color": "black"}),
            html.H3(id="temp", style={"color": "black"})
        ]), width=2),

        dbc.Col(html.Div([
            html.H4("Humedad: ", style={"color": "black"}),
            html.H3(id="hum", style={"color": "black"})
        ]), width=2),

        dbc.Col(html.Div([
            html.H4("Sensor de gas: ", style={"color": "black"}),
            html.H3(id="gas", style={"color": "black"})
        ]), width=2),

        dbc.Col(html.Div([
            html.H4("Distancia: ", style={"color": "black"}),
            html.H3(id="dist", style={"color": "black"})
        ]), width=2),

        dbc.Col(html.Div([
            html.H4("Iluminación: ", style={"color": "black"}),
            html.H3(id="luz", style={"color": "black"})
        ]), width=2),

        dbc.Col(html.Div([
            html.H4("Sensor PIR: ", style={"color": "black"}),
            html.H3(id="pir", style={"color": "black"})
        ]), width=2),
    ]),

    html.Hr(),
    
        dbc.Row([
        dbc.Col(html.H5("Vista de gráficos 📊", style={"backgroundColor": "#CDBE84", "color": "black", "fontSize": "24px", "textAlign": "center"}), width=12)
    ], className="text-center mt-3"),

    dbc.ButtonGroup([
        dbc.Button("Temperatura", id="btn-temp", style={"backgroundColor": "#d2b48c", "color": "black"}),
        dbc.Button("Humedad", id="btn-hum", style={"backgroundColor": "#d2b48c", "color": "black"}),
        dbc.Button("Gas", id="btn-gas", style={"backgroundColor": "#d2b48c", "color": "black"}),
        dbc.Button("Luz", id="btn-luz", style={"backgroundColor": "#d2b48c", "color": "black"}),
        dbc.Button("Ultrasónico", id="btn-dist", style={"backgroundColor": "#d2b48c", "color": "black"}),
        dbc.Button("Movimiento PIR", id="btn-pir", style={"backgroundColor": "#d2b48c", "color": "black"}),
    ], className="d-flex justify-content-center mb-4"),

    html.Div(id="graficas-dinamicas"),

    dbc.Row([
        dbc.Col(dbc.Button("Encender Foco 1", id="btn-foco1-on", n_clicks=0, style={"backgroundColor": "#3b93ff", "color": "black"}), width=3),
        dbc.Col(dbc.Button("Apagar Foco 1", id="btn-foco1-off", n_clicks=0, style={"backgroundColor": "#97a4b3", "color": "black"}), width=3),
        dbc.Col(dbc.Button("Encender Foco 2", id="btn-foco2-on", n_clicks=0, style={"backgroundColor": "#3b93ff", "color": "black"}), width=3),
        dbc.Col(dbc.Button("Apagar Foco 2", id="btn-foco2-off", n_clicks=0, style={"backgroundColor": "#97a4b3", "color": "black"}), width=3),
    ], className="my-3"),

    dbc.Row([
        dbc.Col(html.H5("Control de puertas", style={"backgroundColor": "#61F39C", "color": "black", "fontSize": "24px", "textAlign": "center"}), width=12)
    ], className="text-center mt-3"),

    dbc.Row([
        dbc.Col(dbc.Button("Abrir Puerta 1", id="cerrar1", n_clicks=0, style={"backgroundColor": "#97a4b3", "color": "black"}), width=2),
        dbc.Col(dbc.Button("Cerrar Puerta 1", id="abrir1", n_clicks=0, style={"backgroundColor": "#3b93ff", "color": "black"}), width=2),
        dbc.Col(dbc.Button("Abrir Puerta 2", id="cerrar2", n_clicks=0, style={"backgroundColor": "#97a4b3", "color": "black"}), width=2),
        dbc.Col(dbc.Button("Cerrar Puerta 2", id="abrir2", n_clicks=0, style={"backgroundColor": "#3b93ff", "color": "black"}), width=2),
    ], className="my-3"),

    dbc.Row([
        dbc.Col(html.H5("Control de ventiladores", style={"backgroundColor": "#61F39C", "color": "black", "fontSize": "24px", "textAlign": "center"}), width=12)
    ], className="text-center mt-3"),

    dbc.Row([
        dbc.Col(dbc.Button("Encender Ventilador 1", id="btn-step1", n_clicks=0, style={"backgroundColor": "#3b93ff", "color": "black"}), width=4),
        dbc.Col(dbc.Button("Encender Ventilador 2", id="btn-step2", n_clicks=0, style={"backgroundColor": "#3b93ff", "color": "black"}), width=4),
    ], className="my-3"),

    dcc.Interval(id="actualizar", interval=4000, n_intervals=0),
    dcc.Interval(id="interval", interval=4000, n_intervals=0),
], fluid=True, style={
    "backgroundColor": "#c4f4e0",
    "minHeight": "100vh",
    "paddingBottom": "30px"
})

@app.callback(
    Output("temp", "children"),
    Output("hum", "children"),
    Output("gas", "children"),
    Output("dist", "children"),
    Output("luz", "children"),
    Output("pir", "children"),
    Output("alerta-gas", "is_open"),
    Output("estado-ventiladores", "children"),
    Input("interval", "n_intervals")
)
def update_sensores(_):
    now = datetime.now().strftime("%H:%M:%S")
    tiempos.append(now)

    try: temperaturas.append(float(sensor_data.get("temp", 0)))
    except: temperaturas.append(0)

    try: humedades.append(float(sensor_data.get("hum", 0)))
    except: humedades.append(0)

    try:
        gas = int(sensor_data.get("gas", 0))
        gases.append(gas)
    except:
        gas = 0
        gases.append(0)

    try: luces.append(float(sensor_data.get("luz", 0)))
    except: luces.append(0)

    try: distancias.append(float(sensor_data.get("dist", 0)))
    except: distancias.append(0)

    if str(sensor_data.get("pir", "0")) == "1":
        movimientos.append(now)

    # Limitar historial a 30
    temperaturas[:] = temperaturas[-30:]
    humedades[:] = humedades[-30:]
    gases[:] = gases[-30:]
    luces[:] = luces[-30:]
    distancias[:] = distancias[-30:]
    tiempos[:] = tiempos[-30:]
    movimientos[:] = movimientos[-30:]

    alerta = gas > 3000
    mensaje = "Ventiladores funcionando al 100%" if alerta else ""

    return (
        f"{sensor_data['temp']} °C",
        f"{sensor_data['hum']} %",
        str(sensor_data['gas']),
        f"{sensor_data['dist']} cm",
        str(sensor_data['luz']),
        "Movimiento detectado" if str(sensor_data["pir"]) == "1" else "Sin movimiento",
        alerta,
        mensaje
    )


@app.callback(
    Output("alerta-gas", "children"),
    Output("alerta-gas", "color"),
    Input("actualizar", "n_intervals")
)
def actualizar_alerta(n):
    if not gases: return "", "secondary"
    valor = gases[-1]
    if valor > 3000:
        return f"⚠️ ¡Gas alto detectado!: {valor}", "danger"
    return "", "secondary"


@app.callback(
    Output("graficas-dinamicas", "children"),
    Input("btn-temp", "n_clicks"),
    Input("btn-hum", "n_clicks"),
    Input("btn-gas", "n_clicks"),
    Input("btn-luz", "n_clicks"),
    Input("btn-dist", "n_clicks"),
    Input("btn-pir", "n_clicks"),
    prevent_initial_call=True
)
def mostrar_grafica(n_temp, n_hum, n_gas, n_luz, n_dist, n_pir):
    triggered = ctx.triggered_id
    fig = go.Figure()

    if triggered == "btn-temp":
        fig.add_trace(go.Scatter(x=tiempos, y=temperaturas, mode="lines+markers", line=dict(color="red")))
        fig.update_layout(title="Temperatura (°C)", height=300)
    elif triggered == "btn-hum":
        fig.add_trace(go.Scatter(x=tiempos, y=humedades, mode="lines+markers", line=dict(color="blue")))
        fig.update_layout(title="Humedad (%)", height=300)
    elif triggered == "btn-gas":
        fig.add_trace(go.Scatter(x=tiempos, y=gases, mode="lines+markers", line=dict(color="orange")))
        fig.update_layout(title="Nivel de Gas", height=300)
    elif triggered == "btn-luz":
        fig.add_trace(go.Scatter(x=tiempos, y=luces, mode="lines+markers", line=dict(color="green")))
        fig.update_layout(title="Luz ambiente", height=300)
    elif triggered == "btn-dist":
        fig.add_trace(go.Scatter(x=tiempos, y=distancias, mode="lines+markers", line=dict(color="purple")))
        fig.update_layout(title="Distancia (cm)", height=300)
    elif triggered == "btn-pir":
        fig.add_trace(go.Bar(x=movimientos, y=[1]*len(movimientos), name="Movimientos"))
        fig.update_layout(title="Detecciones PIR", yaxis=dict(showticklabels=False), height=300)
    else:
        return ""

    return dcc.Graph(figure=fig)
# Focos
@app.callback(Output("btn-foco1-on", "n_clicks"), Input("btn-foco1-on", "n_clicks"))
def foco1_on(n): mqtt_client.publish(TOPIC_LED1, "on") if n else None; return 0

@app.callback(Output("btn-foco1-off", "n_clicks"), Input("btn-foco1-off", "n_clicks"))
def foco1_off(n): mqtt_client.publish(TOPIC_LED1, "off") if n else None; return 0

@app.callback(Output("btn-foco2-on", "n_clicks"), Input("btn-foco2-on", "n_clicks"))
def foco2_on(n): mqtt_client.publish(TOPIC_LED2, "on") if n else None; return 0

@app.callback(Output("btn-foco2-off", "n_clicks"), Input("btn-foco2-off", "n_clicks"))
def foco2_off(n): mqtt_client.publish(TOPIC_LED2, "off") if n else None; return 0

# Puertas
@app.callback(Output("abrir1", "n_clicks"), Input("abrir1", "n_clicks"))
def abrir_puerta1(n): mqtt_client.publish(TOPIC_SERVO1, "90") if n else None; return 0

@app.callback(Output("cerrar1", "n_clicks"), Input("cerrar1", "n_clicks"))
def cerrar_puerta1(n): mqtt_client.publish(TOPIC_SERVO1, "0") if n else None; return 0

@app.callback(Output("abrir2", "n_clicks"), Input("abrir2", "n_clicks"))
def abrir_puerta2(n): mqtt_client.publish(TOPIC_SERVO2, "90") if n else None; return 0

@app.callback(Output("cerrar2", "n_clicks"), Input("cerrar2", "n_clicks"))
def cerrar_puerta2(n): mqtt_client.publish(TOPIC_SERVO2, "0") if n else None; return 0

# Ventiladores
@app.callback(Output("btn-step1", "n_clicks"), Input("btn-step1", "n_clicks"))
def ventilador1(n): mqtt_client.publish(TOPIC_STEPPER1, "on") if n else None; return 0

@app.callback(Output("btn-step2", "n_clicks"), Input("btn-step2", "n_clicks"))
def ventilador2(n): mqtt_client.publish(TOPIC_STEPPER2, "on") if n else None; return 0

# Ejecutar app
if __name__ == "__main__":
    app.run(debug=True)    