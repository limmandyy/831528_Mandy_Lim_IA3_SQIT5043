import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import calendar

# Load your data from the CSV file
data_path = 'C:\\Users\\mandy\\831528_Mandy_Lim_IA3_SQIT5043\\my_data.csv'
df = pd.read_csv(data_path)

# Purpose labels
purpose_labels = {
    'pur_sec': 'Purchase of Security',
    'pur_tra_veh': 'Purchase of Transport Vehicles',
    'pur_res_pro': 'Purchase of Residential Property',
    'pur_non_res_pro': 'Purchase of Non-residential Property',
    'pur_fix_ass_oth_lan_and_bui': 'Purchase of Fixed Assets other than Land and Building',
    'per_use': 'Personal uses',
    'cre_car': 'Credit Card',
    'pur_con_goo': 'Purchase of Consumer Durable Goods',
    'con': 'Construction',
    'wor_cap': 'Working Capital',
    'oth_pur': 'Other Purposes'
}

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Loan Analysis Dashboard"),
    html.P("Please select a year:", style={'font-size': '20px', 'font-family': 'Times New Roman', 'font-weight': 'bold'}),
    html.Div([
        dcc.Dropdown(
            id='year-dropdown',
            options=[
                {'label': year, 'value': year} for year in df['year_dt'].unique()
            ],
            value=df['year_dt'].min(),
        ),
        html.Div([
            dcc.Graph(id='line-chart', config={'displayModeBar': False, 'staticPlot': False}),
            dcc.Markdown(id='loan-info', style={'font-size': '18px', 'font-family': 'Times New Roman', 'font-weight': 'bold'})
        ], style={'margin': 'auto'}),
        html.Div([
            dcc.Graph(id='bar-chart', config={'displayModeBar': False, 'staticPlot': False}),
        ], style={'margin': 'auto'})
    ], style={'text-align': 'center'})
])

loan_purpose_columns = [
    'pur_sec', 'pur_tra_veh', 'pur_res_pro', 'pur_non_res_pro',
    'pur_fix_ass_oth_lan_and_bui', 'per_use', 'cre_car',
    'pur_con_goo', 'con', 'wor_cap', 'oth_pur'
]

@app.callback(
    [Output('line-chart', 'figure'), Output('bar-chart', 'figure'), Output('loan-info', 'children')],
    [Input('year-dropdown', 'value')]
)
def update_charts(selected_year):
    filtered_df = df[df['year_dt'] == selected_year]

    # Calculate the sum of each loan purpose for the selected year
    purpose_sums = filtered_df[loan_purpose_columns].sum()

    # Convert the sums to billion (divide by 1,000)
    purpose_sums = purpose_sums / 1000

    # Create a DataFrame to store the sums and corresponding labels for plotting
    purpose_sums_df = pd.DataFrame({
        'Loan Purpose': [purpose_labels[column] for column in purpose_sums.index],
        'Total Value (Billion)': purpose_sums.values
    })

    # Calculate the total and average loan amounts for the selected year
    total_loan_amount = filtered_df['tot_loa_app'].sum()
    average_loan_amount = total_loan_amount / len(filtered_df['month_dt'].unique())

    # Update the text for the total and average loan amounts
    total_loan_text = f"Total amount of loan application for the selected year: RM {total_loan_amount:.2f} billion"
    average_loan_text = f"Average amount of loan application for the selected year: RM {average_loan_amount:.2f} billion"

    # Create the bar chart using Plotly Express
    bar_fig = px.bar(
        purpose_sums_df,
        x='Loan Purpose',
        y='Total Value (Billion)',
        labels={'Total Value (Billion)': 'Total (RM Billion)', 'Loan Purpose': 'Loan Purpose'},
        title=f'Loan Purpose Distribution in {selected_year}',
        text=purpose_sums.values.round(2)  # Format text labels to two decimal places
    )

    # Create the time series line chart for total loan applications month by month
    line_fig = px.line(
        filtered_df,
        x='month_dt',
        y='tot_loa_app',
        labels={'tot_loa_app': 'Total (RM Billion)', 'month_dt': 'Month'},
        title=f'Total Applied Loan for {selected_year} Month over Month'
    )

    # Map month numbers to month names
    month_names = {i: calendar.month_name[i] for i in range(1, 13)}

    # Update x-axis tick labels to display month names
    line_fig.update_xaxes(tickvals=list(month_names.keys()), ticktext=list(month_names.values()))

    # Update line chart labels
    line_fig.update_traces(text=filtered_df['tot_loa_app'].round(2), mode='lines+text', textposition='top center')

    # Set the width and height of both charts
    chart_width = 1250
    chart_height = 700
    bar_fig.update_layout(width=chart_width, height=chart_height)
    line_fig.update_layout(width=chart_width, height=chart_height)

    return line_fig, bar_fig, f"{total_loan_text}\n\n\n\n\n{average_loan_text}"

if __name__ == '__main__':
    app.run_server(debug=True)
