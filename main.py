#importazione librerie base
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, dash_table, ctx
from dash_extensions import EventListener
import dash_bootstrap_components as dbc

#IMPORTAZIONE FOGLIO CSV E MIGLIORIE DB
df= pd.read_csv("C:/Users/arrow/Documents/Dashboardpy/exceldati/cars.csv")


#Sistemazione Sintassi Origin:

def origin_valid(origin):
    if origin=="North America":
        origin="USA"
    if origin=="RWD":
        origin="Europe"
    
    return origin

df["Origin"] = df["Origin"].apply(origin_valid)

#sistemazione classe Tipo Veicolo:

def simplify_type(car_type):
    mapping = {
        'Sedan': ['Sedan', 'Fastback', 'Liftback', 'Hatchback', 'City', 'PHEV Sedan'],
        'Station Wagon': ['Wagon', 'Station Wagon','PHEV Wagon'],
        'SUV': ['SUV', 'Crossover', 'Electric SUV', 'PHEV SUV'],
        'Sports': ['Coupe', 'Sports', 'Sport', 'Concept', 'Electric', 'Coupé', 'Performance'],
        'Supercar': ['Hypercar', 'Supercar'],
        'Cabriolet': ['Convertible', 'Cabriolet', 'Roadster'],
        'Truck': ['Truck'],
        'Minivan': ['Minivan', 'MPV', 'Van', 'Duty Van'],
        'Pickup': ['Pickup','Pick-up']
    }
    for group, variants in mapping.items():
        if car_type in variants:
            return group
    return 'Other'

df["Type_simplified"]=df["Type"].apply(simplify_type)





#CONVERSIONE DA DOLLARI IN EURO:

# Tasso di cambio approssimativo da aggiornare
tasso_cambio_usd_eur = 0.93

# Nuova colonna con il prezzo in euro

df["Invoice"] = pd.to_numeric(df["Invoice"], errors="coerce")

df["Prezzo"] = df["Invoice"] * tasso_cambio_usd_eur

# Nuova colonna ConsumoCity e ConsumoHighway da galloni in benzina:


def conversione_consumi_ita (mpg):

    if mpg > 0:
        mpg_km= round(235.214/ mpg , 2)
    else:
        mpg_km = 0

    return mpg_km


df["Consumo_km/l_Citta"] = df["MPG_City"].apply(conversione_consumi_ita)

df["Consumo_km/l_ExtraUrb"] = df["MPG_Highway"].apply(conversione_consumi_ita)


####################################################### CREAZIONE INIZIALE APP #############################################################

app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

################################################## CREAZIONE DEI FILTRI OBBLIGATORI ########################################################

#FILTRO Origin es. -ASIA, EUROPA-
all_origin_options_list = [{"label": origin, "value": origin} for origin in sorted(df["Origin"].unique())] #da inserire nell' options
origin_dropdown = dcc.Dropdown(
    id="origin-dropdown",
    options=all_origin_options_list,
    placeholder="Seleziona Origine"
)
#FILTRO Type es. -Suv, Sport-
all_type_options_list = [{"label": type, "value": type} for type in sorted(df["Type_simplified"].unique())] #da inserire nell' options
type_dropdown = dcc.Dropdown(
    id="type-dropdown",
    options=all_type_options_list,
    placeholder="Seleziona tipologia veicolo"
)
#FILTRO Make es. -Audi, BMW-
all_make_options_list = [{"label": make, "value": make} for make in sorted(df["Make"].unique())] #da inserire nell' options
make_dropdown = dcc.Dropdown(
    id="make-dropdown",
    options=all_make_options_list,
    placeholder="Seleziona una Marca"
)
all_model_options_list = [{"label": model, "value": model} for model in sorted(df["Model"].unique())] #da inserire nell' options
model_dropdown = dcc.Dropdown(
    id="model-dropdown",
    options=all_model_options_list,
    placeholder="Seleziona Modello"
)


###########################################################################################################################################

################################################### FUNZIONI E FUNZIONALITà AGGIUNTIVE ####################################################

