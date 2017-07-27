import numpy as np
import pandas as pd
import os

BASE_PATH = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
OUTPUT_PATH = os.path.join(BASE_PATH, 'Output')
GENERATION_OUTPUT = os.path.join(OUTPUT_PATH, 'generation_output.csv')

nodes = pd.read_csv(GENERATION_OUTPUT, index_col = 0)

