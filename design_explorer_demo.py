import os
import math
import base64
import pandas as pd
import dash
from dash import dcc, html, no_update
from dash.dependencies import Input, Output
import plotly.graph_objects as go

df = pd.read_csv("data_all_cisbat.csv")

# region Initialise Dictionary
No = {
    'range': [1,2208],
    'label': 'Number',
    'values': df['No']
}

scenario = {
    'tickvals': [1, 2, 3, 4],
    'ticktext': ['IV', 'III', 'II', 'I'],
    'label': 'Futures',
    'values': df['S']
}

t_code = {
    'tickvals' : list(range(1, 20)),
    'ticktext' : ['TO00','TF03', 'TF02', 'TF01', 'TE03', 'TE02', 'TE01', 'TD03', 'TD02', 'TD01', 'TC03', 'TC02', 'TC01', 'TB03', 'TB02', 'TB01', 'TA03', 'TA02', 'TA01'],
    'label' : 'Typology', 
    'values' : df['T']
}

block_typology = {
    'tickvals': [1, 2, 3, 4, 5, 6, 7],
    'ticktext': ['Skyscraper', 'Dense', 'Diverse', 'Tower Slab', 'Blockrand', 'Row Houses', 'No New'],
    'label': 'Typology',
    'values': df['Typology']
}

far = {
    'range': [0, 6],
    'label': 'FAR',
    'values': df['FAR']
}

env_retrofit_dict = {
    'tickvals': [1, 2, 3],
    'ticktext': ['None', 'Regular', 'Aggressive'],
    'label': 'Envelope Retrofit',
    'values': df['Env_R']
}

energy_retrofit_dict = {
    'tickvals': [1, 2],
    'ticktext': ['Fossil', 'District'],
    'label': 'Energy Retrofit',
    'values': df['E_R']
}

total_inhabitants_dict = {
    'range': [900, 5000],
    'label': 'Total Inhabitants',
    'values': df['total_inh']
}

normalised_total_demand_dict = {
    'range': [39.9,67.3],
    'label': 'Total Demand',
    'values': df['n_total']
}

total_emission_dict = {
    'range': [4,19.2],
    'label': 'Total Emission',
    'values': df['lca_total']
}

self_consumption_dict = {
    'range': [0.4, 1.0],
    'label': 'Self Consumption',
    'values': df['solar_sc']
}

self_sufficiency_dict = {
    'range': [0.19, 0.4],
    'label': 'Self Sufficiency',
    'values': df['solar_au']
}

# endregion

app = dash.Dash(__name__)

# region Layout
app.layout = html.Div([
    html.Label("Select total demand range:", style={'font-family': 'Helvetica', 'font-size': '20px'}),
    dcc.RangeSlider(
        id='total-demand-slider',
        marks={i: {'label': str(i), 'style': {'font-family': 'Helvetica', 'font-size': '20px'}} for i in range(int(df['n_total'].min()), int(df['n_total'].max()) + 1)},
        min=math.floor(int(df['n_total'].min())),
        max=math.ceil(int(df['n_total'].max())),
        step=1,
        value=[39, 68],  # Default values
    ),

    html.Label("Select total emission range:", style={'font-family': 'Helvetica', 'font-size': '20px'}),
    dcc.RangeSlider(
        id='total-emission-slider',
        min=math.floor(df['lca_total'].min()),
        max=math.ceil(df['lca_total'].max()),
        step=1,
        marks={i: {'label': str(i), 'style': {'font-family': 'Helvetica', 'font-size': '20px'}} for i in range(int(df['lca_total'].min()), math.ceil(int(df['lca_total'].max())) + 1)},
        value=[4, 20],  # Default values
    ),
    
    html.Label("Select total inhabitants range:", style={'font-family': 'Helvetica', 'font-size': '20px'}),
    dcc.RangeSlider(
        id='inhabitants-slider',
        min=500,
        max=5000,
        step=500,
        marks={i: {'label': str(i), 'style': {'font-family': 'Helvetica', 'font-size': '20px'}} for i in range(500, 5001, 500)},
        value=[500, 5000],  # Default values
    ),

    dcc.Graph(id='parallel-plot'),

    html.Div(id='selected-typology-output', style={'font-family': 'Helvetica', 'font-size': '20px'}),
    html.Div(id='selected-envp-retrofit-output', style={'font-family': 'Helvetica', 'font-size': '20px'}),
    html.Div(id='selected-eneg-retrofit-output', style={'font-family': 'Helvetica', 'font-size': '20px'}),
    html.Div([
        html.Label("Selected Typology Images:", style={'font-family': 'Helvetica', 'font-size': '20px'}),
        html.Div(id='typology-images'),
    ])
])