#creazione interattività 2\4 tra filtri Origin & Make
@app.callback(
    Output("make-dropdown", "options"),
    Input ("origin-dropdown", "value")
)
def aggiorna_make(origin_selezionata):
    if origin_selezionata is None: #filtro non selezionato
        options = all_make_options_list

    else:
        make_filtrato=df[df["Origin"]== origin_selezionata]["Make"].unique()

        options = [{"label": make, "value": make} for make in sorted(make_filtrato)]

    return options

#creazione interattività 3\4 tra filtri Make & Type
@app.callback(
    Output("type-dropdown", "options"),
    Input("make-dropdown", "value")
)

def aggiorna_type(make_selezionato):
    if make_selezionato is None:
        options=all_type_options_list

    else:
        type_filtrato = df[df["Make"]== make_selezionato]["Type_simplified"].unique()

        options=[{"label": type, "value": type} for type in sorted(type_filtrato)]
        
    return options
    
#creazione interattività 4\4 tra filtri Make & Model
@app.callback(
    Output("model-dropdown", "options"),
    Input("origin-dropdown", "value"),
    Input("make-dropdown", "value"),
    Input("type-dropdown", "value")
)

def aggiorna_model(origin_selezionato, make_selezionato, type_selezionato):

    multi_filtro=df
    
    if origin_selezionato is not None:
        multi_filtro=multi_filtro[multi_filtro["Origin"]==origin_selezionato]

    if make_selezionato is not None:
        multi_filtro=multi_filtro[multi_filtro["Make"]==make_selezionato]

    if type_selezionato is not None:
        multi_filtro=multi_filtro[multi_filtro["Type"]==type_selezionato]

    options=[{"label": model, "value": model} for model in sorted(multi_filtro["Model"])]
    return options

# CREAZIONE BOTTONE "Azzera Filtri":

@app.callback(
    Output("origin-dropdown", "value"),
    Output("make-dropdown", "value"),
    Output("type-dropdown", "value"),
    Output("model-dropdown", "value"),
    Input("azzera-filtri-prompt", "n_clicks")
)

def azzera_filtri(n_clicks):

    return None, None, None, None #origin_selezionato, make_selezionato, type_selezionato, model_selezionato


#AGGIORNA LOGO MARCA:

@app.callback(
    Output("logo-marca", "src"),
    Input("make-dropdown", "value")
)
def aggiorna_logo(make_selezionato):
    if make_selezionato:
        logo=f"/assets/{make_selezionato.lower()}.png"
        return logo
    else:
        return "/assets/search-logo.png"

########### CARD 1:
#CREAZIONE PIE CHART

origin_pie_chart=px.pie(
        df,                 # inserisco db di riferimento
        names= "Origin",    # inserisco il campo
        title=False,
        height=450,
        color_discrete_sequence=["#3c9fe0","#ce3030", "#3bc74e"]

    )

origin_pie_chart.update_traces(
    textposition='outside',  # etichette fuori dalla fetta
    textinfo='percent+label', 
    hoverinfo='label+percent+value'
)

origin_pie_chart.update_layout(
    title_x=0.5,
    showlegend=True,
    margin=dict(t=50, b=50, l=50, r=50),
)


########### CARD 2:

#AGGIORNAMENTO DINAMICO GRAFICO  e KPI (CAVALLI, CONSUMO, PREZZI)

color_map = {
    "SUV":  "#2984da",      # blu
    "Station Wagon": "#ff7f00",     # arancio
    "Sedan": "#4daf4a",      # verde
    "Truck": "#c460d3",      # viola
    "Sports": "#e41a1c",     # rosso
    "Hybrid": "#ffff33",     # giallo
    # aggiungi altri tipi se presenti nel tuo dataset
}


@app.callback(
    Output("grafico-cv-output", "figure"),
    Output("totale-modelli", "children"),
    Output("consumo-medio-citta", "children"),
    Output("consumo-medio-eu", "children"),
    Output("prezzo-euro", "children"),
    Input("origin-dropdown", "value"),
    Input("make-dropdown", "value"),
    Input("type-dropdown", "value"),
    Input("model-dropdown", "value")

)

