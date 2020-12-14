import os
import sys
import base64
from copy import copy
import dash
import dash_core_components as dcc 
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from urllib.parse import quote as urlquote
from flask import send_from_directory, request, redirect, url_for
import webbrowser
from threading import Timer
from tqdm import tqdm

COLORS = {"background": "#000000", "text": "#0090da", "alt_color": "#a4ce4e"}
BUTTON_DEFAULT_STYLE = {"backgroundColor": COLORS["alt_color"],
						"color": COLORS["background"],
						"width": "20%",
						"height": "38px",
						"fontSize": 18,
						"fontWeight": "bold"}

UPLOAD_DIRECTORY = "app_uploaded_files"
OUTPUT_DIRECTORY = "outputs"

if not os.path.exists(UPLOAD_DIRECTORY):
	os.makedirs(UPLOAD_DIRECTORY)


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([html.Div([html.H1("Disability Pricing Tool", style={"textAlign": "center", "color": COLORS["alt_color"]})]),
	                  html.Div(children="Simple Dashboard to upload Excel and Download Results",
	                  	       style={"textAlign": "center",
	                  	              "fontStyle": "italic",
	                  	              "fontSize": 18,
	                  	              "fontFamily": "monospace"}),
	                  html.H3("Select Excel to Upload"),
	                  dcc.Upload(id="upload-data",
	                  	         children=html.Div(['Drag and drop or click to select a file to upload']),
	                  	         style={
	                  	              "width": "30%",
	                  	              "height": "60px",
	                  	              "lineHeight": "60px",
	                  	              "borderWidth": "1px",
	                  	              "borderStyle": "dashed",
	                  	              "borderRadius": "5px",
	                  	              "textAlign": "center",
	                  	              "margin": "10px"
	                  	         }, multiple=True),
	                  html.Br(),
	                  html.Div([
	                  	html.Div([
	                  	         html.H3("Uploaded Files"),
	                  	         html.Ul(id="file-list")
	                  	         ],
	                  	         style={"width": "20%", "display": "inline-block"}
	                  	),
	                  html.Div([
	                  	dcc.ConfirmDialog(id='confirm-clear-input',
	                  		message=("Are you sure you would like to delete all uploads ? \n This "
	                  			"action cannot be reversed"),
	                  		submit_n_clicks=0),
	                  html.Button(id='clear-input-button',
	                  	children="Clear Uploads",
	                  	n_clicks=0)
	                  ], style={"width": "50%", "display": "inline-block"})
	                  ], style={"width": "80"}),
					html.Br(),
					html.Div(id="button-container",
						children=[html.Button(children="Click to Begin Calculations",
							id="begin-button",
							n_clicks=0,
							style=BUTTON_DEFAULT_STYLE),
						], style={"textAlign": "center"}),
					html.H3("Current Output"),
					html.Div(id="current-output-container",
						children=[html.Ul(id="output-list", children=[html.Li("No files yet.")])]),
					html.Div(id='page-content'),
					html.H6('Progress bar'), dbc.Progress(id="progress", value=10, striped=True, animated=True, style={"height": "30px"}, className="mb-3", color="success"),
					html.Div([html.Button(id='stop-server',
	                  	children="ShutDown Server",
	                  	n_clicks=0)],
	                  style={"width": "50%", "display": "inline-block"}),
 					  html.P(id='placeholder')]
					)


@app.server.route("/outputs/<path:path>")
def output(path):
	return send_from_directory(OUTPUT_DIRECTORY, path, as_attachment=True)


@app.server.route("/downloads/<path:path>")
def download(path):
	return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)


@app.server.route("/shutdown/")
def display_page():
    return shutdown()
    

def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return "The server is stopped."


def save_file(name, content):
	"""Decode and store a file Uploaded with plotly Dash. """
	data = content.encode("utf-8").split(b";base64,")[1]
	with open(os.path.join(UPLOAD_DIRECTORY, name), "wb") as fp:
		fp.write(base64.decodebytes(data))


