cd D:\ShoresideTDM\DemandModel
python 1_generation.py
python 2_distribution.py
python 3_tod.py
python 4_static_assignment.py
cd D:\ShoresideTDM\TimePeriods\AM
DTALite.exe
cd D:\ShoresideTDM\TimePeriods\PM
DTALite.exe
cd D:\ShoresideTDM\DemandModel
python 5_spectral_post_processing.py
python 6_cleanup.py