def aggiorna_grafico( origin_selezionato, make_selezionato, type_selezionato, model_selezionato):

    df_filtrato=df.copy()

    if origin_selezionato is not None:
        df_filtrato=df_filtrato[df_filtrato["Origin"]==origin_selezionato]

    if make_selezionato is not None:
        df_filtrato=df_filtrato[df_filtrato["Make"]==make_selezionato]

    if type_selezionato is not None:
        df_filtrato=df_filtrato[df_filtrato["Type_simplified"]==type_selezionato]
    
    if model_selezionato is not None:
        df_filtrato=df_filtrato[df_filtrato["Model"]==model_selezionato]

    #aggiornamento totale modelli:

    totale_modelli=df_filtrato["Model"].nunique()

    #aggiornamento totale consumi città:

    consumo_citta=f"{round(df_filtrato['Consumo_km/l_Citta'].mean(), 1)} L/100km"

    #aggiungere totale consumi fuori città

    consumo_extra_urb=f"{round(df_filtrato['Consumo_km/l_ExtraUrb'].mean(), 1)} L/100km"

    #aggiungere prezzo

    prezzo = f"€{df_filtrato['Prezzo'].mean():,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    #parte grafica

    fig_cavalli=px.bar(df_filtrato,
    x="Model",
    y="Horsepower",
    text="Horsepower",  # mostra valore sopra le barre
    color="Type_simplified",       # differenzia i colori per marca
    color_discrete_map=color_map,
    color_discrete_sequence=px.colors.qualitative.Set1  # tavolozza più gradevole
    )
    
    fig_cavalli.update_layout(
    height=450,  # altezza più compatta
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis_title=None,
    yaxis_title="Cavalli",
    margin=dict(l=20, r=20, t=60, b=40),
    font=dict(size=12)
    )

    fig_cavalli.update_traces(
        textposition='outside',
        hovertemplate="<b>%{x}</b><br>Cavalli: %{y}<extra></extra>",
        marker_line_color='rgba(0,0,0,0.3)',
        marker_line_width=1
    )
    
   
    return fig_cavalli, totale_modelli, consumo_citta, consumo_extra_urb, prezzo


########### CARD 3:

#AGGIORNAMENTO TABELLONE RIEPILOGATIVO: TABELLA & BOTTONE EXPORT

#controlla se il bottone EXPORT DATI è stato cliccato e in caso esegui il download

@app.callback(
    Output("tabella-recap", "children"),
    Output("download-dati", "data"),
    Input("origin-dropdown", "value"),
    Input("make-dropdown", "value"),
    Input("type-dropdown", "value"),
    Input("model-dropdown", "value"),
    Input("export-dati", "n_clicks"),
    prevent_initial_call=True

)
def tabellone_export(origin_selezionato, make_selezionato, type_selezionato, model_selezionato, n_clicks):

    df_filtrato=df.copy()

    if origin_selezionato is not None:
        df_filtrato=df_filtrato[df_filtrato["Origin"]==origin_selezionato]

    if make_selezionato is not None:
        df_filtrato=df_filtrato[df_filtrato["Make"]==make_selezionato]

    if type_selezionato is not None:
        df_filtrato=df_filtrato[df_filtrato["Type_simplified"]==type_selezionato]
    
    if model_selezionato is not None:
        df_filtrato=df_filtrato[df_filtrato["Model"]==model_selezionato]

#creazione Tabella Recap.
    fig_tabella=dash_table.DataTable( 
            columns=[{"name": i, "id": i} for i in df_filtrato.columns],
            data=df_filtrato.to_dict('records'),
            page_size=20,
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '5px',
                'fontFamily': 'Arial',
                'fontSize': '14px'
            },
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            })
    
    if ctx.triggered_id == "export-dati" and n_clicks is not None:
        download= dcc.send_data_frame(df_filtrato.to_excel, "dati_filtrati.xlsx", index=False, sheet_name="Dati")
    else:
        download=None

    return fig_tabella, download





##################################################################### Layout dell APP ###########################################################################