def list_files(directory):
	"""List the files i upload directory."""
	files = []
	for filename in os.listdir(directory):
		path = os.path.join(directory, filename)
		if os.path.isfile(path):
			files.append(filename)
	return files


def file_download_link(filename, upload=True):
	"""Create a Plotly Dash 'A' element that downloads a file from the app"""
	if upload:
		location = "/downloads/{}".format(urlquote(filename))
	else:
		location = "/outputs/{}".format(urlquote(filename))
	return html.A(filename, href=location)


def clear_files(directory):
	files= list_files(directory)
	for filename in files:
		path = os.path.join(directory, filename)
		if os.path.isfile(path):
			os.remove(path)


def simple_calculation(filename):
	script_fn = "calculation.py"
	sys.argv.insert(0, os.path.join(UPLOAD_DIRECTORY, "tips.csv"))
	tqdm(exec(open(script_fn).read()))
	files = list_files(os.path.join(os.getcwd(), "outputs"))

	return [html.Li(file_download_link(filename, upload=False)) for filename in files]


@app.callback(
	Output("file-list", "children"),
	[Input("upload-data", "filename"),
	Input("upload-data", "contents"),
	],
	)
def update_upload(uploaded_filenames, uploaded_file_contents,
	              input_dir=UPLOAD_DIRECTORY):
	""" Save uploded files and regenerate the file list"""

	if uploaded_filenames is not None and uploaded_file_contents is not None:
		for name, data in zip(uploaded_filenames, uploaded_file_contents):
			save_file(name, data)
					  
	files = list_files(directory=input_dir)
	if len(files) == 0:
		return [html.Li("No files yet.")]
	else:
		return [html.Li(file_download_link(filename)) for filename in files]


@app.callback(
	Output('confirm-clear-input', 'displayed'),
	[Input('clear-input-button', 'n_clicks')],
	)
def display_confirm_input_clear(n_clicks):
	if n_clicks == 0:
		raise PreventUpdate
	else:
		return True


@app.callback(
	Output('placeholder', "None"),
	[Input('stop-server', 'n_clicks')],
	)
def display_confirm_input_clear(n_clicks):
	if n_clicks > 0:
		return redirect(url_for('display_page'))
	else:
		return "Server Stopped"


@app.callback(
	Output('upload-data', 'filename'),
	[Input('confirm-clear-input', 'submit_n_clicks')],
	)
def clear_input(submit_n_clicks, input_dir=UPLOAD_DIRECTORY):
	if submit_n_clicks == 0:
		raise PreventUpdate
	else:
		clear_files(input_dir)
		return ()


@app.callback(
	Output('output-list', 'children'),
	[Input('begin-button', 'n_clicks')],
	[State('upload-data', 'filename'),
	]
	)
def run_calc(n_clicks, filename):
	"Run Calculations"
	if n_clicks == 0:
		raise PreventUpdate
	else:
		if n_clicks > 0:
			return simple_calculation(filename)
		else:
			return [html.Li("No files yet.")]


@app.callback(
	[Output('begin-button', 'children'),
	Output('begin-button', 'style'),
	Output('begin-button', 'disabled')],
	[Input('begin-button', 'n_clicks')])
def running_button(n_clicks, button_style=BUTTON_DEFAULT_STYLE):
	if n_clicks == 0:
		raise PreventUpdate
	style = copy(button_style)
	if n_clicks > 0:
		children = "Running"
		style['backgroundColor'] = 'red'
		disabled = True
		return children, style, disabled

@app.callback(
	Output('current-output-container', 'children'),
	[Input('output-list', 'children')])
def show_outputs(output_list):
	output_list = os.listdir(os.path.join(os.getcwd(), "outputs"))
	return [html.Li(file_download_link(filename, upload=False)) for filename in output_list]


def open_browser():
	if not os.environ.get("WERKZEUG_RUN_MAIN"):
		webbrowser.open_new("http://127.0.0.1:8888")



if __name__ == "__main__":
	Timer(1, open_browser).start()
	app.run_server(debug=True, port=8888)