typology_mapping = {
    1: 'Skyscraper',
    2: 'Dense',
    3: 'Diverse',
    4: 'Tower Slab',
    5: 'Blockrand',
    6: 'Row Houses',
    7: 'No New'
}

Env_R_mapping = {
    1: 'No Envelope Retrofit',
    2: 'Regular Envelope Retrofit',
    3: 'Aggressive Envelope Retrofit'
}

E_R_mapping = {
    1: 'Fossil Fuel Energy Systems',
    2: 'District Energy Systems'
}

typology_picture_mapping = {
    19: r'typology\TA01.png', 
    18: r'typology\TA02.png', 
    17: r'typology\TA03.png', 
    16: r'typology\TB01.png', 
    15: r'typology\TB02.png', 
    14: r'typology\TB03.png', 
    13: r'typology\TC01.png', 
    12: r'typology\TC02.png', 
    11: r'typology\TC03.png', 
    10: r'typology\TD01.png', 
    9: r'typology\TD02.png', 
    8: r'typology\TD03.png', 
    7: r'typology\TE01.png', 
    6: r'typology\TE02.png', 
    5: r'typology\TE03.png', 
    4: r'typology\TF01.png', 
    3: r'typology\TF02.png', 
    2: r'typology\TF03.png', 
    1: r'typology\TO00.png'
}

@app.callback(
    [Output('parallel-plot', 'figure'),
     Output('selected-typology-output', 'children'),
     Output('selected-envp-retrofit-output', 'children'),
     Output('selected-eneg-retrofit-output', 'children'),
     Output('typology-images', 'children')
    ], 
    [Input('total-demand-slider', 'value'),
     Input('total-emission-slider', 'value'),
     Input('inhabitants-slider', 'value')]
)
def update_parallel_plot(selected_total_demand_range,
                         selected_total_emission_range,
                         selected_inhabitants_range,):
    # Create a blank figure
    fig = go.Figure()

    # Add the parallel coordinates trace
    fig.add_trace(
        go.Parcoords(
            line=dict(
                color=df['S'],
                colorscale=['orange', 'red', 'green', 'blue'],
                showscale=False,
                cmin=1,
                cmax=4,
            ),
            dimensions=[
                dict(scenario),
                dict(normalised_total_demand_dict, constraintrange=selected_total_demand_range),
                dict(total_emission_dict, constraintrange=selected_total_emission_range),
                dict(self_consumption_dict),
                dict(self_sufficiency_dict),
                dict(scenario),
                dict(block_typology),
                dict(far),
                dict(total_inhabitants_dict, constraintrange=selected_inhabitants_range),
                dict(env_retrofit_dict),
                dict(energy_retrofit_dict),
                dict(scenario)
            ]
        )
    )
    
    fig.update_layout(
        font=dict(
            family="Helvetica",
            size=20
        )
    )

    # Filter the DataFrame based on the selected ranges
    filtered_df = df.loc[
        (df['n_total'] >= selected_total_demand_range[0]) & (df['n_total'] <= selected_total_demand_range[1]) &
        (df['lca_total'] >= selected_total_emission_range[0]) & (df['lca_total'] <= selected_total_emission_range[1]) &
        (df['total_inh'] >= selected_inhabitants_range[0]) & (df['total_inh'] <= selected_inhabitants_range[1])
    ]

    selected_typologies = filtered_df['Typology'].map(typology_mapping).astype(str).unique()
    selected_typologies_str = ', '.join(selected_typologies)
        
    selected_Env_R = filtered_df['Env_R'].map(Env_R_mapping).astype(str).unique()
    selected_Env_R_str = ', '.join(selected_Env_R)

    selected_E_R = filtered_df['E_R'].map(E_R_mapping).astype(str).unique()
    selected_E_R_str = ', '.join(selected_E_R)
    
    unique_t_values = sorted(filtered_df['T'].unique())

    # Create a list of HTML img elements for the selected images
    image_elements = []
    for t_value in unique_t_values:
        image_path = typology_picture_mapping.get(t_value, 'TO00.png') 
        image_path_base64 = base64.b64encode(open(image_path, 'rb').read()).decode('ascii')
        image_elements.append(html.Img(src='data:image/png;base64,{}'.format(image_path_base64), width=180, height=180, style={'margin': '10px'}))
        #image_elements.append(html.Img(src=image_path, width=200, height=200, style={'margin': '10px'}))

    return fig, f"Selected Typologies: {selected_typologies_str}", f"Selected Envelope Retrofit: {selected_Env_R_str}", f"Selected Energy Retrofit: {selected_E_R_str}", image_elements


if __name__ == '__main__':
    app.run(debug=True)