#definizione Layout:
# 1 CREAZIONE CONTAINER PRINCIPALE di proprietà di dash_bootstrap_components
app.layout = html.Div(style={"backgroundColor": "#8AC2F02D", "minHeight": "100vh"}, children=[
    
    dbc.Container([

        #intestazione TITOLO

        dbc.Row([
            dbc.Col(html.Img(src="/assets/PYlogoon.webp", height="60px"), width="auto", className="d-flex justify-content-center align-items-center"),
            dbc.Col(html.H1("Dashboard Auto CARS", className="text-center"), width=True, className="d-flex justify-content-center align-items-center"),
            dbc.Col(html.Img(src="/assets/SASlogo.webp", height="60px"), width="auto", className="d-flex justify-content-center align-items-center"),
        ], className="mb-4", align="center"),

        #filtri
        dbc.Row([
            dbc.Col(origin_dropdown, width=2),
            dbc.Col(make_dropdown, width=2),
            dbc.Col(type_dropdown, width=2),
            dbc.Col(model_dropdown, width=2),
            dbc.Col(dbc.Button("Azzera Ricerca", id="azzera-filtri-prompt", 
                               style={"backgroundColor": "#cce5ff", "color": "#003366"},
                                className="ms-2 border-0"),
                                 width="auto"), 

        ],className="mt-4 mb-5 d-flex justify-content-center"),

        # Grafici A barre CAVALLI e DiSTRIBUZIONE GLOBALE
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("Distribuzione Globale AUTO", className="text-center fw-bold"),
                    dbc.CardBody([
                        dcc.Graph(id="pie-chart-figure", figure=origin_pie_chart, config={"displayModeBar": False})
                    ])
                ], 
                className=" shadow rounded-4 border-0"),
                width=3
            ),
            
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("Distribuzione Cavalli Medi", className="text-center fw-bold"),
                    dbc.CardBody([
                        dcc.Graph(id="grafico-cv-output", config={"displayModeBar": False})
                    ])
                ],className=" shadow rounded-4 border-0"), 
                width=9#,
                #style={"marginTop": "40px"}
                ),

        ]),

        # card colorate con PREZZI e CONSUMI
        dbc.Row([
            dbc.Col(
                dbc.Button("Export Dati", id="export-dati",
                        style={"backgroundColor": "#13af61d8", "color": "#FDFDFD", "width": "180px", "Padding": "0px"},
                        className="border-0"
                ),
                className="d-flex align-items-end justify-content-end"
            ),
            dbc.Col(
                html.Img(
                    src="/assets/excel.png",
                    style={
                        "height": "30px",
                        "width": "30px",
                        "opacity": "0.9",
                        "MarginEnd":"100px",
                        "Padding": "0px"
                    },
                    className="img-fluid"
                ),
                className="d-flex align-items-end justify-content-start",
            ),

            dbc.Col(
                html.Img(
                    id="logo-marca",
                    src="/assets/search-logo.png",
                    style={
                        "height": "100px",
                        "opacity": "0.9"
                    },
                    className="img-fluid"
                ),
                width=1, className="d-flex align-items-center justify-content-center",  # largo quanto basta
            ),

            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Totale Modelli", className="card-title"),
                        html.H3(id="totale-modelli", children="--", className="card-text")
                    ])
            ], style={"backgroundColor": "#17b63aff"}, inverse=True, className="rounded-4 shadow"), width=2),

            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Consumo Medio (città)", className="card-title"),
                        html.H3(id="consumo-medio-citta", children="--", className="card-text")
                    ])
                ], style={"backgroundColor": "#397fcf"}, inverse=True, className="rounded-4 shadow"), width=2),

            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Consumo Medio (extra-urbano)", className="card-title"),
                        html.H3(id="consumo-medio-eu", children="--", className="card-text")
                    ])
                ], style={"backgroundColor": "#a945ec"}, inverse=True, className="rounded-4 shadow"), width=2),

            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Prezzo (EUR)", className="card-title"),
                        html.H3(id="prezzo-euro", children="--", className="card-text")
                    ])
                ], style={"backgroundColor": "#e76f29"}, inverse=True, className="rounded-4 shadow"), width=2),


        ], className="mt-5 mb-4 d-flex align-items-end justify-content-end me-1"),

        #Ultima riga TABELLONE EXPORT
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("Tutte le misurazioni", className="text-center fw-bold"),
                    dbc.CardBody([
                        html.Div(id="tabella-recap")
                    ])
                ], className="shadow rounded-4 border-0 mt-1")
            )
        ]),
        dcc.Download(id="download-dati"),
        
    ], fluid=True),  # fluid=True significa che il layout si adatta alla larghezza dello schermo (responsive).

]) 


if __name__ == "__main__":
    app.run(debug=True)
