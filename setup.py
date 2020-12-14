import os
from cx_Freeze import setup, Executable
import stat


if __name__ == "__main__":
	wkd = r"C:\Users\Laksh\dash_poc"

	base = "Console"
	executables = [Executable('app.py', base=base)]

	buildOptions = dict(
		packages=[
		'os',
		'pandas',
		'numpy',
		'dash',
		'jinja2'],
	excludes = [
	'_pytest'],
	includes=[
	wkd])

	setup(
		name='Disability_Pricing',
		options=dict(build_exe=buildOptions),
		version='1.0',
		description='Testing standalone exe',
		executables=executables)