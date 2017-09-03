cd D:\ShoresideTDM\DemandModel
python 1_generation.py
python 2_distribution.py
python 3_tod.py
cd D:\ShoresideTDM\TimePeriods\AM
DTALite.exe
cd D:\ShoresideTDM\TimePeriods\PM
DTALite.exe
cd D:\ShoresideTDM\DemandModel
python 4_static_assignment.py
python 5_spectral_post_processing.py