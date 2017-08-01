import os

BASE_PATH = os.path.split(os.path.realpath(__file__))[0]
DEMAND_MODEL_PATH = os.path.join(BASE_PATH, 'DemandModel')

os.system('python ' + os.path.join(DEMAND_MODEL_PATH, 'generation.py'))
os.system('python ' + os.path.join(DEMAND_MODEL_PATH, 'distribution.py'))