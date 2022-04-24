import pandas as pd
import plotly.express as px

data = pd.read_csv('../Data/train.csv')

print(data.head())

segment = data.groupby('Segment').sum()
segment.reset_index(inplace=True)

print(segment)