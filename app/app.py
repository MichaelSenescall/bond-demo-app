import streamlit as st
import pandas as pd
import statsmodels.api as sm
import plotly.express as px

def load_fama_french_5_factor_rets():
	df = pd.read_csv("data/fama_french_5_factor_rets.csv", header=0, index_col=0)
	df.index = pd.to_datetime(df.index)
	df.index = df.index.to_period('M')
	return df
	
def load_yahoo_rets(series_rf):
	df = pd.read_csv("data/yahoo_rets.csv", header=0, index_col=0)
	df.subtract(series_rf, axis=0)
	df.index = pd.to_datetime(df.index)
	df.index = df.index.to_period('M')
	return df

def regress(dependent_variable, explanatory_variables):
	# Create safe copies
	explanatory_variables = explanatory_variables.copy()
	dependent_variable = dependent_variable.copy()

	# Add Alpha scalar
	explanatory_variables.insert(0, "Alpha", 1)

	# Drop any na rows
	dependent_variable.dropna(inplace=True)
	mask = dependent_variable.index
	explanatory_variables = explanatory_variables.loc[mask]
	
	# Run model
	lm = sm.OLS(dependent_variable, explanatory_variables).fit()
	return lm

def draw_factors_graph(df, container):
	chart_container = container.container()

	# Year Selector
	min = int(df.index.year.min())
	max = int(df.index.year.max())
	selected_years = container.slider(label="Select Years", min_value=min, max_value=max, value=(min, max), key="5FG")
	
	mask = (df.index.year >= selected_years[0]) & (df.index.year <= selected_years[1])
	df = df.loc[mask]

	# Create Chart
	df.index = df.index.map(str)
	fig = px.line(df, x=df.index, y=df.columns, color_discrete_sequence=px.colors.qualitative.Antique)
	fig.update_layout(
		title="Factor Returns vs Time",
		title_x=0.5,
		legend_title_text="Factor",
		xaxis_title="Date",
		yaxis_title="Monthly Returns"
	)

	# Draw Chart & Return
	chart_container.plotly_chart(fig, use_container_width=True)

def draw_stock_graph(df, stock, container):
	chart_container = container.container()

	# Year Selector
	min = int(df.index.year.min())
	max = int(df.index.year.max())
	selected_years = container.slider(label="Select Years", min_value=min, max_value=max, value=(min, max), key="SG")
	
	mask = (df.index.year >= selected_years[0]) & (df.index.year <= selected_years[1])
	df = df.loc[mask]

	# Create Chart
	df.index = df.index.map(str)
	fig = px.line(df, x=df.index, y=df[stock], color_discrete_sequence=px.colors.qualitative.Antique)
	fig.update_layout(
		title=f"{stock} Returns vs Time",
		title_x=0.5,
		legend_title_text="Stock",
		xaxis_title="Date",
		yaxis_title="Monthly Returns"
	)

	# Draw Chart & Return
	chart_container.plotly_chart(fig, use_container_width=True)

def main():
	# Init
	st.set_page_config(layout="wide")

	# Load data
	df_fama_french = load_fama_french_5_factor_rets()
	df_yahoo = load_yahoo_rets(df_fama_french["RF"])

	# Header
	st.markdown("<h1 style='text-align: center;'>Fama-French 5 Factor Model</h1>", unsafe_allow_html=True)
	fama_french_5_factor_equation = """
		<div style="text-align: center;font-size: 20px;font-family: math;">
        	R<sub>it</sub> — RF<sub>t</sub> = &alpha;<sub>i</sub> + &beta;<sub>i</sub>(RM<sub>t</sub> — RF<sub>t</sub>) + s<sub>i</sub>SMB<sub>t</sub> + h<sub>i</sub>HML<sub>t</sub> + r<sub>i</sub>RMW<sub>t</sub> + c<sub>i</sub>CMA<sub>t</sub>
		</div>
        """
	st.markdown(fama_french_5_factor_equation, unsafe_allow_html=True)

	# User input
	selected_stock = st.selectbox("Please select a stock for price prediction", df_yahoo.columns)

	min_value = -10.0
	max_value = 10.0
	step = 0.000001

	Mkt_minus_RF = st.number_input("Mkt-RF", min_value=min_value, max_value=max_value, value=0.007745, step=step, format="%.6f")
	cols = st.columns(2)
	SMB = cols[0].number_input("SMB", min_value=min_value, max_value=max_value, value=0.001468, step=step, format="%.6f")
	RMW = cols[0].number_input("RMW", min_value=min_value, max_value=max_value, value=0.003084, step=step, format="%.6f")
	HML = cols[1].number_input("HML", min_value=min_value, max_value=max_value, value=0.000196, step=step, format="%.6f")
	CMA = cols[1].number_input("CMA", min_value=min_value, max_value=max_value, value=0.001693, step=step, format="%.6f")

	# Run model
	factors = ["Mkt-RF", "SMB", "HML", "RMW", "CMA"]
	results = regress(df_yahoo[selected_stock], df_fama_french.loc[:,factors]).params
	ret_minus_rf = results["Alpha"] + (results["Mkt-RF"]*Mkt_minus_RF) + (results["SMB"]*SMB) + (results["HML"]*HML) + (results["RMW"]*RMW) + (results["CMA"]*CMA)

	# Display results
	result_text = f"""
		<div style="text-align: center;font-size: 20px;font-family: math;">
			R<sub>it</sub> — RF<sub>t</sub> = {round(ret_minus_rf*100, 4)}%
		</div>
	"""
	st.markdown(result_text, unsafe_allow_html=True)

	# Draw graphs
	cols = st.columns(2)
	draw_factors_graph(df_fama_french, cols[0])
	draw_stock_graph(df_yahoo, selected_stock, cols[1])

if __name__ == "__main__":
	main()