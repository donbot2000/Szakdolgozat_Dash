import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output,  State, dash_table  # pip install dash (version 2.0.0 or higher)
import dash_daq as daq




app = Dash(__name__)

# -- Import and clean data (importing csv into pandas)
# df = pd.read_csv("intro_bees.csv")
df = pd.read_csv("param_scores.csv")
df2 = pd.read_csv("match_df.csv")
df3 = pd.read_csv("goals_df.csv")

#df = df.groupby(['State', 'ANSI', 'Affected by', 'Year', 'state_code'])[['Pct of Colonies Impacted']].mean()
#df.reset_index(inplace=True)
#print(df[:5])

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([
    

    html.H1("Hajszter Donát Tibor szakdolgozat", style={'text-align': 'center'}),
    html.H2("A diplomamunka címe: Labdarúgó mérkőzések időszakokra bontása játékintenzitás alapján adatelemzés segítségével", style={'text-align': 'center'}),
    html.Br(),
    html.Br(),


    html.Div(id='explanation_container', children=[], style={'text-align': 'center', 'font-size' : '20px'}),
    html.Br(),
    html.Br(),

    
    dcc.Dropdown(id="slct_param",
                 options=[
                     {"label": "com", "value": "com"},
                     {"label": "alpha", "value": "alpha"},
                     {"label": "halflife", "value": "halflife"},
                     {"label": "span", "value": "span"}],
                 multi=False,
                 value="com",
                 style={'width': '40%','align-items': 'center', 'justify-content': 'center'} ),
    html.Br(),
    html.Div([
        dcc.Graph(id='param_scores', figure={}, style={'width':'80%',}),
        html.Div(id='best_score_container', children=[],style={'width':'20%','text-align': 'center', 'font-size' : '20px', 'border':'3px'})
        ], style={'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'background-color':'#ECCB6B'}),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Div(id='output_container', children=[],style={'text-align': 'left', 'font-size' : '20px'}),
    html.Br(),


    dcc.Dropdown(id="slct_match",
                 options=[
                     {"label": "Stal Mielec - Wisła Kraków, 0-6", "value": "sm-wk0-6"},
                     {"label": "Stal Mielec - Lechia Gdańsk, 3-3", "value": "sm-lg3-3"},
                     {"label": "Raków Częstochowa - Górnik Zabrze, 0-0", "value": "rc-gz0-0"},
                     {"label": "Górnik Łęczna - Zagłębie Lubin, 2-1", "value": "gl-zl2-1"},
                     {"label": "Zagłębie Lubin - Raków Częstochowa, 1-2", "value": "zl-rc1-2"}],
                 multi=False,
                 value="sm-wk0-6",
                 style={'width': "50%"}
                 ),
    html.Br(),

    dcc.Graph(id='matches', figure={})

],style={'background-color': "LightGray"})


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='explanation_container', component_property='children'),
     Output(component_id='best_score_container', component_property='children'),
     Output(component_id='output_container', component_property='children'),
     Output(component_id='param_scores', component_property='figure'),
     Output(component_id='matches', component_property='figure')],
    [Input(component_id='slct_param', component_property='value'), Input(component_id='slct_match', component_property='value')]
)
def update_graph(option_slctd, match_selected):
    
    dff = df.copy()
    dff2 = df2.copy()
    dff3 = df3.copy()

    dff = dff[dff["fun_name"] == option_slctd]

    best_param = dff.loc[dff["score"] ==dff["score"].max(), "param"]
    best_param=float(best_param)

    container="Az alább látható 1-es számú grafikonon az látható, hogy hogyan változik az xboost-tal végzett bináris klasszifikáció pontossági értéke a választott ewm függvény paraméterezésének növelésével. A klasszifikáció az ewm-ek értékéból következtet arra, hogy gól trötént-e az adott időablakban. \n Az ewm függvény lenyíló listán kiválasztható."

    container2 = "A(z) {} ewm függvény {} paraméterének a legnagyobb a pontossága, amely: {}%".format(option_slctd,best_param,round(dff["score"].max()*100, 2))

    container3="A 2. grafikonon az látható, hogy egy választott meccsen hogyan alakultak a csapatok ewm értékei percről percre."



    #dff = dff[dff["Affected by"] == "Varroa_mites"]
    # Plotly Express
    fig = go.Figure(data=[go.Scatter(x=dff["param"], y=dff["score"])] )
    fig.update_layout(
    title="1. grafikon XGboost klasszifikáció ewm értékekből gólokra ",
    xaxis_title="ewm {} függvényének paramétere".format(option_slctd),
    yaxis_title="Klasszifikáció pontossága",
    legend_title="Legend Title",
    font=dict(
        family="Courier New, monospace",
        size=18,
        color="Black"
    )
    )
    fig.layout.paper_bgcolor = '#ECCB6B'


    dff2 = dff2[(dff2["used_name"]==match_selected)&(dff2["ewm_fun"]==option_slctd) ]
    dff3 = dff3[(dff3["match"]==match_selected)]

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
    x=[*range(len(dff2))],
    y=dff2["home_ewm"],
    name="Hazai csapat ewm értékek"     
    ))
    fig2.add_trace(go.Scatter(
    x=[*range(len(dff2))],
    y=dff2["away_ewm"],
    name="Vendég csapat ewm értékek"
    ))
    fig2.update_layout(
    title="2. garikon Ewm értékek az adott mérkőzés összes percére az ewm {} függvényének optimális paramétereivel".format(option_slctd),
    xaxis_title="Mérkőzés percei, a szagatott vonalak a gólokat jelölik",
    yaxis_title="Ewm értékei az adott percre",
    legend_title="Ábra elemei:",
    font=dict(
        family="Courier New, monospace",
        size=18,
        color="Black"
    )
    )
    fig2.layout.paper_bgcolor = '#ECCB6B'

    for i in range(len(dff3)):
        if(dff3["place"].iloc[i]=="H"):
            fig2.add_vline(x=dff3["minutes"].iloc[i], line_width=3, line_dash="dash", line_color="blue")
        else:
            fig2.add_vline(x=dff3["minutes"].iloc[i], line_width=3, line_dash="dash", line_color="red")


    return container,container2,container3, fig, fig2


    


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)