import pandas as pd 
import sys
print(os.path.join(os.path.dirname(__file__), '..'))

BASE_DIR = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path.append(os.path.join(BASE_DIR, 'dash_poc', 'reusable_components'))
print(sys.path)
import reuse_functions as reuse
df = pd.read_csv(sys.argv[0])
df['new_column'] = 'none'
for i in range(10000000):
	pass
df.to_csv(r"C:\Users\Laksh\dash_old\outputs\tips1.csv")
df.to_csv(r"C:\Users\Laksh\dash_old\outputs\tips2.csv")