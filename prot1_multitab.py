#importazione librerie base
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

#importazione foglio csv di un database
df= pd.read_csv("C:/Users/arrow/Documents/Dashboardpy/exceldati/cars.csv")

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
all_type_options_list = [{"label": type, "value": type} for type in sorted(df["Type"].unique())] #da inserire nell' options
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
        type_filtrato = df[df["Make"]== make_selezionato]["Type"].unique()

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
    Input("azzera-filtri-pormpt", "n_clicks")
)

def azzera_filtri(n_clicks):

    return None, None, None, None #origin_selezionato, make_selezionato, type_selezionato, model_selezionato


########### CARD 1

#AGGIORNAMENTO DINAMICO GRAFICO (CAVALLI, CONSUMO, PREZZI)

color_map = {
    "SUV":  "#2984da",      # blu
    "Wagon": "#ff7f00",     # arancio
    "Sedan": "#4daf4a",      # verde
    "Truck": "#c460d3",      # viola
    "Sports": "#e41a1c",     # rosso
    "Hybrid": "#ffff33",     # giallo
    # aggiungi altri tipi se presenti nel tuo dataset
}

@app.callback(
    Output("grafico-output", "figure"),
    Input("cards-tab", "active_tab"),
    Input("origin-dropdown", "value"),
    Input("make-dropdown", "value"),
    Input("type-dropdown", "value"),
    Input("model-dropdown", "value")
)

def aggiorna_grafico(tab, origin_selezionato, make_selezionato, type_selezionato, model_selezionato):

    df_filtrato=df.copy()

    if origin_selezionato is not None:
        df_filtrato=df_filtrato[df_filtrato["Origin"]==origin_selezionato]

    if make_selezionato is not None:
        df_filtrato=df_filtrato[df_filtrato["Make"]==make_selezionato]

    if type_selezionato is not None:
        df_filtrato=df_filtrato[df_filtrato["Type"]==type_selezionato]
    
    if model_selezionato is not None:
        df_filtrato=df_filtrato[df_filtrato["Model"]==model_selezionato]
    
    #parte grafica

    if tab=="tab-cavalli":

        fig=px.bar(df_filtrato,
        x="Model",
        y="Horsepower",
        text="Horsepower",  # mostra valore sopra le barre
        color="Type",       # differenzia i colori per marca
        color_discrete_map=color_map,
        color_discrete_sequence=px.colors.qualitative.Set1  # tavolozza più gradevole
        )
        
        fig.update_layout(
        height=450,  # altezza più compatta
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_title=None,
        yaxis_title="Cavalli",
        margin=dict(l=20, r=20, t=60, b=40),
        font=dict(size=12)
        )

        fig.update_traces(
            textposition='outside',
            hovertemplate="<b>%{x}</b><br>Cavalli: %{y}<extra></extra>",
            marker_line_color='rgba(0,0,0,0.3)',
            marker_line_width=1
        )

        return fig
    
    else:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=df_filtrato["MPG_City"].mean(),
            title={'text': "Consumo Medio (City)"},
            gauge={
                'axis': {'range': [0, 60]},
                'bar': {'color': "#3A9BDC"},
                'steps': [
                    {'range': [0, 20], 'color': "#e22635"},
                    {'range': [20, 40], 'color': "#85e914"},
                    {'range': [40, 60], 'color': "#0090f0"}
                ]
            }
        ))
        
        return fig

#CREAZIONE PIE CHART

origin_pie_chart=px.pie(
        df,                 # inserisco db di riferimento
        names= "Origin",    # inserisco il campo
        title=False,
        height=450
    )


##################################################################### Layout dell APP ###########################################################################

#definizione Layout:
# 1 CREAZIONE CONTAINER PRINCIPALE di proprietà di dash_bootstrap_components
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.Img(src="/assets/PYlogoon.webp", height="60px"), width="auto", className="d-flex justify-content-center align-items-center"),
        dbc.Col(html.H1("Dashboard Auto CARS", className="text-center"), width=True, className="d-flex justify-content-center align-items-center"),
        dbc.Col(html.Img(src="/assets/SASlogo.webp", height="60px"), width="auto", className="d-flex justify-content-center align-items-center"),
    ], className="mb-5", align="center"),
    dbc.Row([
        dbc.Col(origin_dropdown, width=2),
        dbc.Col(make_dropdown, width=2),
        dbc.Col(type_dropdown, width=2),
        dbc.Col(model_dropdown, width=2),
        dbc.Col(dbc.Button("Azzera Ricerca", id="azzera-filtri-pormpt", style={"backgroundColor": "#cce5ff", "color": "#003366"}, className="ms-2 border-0"), width="auto"),    
    ], justify="center", className="mt-3"),
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Distribuzione mondiale", className="text-center fw-bold"),
                dbc.CardBody([
                    dcc.Graph(id="Origin_pie_chart", figure=origin_pie_chart)
                ])
            ], 
            className="mt-3 ms-5 shadow rounded-4 border-0"),
            width=3
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(
                    dbc.Tabs(id="cards-tab", active_tab="tab-cavalli", className="text-center fw-bold",
                        children=[
                            dbc.Tab(label="Cavalli", tab_id="tab-cavalli"),
                            dbc.Tab(label="Consumo", tab_id="tab-consumo"),
                            dbc.Tab(label="Prezzi", tab_id="tab-prezzi")
                        ]
                     )
                ),
                dbc.CardBody([
                    dcc.Graph(id="grafico-output", config={"displayModeBar": False})
                ])
            ],
            className=" mt-3 ms-3 mr-5 shadow rounded-4 border-0"),  # stile moderno
            width=9 # dimensione contenuta,
        ),

    ], justify="left", className="mt-4"),
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Consumi Standard", className="text-center fw-bold"),
                dbc.CardBody([
                    dcc.Graph(id="Origin_pie_chart", figure=origin_pie_chart)
                ])
            ], 
            className="mt-3 ms-5 shadow rounded-4 border-0"),
            width=3
        ),
    ]),    

], style={"backgroundColor": "#8AC2F02D", "color": "#2E2E2E"},fluid=True) # fluid=True significa che il layout si adatta alla larghezza dello schermo (responsive).



if __name__ == "__main__":
    app.run(debug=True)
