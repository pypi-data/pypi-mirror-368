#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
# - clean names
# - add descriptions
import sys
from math import pi
from pathlib import Path

r = 12
no=190
DAMP_R1 = 0.01
THREADS = 8
LINEAR_METRICS = ["PEAK_ACCEL", "PEAK_DRIFT"] #, "ACC_RESPONSE_HISTORY"]
NONLINEAR_METRICS = ["COLUMN_STRAIN_STATES"]
SS_DEC = 1
PERIOD_BAND = [0.1, 8]
PYTHON = sys.executable

CE58658 = {
    "channels": {
    # channel node  dof rotation angle location name
        "1":  (1031, 3,  37.66*pi/180, "abutment_1"),
        "2":  (1031, 2,  37.66*pi/180, "abutment_1"),
        "3":  (1031, 1,  37.66*pi/180, "abutment_1"),
        "6":  (307,  1,  31.02*pi/180, "bent_3_south_column_grnd_level"),
        "7":  (307,  2,  31.02*pi/180, "bent_3_south_column_grnd_level"),
        "11": (1030, 3,  37.66*pi/180, "deck_level_near_abut_1"),
        "12": (1030, 1,  37.66*pi/180, "deck_level_near_abut_1"),
        "13": (1030, 2,  37.66*pi/180, "deck_level_near_abut_1"),
        "14": (304,  1,  31.02*pi/180, "bent_3_deck_level"),
        "15": (304,  2,  31.02*pi/180, "bent_3_deck_level"),
      # "16": (30003, 3, ((31.02+26.26)/2)*pi/180, "midspan_between_bents_3_4_deck"),
        "17": (401,  1,  26.26*pi/180, "bent_4_north_column_grnd_level"),
        "18": (401,  2,  26.26*pi/180, "bent_4_north_column_grnd_level"),
        "19": (403,  1,  26.26*pi/180, "bent_4_north_column_top"),
        "20": (403,  2,  26.26*pi/180, "bent_4_north_column_top"),
        "21": (405,  3,  26.26*pi/180, "bent_4_deck_level"),
        "22": (405,  1,  26.26*pi/180, "bent_4_deck_level"),
        "23": (405,  2,  26.26*pi/180, "bent_4_deck_level"),
        "24": (407,  1,  26.26*pi/180, "bent_4_south_column_grnd_level"),
        "25": (407,  2,  26.26*pi/180, "bent_4_south_column_grnd_level")
    },
    "damping": {1: 0.015, 2: 0.015},
    "columns": [
        {'key':  2010, 'strain': True, 'label':  'Bent 2 North' },
        {'key':  2020, 'strain': True, 'label':  'Bent 2 South' },
        {'key':  3010, 'strain': True, 'label':  'Bent 3 North' },
        {'key':  3020, 'strain': True, 'label':  'Bent 3 South' },
        {'key':  4010, 'strain': True, 'label':  'Bent 4 North' },
        {'key':  4020, 'strain': True, 'label':  'Bent 4 South' },
        {'key':  5010, 'strain': True, 'label':  'Bent 5 North' },
        {'key':  5020, 'strain': True, 'label':  'Bent 5 South'}, 
        {'key':  6010, 'strain': True, 'label':  'Bent 6 North' },
        {'key':  6020, 'strain': True, 'label':  'Bent 6 South'}, 
        {'key':  7010, 'strain': True, 'label':  'Bent 7 North' },
        {'key':  7020, 'strain': True, 'label':  'Bent 7 South'}, 
        {'key':  8010, 'strain': True, 'label':  'Bent 8 North' },
        {'key':  8020, 'strain': True, 'label':  'Bent 8 South'}, 
        {'key':  9010, 'strain': True, 'label':  'Bent 9 North' },
        {'key':  9020, 'strain': True, 'label':  'Bent 9 South'}, 
        {'key': 10010, 'strain': True, 'label': 'Bent 10 North' },
        {'key': 10020, 'strain': True, 'label': 'Bent 10 South'}, 
        {'key': 11010, 'strain': True, 'label': 'Bent 11 North' },
        {'key': 11020, 'strain': True, 'label': 'Bent 11 South'}, 
        {'key': 12010, 'strain': True, 'label': 'Bent 12 North' },
        {'key': 12020, 'strain': True, 'label': 'Bent 12 South'}, 
        {'key': 12030, 'strain': True, 'label': 'Bent 12 Center'},
        {'key': 13010, 'strain': True, 'label': 'Bent 13 South, NE Line'}, 
        {'key': 13020, 'strain': True, 'label': 'Bent 13 North, NE Line'}, 
        {'key': 13040, 'strain': False, 'label': 'Bent 13, NR Line'}, 
        {'key': 14010, 'strain': True, 'label': 'Bent 14 South, NE Line'}, 
        {'key': 14020, 'strain': True, 'label': 'Bent 14 North, NE Line'}, 
        {'key': 14030, 'strain': True, 'label': 'Bent 14 Center, NE Line'}, 
        {'key': 14040, 'strain': False, 'label': 'Bent 14, NR Line'}
    ],
    "bents": [
        {'node': 203, 'record': True, 'label': 'Bent 2 North'},
        {'node': 205, 'record': True, 'label': 'Bent 2 South'},
        {'node': 303, 'record': True, 'label': 'Bent 3 North'},
        {'node': 305, 'record': True, 'label': 'Bent 3 South'},
        {'node': 403, 'record': True, 'label': 'Bent 4 North'},
        {'node': 405, 'record': True, 'label': 'Bent 4 South'},
        {'node': 503, 'record': True, 'label': 'Bent 5 North'},
        {'node': 505, 'record': True, 'label': 'Bent 5 South'}, 
        {'node': 603, 'record': True, 'label': 'Bent 6 North'}, 
        {'node': 605, 'record': True, 'label': 'Bent 6 South'}, 
        {'node': 703, 'record': True, 'label': 'Bent 7 North'}, 
        {'node': 705, 'record': True, 'label': 'Bent 7 South'}, 
        {'node': 803, 'record': True, 'label': 'Bent 8 North'}, 
        {'node': 805, 'record': True, 'label': 'Bent 8 South'}, 
        {'node': 903, 'record': True, 'label': 'Bent 9 North'}, 
        {'node': 905, 'record': True, 'label': 'Bent 9 South'}, 
        {'node': 1003, 'record': True, 'label': 'Bent 10 North'}, 
        {'node': 1005, 'record': True, 'label': 'Bent 10 South'}, 
        {'node': 1103, 'record': True, 'label': 'Bent 11 North'}, 
        {'node': 1105, 'record': True, 'label': 'Bent 11 South'}, 
        {'node': 1203, 'record': True, 'label': 'Bent 12 North'}, 
        {'node': 1207, 'record': True, 'label': 'Bent 12 South'}, 
        {'node': 1205, 'record': True, 'label': 'Bent 12 Center'}, 
        {'node': 1303, 'record': True, 'label': 'Bent 13 South, NE Line'}, 
        {'node': 1305, 'record': True, 'label': 'Bent 13 North, NE Line'}, 
        {'node': 1315, 'record': True, 'label': 'Bent 13, NR Line'}, 
        {'node': 1403, 'record': True, 'label': 'Bent 14 South, NE Line'}, 
        {'node': 1405, 'record': True, 'label': 'Bent 14 North, NE Line'}, 
        {'node': 1404, 'record': True, 'label': 'Bent 14 Center, NE Line'}, 
        {'node': 1415, 'record': True, 'label': 'Bent 14, NR Line'}, 
        # {'node': 'Max', 'record': True, 'label': 'Max'}
    ]
}

BRIDGES = {
    "CE13705": {
       "cesmd":  "CE13705", 
       "calid": "56-0586G (08-RIV-15-R41.57)",
       "name": "Corona - I15/Hwy91 Interchange Bridge",
        "accelerometers": {
            "ground_channels": [1, 2, 3], 
            "bridge_channels": [1, 2, 3, 4, 5, 6, 7, 8, 9]
        },
       "predictors": [
           {
               "name": "SRIM_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [3], "outputs": [9]},  # Only 2 events
           },
           {
               "name": "SRIM_long", "description": "Longitudinal configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [2], "outputs": [8]},  # Only 2 events
           },
           {
               "name": "OKID_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [3], "outputs": [9]},  # Only 2 events
           },
           {
               "name": "OKID_long", "description": "Longitudinal configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [2], "outputs": [8]},  # Only 2 events
           },
           {
               "name": "FDD_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fdd"],
               "config": {"period_band": PERIOD_BAND, "outputs": [9]},
           },
           {
               "name": "FDD_long", "description": "Longitudinal configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fdd"],
               "config": {"period_band": PERIOD_BAND, "outputs": [8]},
           },
           {
               "name": "FSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fourier"],
               "config": {"period_band": PERIOD_BAND, "inputs": [3], "outputs": [9]},
           },
           {
               "name": "FSTF_long", "description": "Longitudinal configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fourier"],
               "config": {"period_band": PERIOD_BAND, "inputs": [2], "outputs": [8]},
           },
           {
               "name": "RSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
               "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [3], "outputs": [9]},
           },
           {
               "name": "RSTF_long", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
               "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [2], "outputs": [8]},
           }
        ]
    },
    "CE14406": {
       "cesmd":  "CE14406", 
       "calid": "53-1471 (07-LA-47-0.86)",
       "name": "Los Angeles - Vincent Thomas Bridge",
        "accelerometers": {
            "ground_channels": [1, 14, 23, 3, 9, 13, 19, 20, 24, 25, 26], 
            "bridge_channels": [2, 4, 5, 6, 12, 7, 8, 10, 11, 15, 16, 17, 18, 21, 22, 3, 24, 25, 26]
        },
       "predictors": [
           {
               "name": "SRIM_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [1,9,24], "outputs": [2,5,7]},
           },
           {
               "name": "OKID_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [1,9,24], "outputs": [2,5,7]},
           },
           {
               "name": "FDD_tran", "description": "Transverse configuration", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fdd"],
               "config": {"period_band": PERIOD_BAND, "outputs": [2,5,7]},
           },
           {
               "name": "RSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
               "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [24], "outputs": [3]},
           },
           {
               "name": "FSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fourier"],
               "config": {"period_band": PERIOD_BAND, "inputs": [24], "outputs": [3]},
           },
           {
               "name": "SRIM_tran2", "description": "Transverse with dense sensor configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [1,9,24], "outputs": [2,4,5,6,7]},
           },
           {
               "name": "SRIM_vert", "description": "Vertical Configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [14,19,26], "outputs": [16,18,22]},
           },
           {
               "name": "OKID_vert", "description": "Vertical Configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [14,19,26], "outputs": [16,18,22]},
           },
           {
               "name": "FDD_vert", "description": "Vertical Configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fdd"],
               "config": {"period_band": PERIOD_BAND, "outputs": [16,18,22]},
           },
        ]
    },
    "CE24704": { # La Cienega
       "cesmd":  "CE24704",
       "name": "Los Angeles - I10/La Cienega Bridge",
        "accelerometers": {
            "ground_channels": [9, 10, 11], 
            "bridge_channels": [1, 2, 3, 4, 5, 6, 7, 8, 12, 13, 14, 15]
        },
       "predictors": [
           {
               "name": "SRIM_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [10], "outputs": [5,8,12]},
           },
           {
               "name": "OKID_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [10], "outputs": [5,8,12]},
           },
           {
               "name": "FDD_tran", "description": "Transverse configuration", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fdd"],
               "config": {"period_band": PERIOD_BAND, "outputs": [5,8,12]},
           },
           {
               "name": "RSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
               "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [10], "outputs": [8]},
           },
           {
               "name": "FSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fourier"],
               "config": {"period_band": PERIOD_BAND, "inputs": [10], "outputs": [8]},
           },
        ]
    },
    "CE24706": { # Palmdale
       "cesmd":  "CE24706", 
       "calid": "53-1794 (07-LA-14-R57.37)",
       "name": "Palmdale - Hwy 14/Barrel Springs Bridge",
        "accelerometers": {
            "ground_channels": [11, 12], 
            "bridge_channels": [4, 5, 6, 7, 8, 9, 10]
        },
       "predictors": [
           {
               "name": "SRIM_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [11], "outputs": [6,8,9]},
           },
           {
               "name": "OKID_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [11], "outputs": [6,8,9]},
           },
           {
               "name": "FDD_tran", "description": "Transverse configuration", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fdd"],
               "config": {"period_band": PERIOD_BAND, "outputs": [6,8,9]},
           },
           {
               "name": "RSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
               "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [11], "outputs": [9]},
           },
           {
               "name": "FSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fourier"],
               "config": {"period_band": PERIOD_BAND, "inputs": [11], "outputs": [9]},
           }
        ]
    },
    "CE24775": { # Grapevine
       "cesmd":  "CE24775", 
       "calid": "50-0271 (06-KER-5-4.1)",
       "name": "Grapevine - I5/Lebec Rd Bridge",
        "accelerometers": {
            "ground_channels": [14], 
            "bridge_channels": [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16]
        },
       "predictors": [
           {
               "name": "SRIM_tran", "description": "Transverse configuration._deck", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [14], "outputs": [6,9,15]},
           },
           {
               "name": "OKID_tran", "description": "Transverse configuration._deck", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [14], "outputs": [6,9,15]},
           },
           {
               "name": "FDD_tran", "description": "Transverse configuration._deck", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fdd"],
               "config": {"period_band": PERIOD_BAND, "outputs": [6,9,15]},
           },
           {
               "name": "RSTF_tran", "description": "Transverse configuration._deck", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
               "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [14], "outputs": [9]},
           },
           {
               "name": "FSTF_tran", "description": "Transverse configuration._deck", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fourier"],
               "config": {"period_band": PERIOD_BAND, "inputs": [14], "outputs": [9]},
           },
           {
               "name": "SRIM_tran2", "description": "Transverse configuration._center_wall", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [14], "outputs": [12,9]},
           }
        ]
    },
    "CE47315": { # San Juan Bautista
       "cesmd":  "CE47315", 
       "calid": "43-0031E (05-SBT-156-0.00)",
       "name": "San Juan Bautista - Hwy 101/156 Overpass",
        "accelerometers": {
            "ground_channels": [4, 5, 6, 1, 2, 3, 10, 11, 12], 
            "bridge_channels": [1, 2, 3, 7, 8, 9, 10, 11, 12, 13, 14, 15, 4, 5, 6]
        },
       "predictors": [
           {
               "name": "SRIM_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [6], "outputs": [11,8]},
           },
           {
               "name": "OKID_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [6], "outputs": [11,8]},
           },
           {
               "name": "FDD_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fdd"],
               "config": {"period_band": PERIOD_BAND, "decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [6], "outputs": [11,8]},
           },
           {
               "name": "RSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
               "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [6], "outputs": [11]},
           },
           {
               "name": "FSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fourier"],
               "config": {"period_band": PERIOD_BAND, "inputs": [6], "outputs": [11]},
           },
        #    {
        #        "name": "SRIM_tran2", "description": "Transverse configuration._dense", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
        #        "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [6], "outputs": [13,11,8]},
        #    }
        ]
    },
    "CE68185": { # (Carquinez West, Southbound, Suspension) (Alfred Zampa Memorial Bridge) 
       "cesmd":  "CE68185",
       "calid": "28-0352L (04-SOL-80-0.01)",
       "name": "Vallejo - Carquinez/I80 West Bridge",
        "accelerometers": {
            "ground_channels": [19, 20, 21, 22, 23, 24, 25, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 81, 82, 83, 87, 88, 93, 94], 
            "bridge_channels": [26, 27, 28, 29, 32, 33, 34, 35, 36, 37, 38, 39, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 63, 64, 65, 66, 67, 68, 70, 71, 72, 75, 78, 79, 80, 85, 86, 89, 90, 91, 95, 97, 98, 99, 100, 101, 102, 103, 1, 2, 3, 5, 6, 7, 10, 11, 12, 13, 14, 15, 16, 17, 73, 74, 76]
        },
       "predictors": [
           {
               "name": "RSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
               "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [76], "outputs": [35]},
           },
           {
               "name": "FSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fourier"],
               "config": {"period_band": PERIOD_BAND, "inputs": [76], "outputs": [35]},
           },
           {
               "name": "SRIM_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [72,56,22], "outputs": [51,39,35,29]},
           },
           {
               "name": "OKID_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [72,56,22], "outputs": [51,39,35,29]},
           },
           {
               "name": "FDD_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fdd"],
               "config": {"period_band": PERIOD_BAND, "outputs": [51,39,35,29]},
           },
           {
               "name": "SRIM_tran2", "description": "Transverse with dense sensor configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [76,72,56,22,3], "outputs": [68,65,51,39,35,29,17,7]},
           },
           {
               "name": "SRIM_vert", "description": "Vertical configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [75,71,55,21,2], "outputs": [63,64,37,38,32,33,27,28,5,6]},
           },
           {
               "name": "OKID_vert", "description": "Vertical configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [75,71,55,21,2], "outputs": [63,64,37,38,32,33,27,28,5,6]},
           },
           {
               "name": "FDD_vert", "description": "Vertical configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fdd"],
               "config": {"period_band": PERIOD_BAND, "outputs": [63,64,37,38,32,33,27,28,5,6]},
           }
        ]
    },
    "CE68184": { # (Carquinez East, Northbound)
       "cesmd":  "CE68184", 
       "calid": "23-0015R (04-SOL-80-12.8)",
       "name": "Vallejo - Carquinez/I80 East Bridge",
        "accelerometers": {
            "ground_channels": [12, 13, 28, 29, 30, 31, 32, 33, 42, 43, 44, 45, 46, 47, 48], 
            "bridge_channels": [4, 5, 6, 7, 8, 9, 10, 11, 14, 15, 17, 18, 16, 19, 20, 21, 22, 23, 24, 25, 26, 27, 34, 35, 36, 37, 38, 39, 40, 41, 49, 50, 51, 52, 53, 54, 55, 56]
        },
       "predictors": [
            {
                "name": "SRIM_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [48,46,32,33], "outputs": [56,41,35,27,26,21,18,11]},
                "tags": ["TRANSVERSE", "STATE_SPACE"]
            },
            {
                "name": "OKID_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [48,46,32,33], "outputs": [56,41,35,27,26,21,18,11]},
                "tags": ["TRANSVERSE", "STATE_SPACE"]
            },
            {
                "name": "FDD_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fdd"],
                "config": {"period_band": PERIOD_BAND, "outputs": [56,41,35,27,26,21,18,11]},
            },
            {
                "name": "SRIM_vert", "description": "Vertical configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [43,42,30,28], "outputs": [34,24,20,17,9]},
                "tags": ["VERTICAL", "STATE_SPACE"]
            },
            {
                "name": "OKID_vert", "description": "Vertical configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [43,42,30,28], "outputs": [34,24,20,17,9]},
                "tags": ["VERTICAL", "STATE_SPACE"]
            },
            {
                "name": "FDD_vert", "description": "Vertical configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fdd"],
                "config": {"period_band": PERIOD_BAND, "outputs": [34,24,20,17,9]},
            },
            {
                "name": "RSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
                "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [32], "outputs": [26]},
            },
            {
                "name": "FSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fourier"],
                "config": {"period_band": PERIOD_BAND, "inputs": [32], "outputs": [26]},
            }
        ]
    },
    "CE79421": { # Leggett
       "cesmd":  "CE79421", 
       "calid": "10-0299 (01-MEN-101-160.03)",
       "name": "Leggett - Hwy 101/Confusion Hill Bridge",
        "accelerometers": {
            "ground_channels": [6, 7, 13, 14], 
            "bridge_channels": [1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 15, 16, 17, 18, 19, 20, 21]
        },
       "predictors": [
           {
               "name": "SRIM_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [7,14,20], "outputs": [2,4,8,11,17]},
               "tags": ["TRANSVERSE", "STATE_SPACE"]
           },
           {
               "name": "OKID_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [7,14,20], "outputs": [2,4,8,11,17]},
               "tags": ["TRANSVERSE", "STATE_SPACE"]
           },
           {
               "name": "FDD", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fdd"],
               "config": {"period_band": PERIOD_BAND, "outputs": [2,4,8,11,17]},
           },
           {
               "name": "SRIM_long", "description": "Longitudinal configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [6,13,19], "outputs": [3,10]},
               "tags": ["LONGITUDINAL", "STATE_SPACE"]
           },
           {
               "name": "OKID_long", "description": "Longitudinal configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
               "config": {"outputs": [3,10]},
               "tags": ["LONGITUDINAL", "STATE_SPACE"]
           },
           {
               "name": "FDD_long", "description": "Longitudinal configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fdd"],
               "config": {"period_band": PERIOD_BAND, "outputs": [3,10]},
           },
           {
               "name": "RSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
               "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [14], "outputs": [8]},
               "tags": ["TRANSVERSE", "RESPONSE_SPECTRUM"]
           },
           {
               "name": "RSTF_long", "description": "Longitudinal configuration at the southwest (Willits) side.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
               "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [6], "outputs": [3]},
               "tags": ["LONGITUDINAL", "RESPONSE_SPECTRUM"]
           },
           {
               "name": "RSTF_long2", "description": "Longitudinal configuration at the northeast (Garberville) side.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
               "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [13], "outputs": [10]},
               "tags": ["LONGITUDINAL", "RESPONSE_SPECTRUM"]
           },
           {
               "name": "FSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fourier"],
               "config": {"period_band": PERIOD_BAND, "inputs": [14], "outputs": [8]},
               "tags": ["TRANSVERSE", "FOURIER"]
           }
        ]
    },
    "CE89708": { # Arcata
       "cesmd":  "CE89708", 
       "calid": "04-0170 (01-HUM-101-R92.99)",
       "name": "Arcata - Hwy 101/Murray Road Bridge",
        "accelerometers": {
            "ground_channels": [10, 11], 
            "bridge_channels": [4, 5, 6, 7, 8, 9, 12]
        },
       "predictors": [
           {
               "name": "SRIM_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [10], "outputs": [7,9,12]},
           },
           {
               "name": "OKID_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [10], "outputs": [7,9,12]},
           },
           {
               "name": "FDD_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fdd"],
               "config": {"period_band": PERIOD_BAND, "outputs": [7,9,12]},
           },
           {
               "name": "SRIM_long", "description": "Longitudinal configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [11], "outputs": [8]},
           },
           {
               "name": "OKID_long", "description": "Longitudinal configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [11], "outputs": [8]},
           },
           {
               "name": "FDD_long", "description": "Longitudinal configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fdd"],
               "config": {"period_band": PERIOD_BAND, "outputs": [8]},
           },
           {
               "name": "RSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
               "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [10], "outputs": [9]},
           },
           {
               "name": "RSTF_long", "description": "Longitudinal configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
               "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [11], "outputs": [8]},
           },
           {
               "name": "FSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fourier"],
               "config": {"period_band": PERIOD_BAND, "inputs": [10], "outputs": [9]},
           },
           {
               "name": "FSTF_long", "description": "Longitudinal configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fourier"],
               "config": {"period_band": PERIOD_BAND, "inputs": [11], "outputs": [8]},
           },
        ]
    },
    "CE89735": {
       "cesmd":  "CE89735", 
       "calid": "04-0229 (01-HUM-255-0.7)",
       "name": "Eureka - Middle Channel Bridge",
        "accelerometers": {
            "ground_channels": [12, 13, 16, 17], 
            "bridge_channels": [1, 2, 3, 4, 5, 6, 10, 11, 14, 15]
        },
       "predictors": [
           {
               "name": "SRIM_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [12,16], "outputs": [10,14,3]},
           },
           {
               "name": "OKID_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [12,16], "outputs": [10,14,3]},
           },
           {
               "name": "FDD_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fdd"],
               "config": {"period_band": PERIOD_BAND, "outputs": [10,14,3]},
           },
           {
               "name": "RSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
               "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [12], "outputs": [10]},
           },
           {
               "name": "FSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fourier"],
               "config": {"period_band": PERIOD_BAND, "inputs": [12], "outputs": [10]},
           }
        ]
    },
    "CE89736": {
       "cesmd":  "CE89736", 
       "calid": "04-0230 (01-HUM-255-0.2)",
       "name": "Eureka - Eureka Channel Bridge",
        "accelerometers": {
            "ground_channels": [6, 7, 1, 2, 3, 22, 23, 24, 25, 26, 27], 
            "bridge_channels": [4, 5, 8, 9, 13, 14, 15, 16, 17, 18, 19, 20, 21]
        },
       "predictors": [
           {
               "name": "SRIM_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [7,3], "outputs": [9,21,19]},
           },
           {
               "name": "OKID_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [7,3], "outputs": [9,21,19]},
           },
           {
               "name": "FDD_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fdd"],
               "config": {"period_band": PERIOD_BAND, "outputs": [9,21,19]},
           },
           {
               "name": "SRIM_tran2", "description": "Transverse with dense sensor configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [7,3], "outputs": [9,5,21,19]},
           },
           {
               "name": "RSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
               "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [7], "outputs": [9]},
           },
           {
               "name": "FSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fourier"],
               "config": {"period_band": PERIOD_BAND, "inputs": [7], "outputs": [9]},
           }
        ]
    },
    "CE89973": { # rio-dell eel river
       "cesmd":  "CE89973", 
       "calid": "04-0016R (01-HUM-101-53.9)",
       "Location": "40.5093 N, 124.1196 W",
       "name": "Rio Dell - Hwy 101/Eel River Bridge",
        "accelerometers": {
            "ground_channels": [], 
            "bridge_channels": [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
        },
       "predictors": [
           {
               "name": "SRIM_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [4,11,16], "outputs": [7,10,13,14,18]},
           },
           {
               "name": "OKID_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [4,11,16], "outputs": [7,10,13,14,18]},
           },
           {
               "name": "FDD_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fdd"],
               "config": {"period_band": PERIOD_BAND, "outputs": [7,10,13,14,18]},
           },
           {
               "name": "RSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
               "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [11], "outputs": [13]},
           },
           {
               "name": "FSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fourier"],
               "config": {"period_band": PERIOD_BAND, "inputs": [11], "outputs": [13]},
           }
        ]
    },
    "CE33742": { # ridgecrest
       "cesmd": "CE33742", 
       "calid": "50-0340 (09-KER-395-R25.08)",
       "name": "Ridgecrest - Hwy 395/Brown Road Bridge",
        "accelerometers": {
            "ground_channels": [4, 5], 
            "bridge_channels": [6, 7, 8, 9]
        },
       "predictors": [
           {
               "name": "SRIM_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [4], "outputs": [6, 7, 9]},
           },
           {
               "name": "OKID_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [4], "outputs": [6, 7, 9]},
           },
           {
               "name": "FDD_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fdd"],
               "config": {"period_band": PERIOD_BAND, "outputs": [6, 7, 9]},
           },
           {
               "name": "RSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
               "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [4], "outputs": [7]},
           },
           {
               "name": "FSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fourier"],
               "config": {"period_band": PERIOD_BAND, "inputs": [4], "outputs": [7]},
           }
        ]
    },
    "CE24694": { # Sylmar
        "cesmd": "CE24694",
        "calid": "53-2795F",
        "Location": "34.3349 N, 118.5084 W",
        "name": "Sylmar - I5/14 Interchange Bridge",
        "accelerometers": {
            "ground_channels": [10, 11, 18, 19, 20, 21, 22, 23, 24, 38, 39], 
            "bridge_channels": [1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13, 14, 15, 16, 17, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37]
        },
        "predictors": [
            {
                "name": "SRIM_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [10,18], "outputs": [7,8,12,14,27]},  # No events
            },
            {
                "name": "OKID_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [10,18], "outputs": [7,8,12,14,27]},  # No events
            },
            {
                "name": "FDD_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fdd"],
                "config": {"period_band": PERIOD_BAND, "outputs": [7,8,12,14,27]},  # No events
            },
            {
                "name": "SRIM_tran2", "description": "Transverse configuration._dense",
                "protocol": "",
                "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],
                "entry_point": [PYTHON, "-m", "mdof", "srim"],
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [1,10,18,33], "outputs": [3,5,6,7,8,12,14,27,28,29,30]},
            },
            {
                "name": "RSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
                "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [18], "outputs": [14]},
            },
            {
                "name": "FSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fourier"],
                "config": {"period_band": PERIOD_BAND, "inputs": [18], "outputs": [14]},
            }
        ]
    },
    "CE13795": { # Capistrano
       "cesmd": "CE13795", 
       "calid": "55-0225 (07-ORA-5-6.62)",
       "name": "Capistrano Beach - I5/Via Calif. Bridge",
        "accelerometers": {
            "ground_channels": [4, 5], 
            "bridge_channels": [6, 7, 8, 9, 10, 11, 12]
        },
       "predictors": [
           {
               "name": "SRIM_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
               "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [4], "outputs": [10, 7]},
           },
           {
               "name": "OKID_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
               "config": {"outputs": [10, 7]},
           },
           {
               "name": "FDD_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fdd"],
               "config": {"period_band": PERIOD_BAND, "decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [4], "outputs": [10, 7]},
           },
           {
               "name": "RSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
               "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [4], "outputs": [10]},
           },
           {
               "name": "FSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fourier"],
               "config": {"period_band": PERIOD_BAND, "inputs": [4], "outputs": [10]},
           }
       ]
    },
    "CE01336": { # meloland
        "cesmd": "CE01336",
        "calid": "58-0215",
        "Location": "32.7735 N, 115.4481 W",
        "name": "Hwy8/Meloland Overpass",
        "accelerometers": {
            "ground_channels": [1, 2, 4, 10, 11, 12, 23, 25, 26, 30], 
            "bridge_channels": [3, 5, 6, 7, 8, 13, 9, 16, 17, 18, 19, 27, 20, 21, 22, 28, 31, 29, 32]
        },
        "predictors": [
            {
                "name": "SRIM_tran", "description": "Transverse configuration.",
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [2], "outputs": [5, 7, 9]},
                "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"]
            },
            {
                "name": "OKID_tran", "description": "Transverse configuration.",
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [2], "outputs": [5, 7, 9]},
                "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "okid-era"]
            },
            {
                "name": "FDD_tran", "description": "Transverse configuration.",
                "config": {"period_band": PERIOD_BAND, "outputs": [5, 7, 9]},
                "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fdd"]
            },
            {
                "name": "SRIM_long", "description": "Longitudinal configuration.",
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [4], "outputs": [15]},
                "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"]
            },
            {
                "name": "OKID_long", "description": "Longitudinal configuration.",
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [4], "outputs": [15]},
                "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "okid-era"]
            },
            {
                "name": "FDD_long", "description": "Longitudinal configuration.",
                "config": {"period_band": PERIOD_BAND, "decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [4], "outputs": [15]},
                "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fdd"]
            },
            {
                "name": "RSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
                "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [2], "outputs": [7]},
            },
            {
                "name": "RSTF_long", "description": "Longitudinal configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
                "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [4], "outputs": [15]},
            },
            {
                "name": "FSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fourier"],
                "config": {"period_band": PERIOD_BAND, "inputs": [2], "outputs": [7]},
            },
            {
                "name": "FSTF_long", "description": "Longitudinal configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fourier"],
                "config": {"period_band": PERIOD_BAND, "inputs": [4], "outputs": [15]},
            },
            {
                "name": "SRIM_tran2", "description": "Transverse with sparse sensor configuration.",
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [2], "outputs": [7]},
                "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"]
            },
        ]
    },
    "CE54730": { # crowley
        "cesmd": "CE54730",
        "calid": "47-0048",
        "Location": "37.5733 N, 118.7390 W",
        "name": "Lake Crowley - Hwy 395 Bridge",
        "accelerometers": {
            "ground_channels": [4, 5], 
            "bridge_channels": [6, 7, 8, 9]
        },
        "predictors": [
            {
                "name": "SRIM_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [4], "outputs": [6, 7, 9]}, 
            },
            {
                "name": "OKID_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [4], "outputs": [6, 7, 9]}, 
            },
            {
                "name": "FDD_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fdd"],
                "config": {"period_band": PERIOD_BAND, "outputs": [6, 7, 9]}, 
            },
            {
                "name": "SRIM_long", "description": "Longitudinal configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [5], "outputs": [8]}, 
            },
            {
                "name": "RSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
                "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [4], "outputs": [7]},
            },
            {
                "name": "RSTF_long", "description": "Longitudinal configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
                "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [5], "outputs": [8]},
            },
            {
                "name": "FSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fourier"],
                "config": {"period_band": PERIOD_BAND, "inputs": [4], "outputs": [7]},
            },
            {
                "name": "FSTF_long", "description": "Longitudinal configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fourier"],
                "config": {"period_band": PERIOD_BAND, "inputs": [5], "outputs": [8]},
            },
        ],
    },
    "CE89686": {
        "cesmd": "CE89686",
        "calid": "04-0228",
        "name": "Eureka - Samoa Channel Bridge",
        "accelerometers": {
            "ground_channels": [7, 8, 9, 17, 28, 29, 30, 31, 32, 33, 16], 
            "bridge_channels": [1, 2, 3, 4, 5, 6, 10, 11, 12, 13, 14, 15, 18, 19, 20, 21, 22, 23, 24]
        },
        "predictors": [
            {
                "name": "SRIM_tran", "description": "Transverse configuration.",
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [8,16], "outputs": [10,12,21]}, "protocol": "", "metrics": {"SPECTRAL_SHIFT_IDENTIFICATION"},"entry_point": [PYTHON, "-m", "mdof", "srim"],
            },  # Ch16 has 9 events but the rest have at least 11
            {
                "name": "OKID_tran", "description": "Transverse configuration.",
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [8,16], "outputs": [10,12,21]}, "protocol": "", "metrics": {"SPECTRAL_SHIFT_IDENTIFICATION"},"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
            },  # Ch16 has 9 events but the rest have at least 11
            {
                "name": "FDD_tran", "description": "Transverse configuration.",
                "config": {"period_band": PERIOD_BAND, "outputs": [10,12,21]}, "protocol": "", "metrics": {"SPECTRAL_SHIFT_IDENTIFICATION"},"entry_point": [PYTHON, "-m", "mdof", "fdd"],
            },  # Ch16 has 9 events but the rest have at least 11
            {
                "name": "SRIM_tran2", "description": "Transverse configuration at Pier 8.",
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [8], "outputs": [10,12]}, "protocol": "", "metrics": {"SPECTRAL_SHIFT_IDENTIFICATION"},"entry_point": [PYTHON, "-m", "mdof", "srim"],
            },
            {
                "name": "RSTF_tran", "description": "Transverse configuration at Pier 8.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
                "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [8], "outputs": [10]},
            },
            {
                "name": "FSTF_tran", "description": "Transverse configuration at Pier 8.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fourier"],
                "config": {"period_band": PERIOD_BAND, "inputs": [8], "outputs": [10]},
            }
        ],
    },
    "CE89324": { # painter
        "cesmd": "CE89324",
        "calid": "04-0236",
        "Location": "40.5031 N, 124.1009 W",
        "name": "Rio Dell - Hwy 101/Painter St. Overcrossing",
        "accelerometers": {
            "ground_channels": [1, 2, 3, 15, 16, 17, 18, 19, 20], 
            "bridge_channels": [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        },
        "predictors": [
            {
                "name": "SRIM_tran", "description": "Transverse configuration.",
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [17,3,20], "outputs": [9,7,4]}, "protocol": "", "metrics": {"SPECTRAL_SHIFT_IDENTIFICATION"},"entry_point": [PYTHON, "-m", "mdof", "srim"],
            },
            {
                "name": "OKID_tran", "description": "Transverse configuration.",
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [17,3,20], "outputs": [9,7,4]}, "protocol": "", "metrics": {"SPECTRAL_SHIFT_IDENTIFICATION"},"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
            },
            {
                "name": "FDD_tran", "description": "Transverse configuration.",
                "config": {"period_band": PERIOD_BAND, "outputs": [9,7,4]}, "protocol": "", "metrics": {"SPECTRAL_SHIFT_IDENTIFICATION"},"entry_point": [PYTHON, "-m", "mdof", "fdd"],
            },
            {
                "name": "SRIM_long", "description": "Longitudinal configuration.",  # Sensor 11 may not be far enough away from the substructure for this configuration to be meaningful.
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [18], "outputs": [11]}, "protocol": "", "metrics": {"SPECTRAL_SHIFT_IDENTIFICATION"},"entry_point": [PYTHON, "-m", "mdof", "srim"],
            },
            {
                "name": "OKID_long", "description": "Longitudinal configuration.",  # Sensor 11 may not be far enough away from the substructure for this configuration to be meaningful.
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [18], "outputs": [11]}, "protocol": "", "metrics": {"SPECTRAL_SHIFT_IDENTIFICATION"},"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
            },
            {
                "name": "FDD_long", "description": "Longitudinal configuration.",  # Sensor 11 may not be far enough away from the substructure for this configuration to be meaningful.
                "config": {"period_band": PERIOD_BAND, "outputs": [11]}, "protocol": "", "metrics": {"SPECTRAL_SHIFT_IDENTIFICATION"},"entry_point": [PYTHON, "-m", "mdof", "fdd"],
            },
            {
                "name": "RSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
                "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [3], "outputs": [7]}, 
            },
            {
                "name": "RSTF_long", "description": "Longitudinal configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
                "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [18], "outputs": [11]}, 
            },
            {
                "name": "FSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fourier"],
                "config": {"period_band": PERIOD_BAND, "inputs": [3], "outputs": [7]}, 
            },
            {
                "name": "FSTF_long", "description": "Longitudinal configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fourier"],
                "config": {"period_band": PERIOD_BAND, "inputs": [18], "outputs": [11]}, 
            }
        ],
    },
    "CE23631": { # bernardino
        "cesmd": "CE23631",
        "calid": "54-0823G",
        "Location": "34.0650 N, 117.2962 W",
        "name": "San Bernardino - I10/215 Interchange",
        "accelerometers": {
            "ground_channels": [4, 6, 5, 22, 23, 24], 
            "bridge_channels": [1, 2, 3, 7, 10, 8, 9, 11, 12, 13, 14, 15, 16, 17, 19, 18, 20, 25, 26, 28, 29, 30, 33, 31, 32, 34, 35, 36]
        },
        "predictors": [
            {
                "name": "SRIM_tran", "description": "Transverse with sparse sensor configuration.",
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [24], "outputs": [11,19,20,25]}, "protocol": "", "metrics": {"SPECTRAL_SHIFT_IDENTIFICATION"},"entry_point": [PYTHON, "-m", "mdof", "srim"],
            },
            {
                "name": "OKID_tran", "description": "Transverse with sparse sensor configuration.",
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [24], "outputs": [11,19,20,25]}, "protocol": "", "metrics": {"SPECTRAL_SHIFT_IDENTIFICATION"},"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
            },
            {
                "name": "FDD_tran", "description": "Transverse with sparse sensor configuration.",
                "config": {"period_band": PERIOD_BAND, "outputs": [11,19,20,25]}, "protocol": "", "metrics": {"SPECTRAL_SHIFT_IDENTIFICATION"},"entry_point": [PYTHON, "-m", "mdof", "fdd"],
            },
            {
                "name": "SRIM_tran2", "description": "Transverse with dense sensor configuration.",
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [3,6,24], "outputs": [7,8,11,19,20,25,26,29,30,31,32,36]}, "protocol": "", "metrics": {"SPECTRAL_SHIFT_IDENTIFICATION"},"entry_point": [PYTHON, "-m", "mdof", "srim"],
            },
            {
                "name": "RSTF_tran", "description": "Transverse with dense sensor configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
                "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [24], "outputs": [20]},
            },
            {
                "name": "FSTF_tran", "description": "Transverse with dense sensor configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fourier"],
                "config": {"period_band": PERIOD_BAND, "inputs": [24], "outputs": [20]},
            }
        ],
    },
    "CE58658": { # hayward
        "digital_twin": True,
        "cesmd": "CE58658",
        "calid": "33-0214L",
        "Location": "37.6907 N, 122.0993 W",
        "name": "Hayward Hwy 580-238 Interchange",
        "accelerometers": {
            "ground_channels": [6, 7, 17, 18, 24, 25],
            "bridge_channels": [1, 2, 3, 4, 5, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22, 23]
        },
        # "accelerometers": {
        #     "ground_channels": [1, 2, 3, 6, 7, 17, 18, 24, 25],
        #     "bridge_channels": [11, 12, 13, 14, 15, 16, 19, 20, 21, 22, 23],
        # },
        "predictors": [
            {
                "name": f"Linear",
                "metrics": [*LINEAR_METRICS],
                "protocol": "IRIE_PREDICTOR_V1",
                "entry_point": [PYTHON, "-mCE58658", f"Procedures/linear.tcl"],
                "platform": "OpenSees",
                "active": False,
                "config": CE58658
            },
            {
                "name": f"OpenSees",
                "metrics": [*LINEAR_METRICS, *NONLINEAR_METRICS],
                "protocol": "IRIE_PREDICTOR_V1",
                "entry_point": [PYTHON, "-mCE58658", f"Procedures/nonlinear.tcl"],
                "platform": "OpenSees",
                "active": False,
                "config": CE58658,
                "model_file": Path(__file__).parents[0]/"hayward.zip"
            },
            {
                "name": "SRIM_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [2,7,25,18], "outputs": [13,15,23,20]},
            },
            {
                "name": "OKID_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [2,7,25,18], "outputs": [13,15,23,20]},
            },
            {
                "name": "FDD_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fdd"],
                "config": {"period_band": PERIOD_BAND, "outputs": [13,15,23,20]},
            },
            {
                "name": "SRIM_long", "description": "Longitudinal configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [3, 6, 17], "outputs": [12, 14, 19]},
            },
            {
                "name": "OKID_long", "description": "Longitudinal configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "okid-era"],
                "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [3, 6, 17], "outputs": [12, 14, 19]},
            },
            {
                "name": "FDD_long", "description": "Longitudinal configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fdd"],
                "config": {"period_band": PERIOD_BAND, "outputs": [12, 14, 19]},
            },
            {
                "name": "RSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
                "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [25], "outputs": [23]},
            },
            {
                "name": "RSTF_long", "description": "Longitudinal configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "response"],
                "config": {"period_band": PERIOD_BAND, "threads": THREADS, "damping": DAMP_R1, "inputs": [3], "outputs": [12]},
            },
            {
                "name": "FSTF_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fourier"],
                "config": {"period_band": PERIOD_BAND, "inputs": [25], "outputs": [23]},
            },
            {
                "name": "FSTF_long", "description": "Longitudinal configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "fourier"],
                "config": {"period_band": PERIOD_BAND, "inputs": [3], "outputs": [12]},
            },
        ]
    },
    # "CE58700": {
    #    "cesmd":  "CE58700",
    #    "name": "San Francisco - Golden Gate Bridge",
    #    "predictors": [
    #        {
    #            "name": "SRIM_tran", "description": "Transverse configuration._suspension", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
    #            "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [47,33,18,12], "outputs": [35,26,21]},  # Suspension bridge
    #        },
    #     #    {
    #     #        "name": "S2", "description": "Transverse configuration._suspension_dense",
    #     #        "protocol": "",
    #     #        "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],
    #     #        "entry_point": [PYTHON, "-m", "mdof", "srim"],
    #     #        "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [47,33,18,12], "outputs": [42,35,26,21,14]},  # Suspension bridge
    #     #    },
    #     #    {
    #     #        "name": "S3", "description": "Transverse configuration._suspension_towers",
    #     #        "protocol": "",
    #     #        "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],
    #     #        "entry_point": [PYTHON, "-m", "mdof", "srim"],
    #     #        "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [47,33,18,12], "outputs": [39,23]},  # Suspension bridge
    #     #    },
    #     #    {
    #     #        "name": "S4", "description": "Transverse configuration at the north viaduct.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
    #     #        "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [12,3], "outputs": [97,96,76]},  # North Viaduct
    #     #    },
    #         #    {
    #     #        "name": "S5", "description": "Transverse configuration at the south_viaduct.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
    #     #        "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [59,47], "outputs": [61,55,54,51]},  # South Viaduct
    #     #    },
    #     ]
    # },
    # "CE58601": {
    #    "cesmd":  "CE58601",
    #    "name": "Oakland - SF Bay Bridge/East: Skyway",
    #    "predictors": [
    #        {
    #            "name": "SRIM_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
    #            "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [4,9,14,20], "outputs": [43,44,45,51]},
    #        },
    #     #    {
    #     #        "name": "S2", "description": "Transverse with dense sensor configuration.",
    #     #        "protocol": "",
    #     #        "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],
    #     #        "entry_point": [PYTHON, "-m", "mdof", "srim"],
    #     #        "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [4,9,14,20], "outputs": [42,43,44,45,48,51,56,62,65]},
    #     #    }
    #     ]
    # },
    # "CE58632": {
    #    "cesmd":  "CE58632", 
    #    "calid": "34-0003 (04-SF-80-5.6)",
    #    "name": "San Francisco - Bay Bridge/West",
    #    "predictors": [
    #        {
    #            "name": "SRIM_tran", "description": "Transverse configuration.", "protocol": "", "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],"entry_point": [PYTHON, "-m", "mdof", "srim"],
    #            "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [1,7,16,33,50,55,70], "outputs": [5,10,20,22,28,40,47,52,61,58,65,68,73,77]},
    #        },
    #     #    {
    #     #        "name": "S2", "description": "Transverse configuration at the towers.",
    #     #        "protocol": "",
    #     #        "metrics": ["SPECTRAL_SHIFT_IDENTIFICATION"],
    #     #        "entry_point": [PYTHON, "-m", "mdof", "srim"],
    #     #        "config": {"decimate": SS_DEC, "order": 12, "horizon": 190, "inputs": [1,7,16,33,50,55,70], "outputs": [25,44,63,75]},
    #     #    }
    #     ]
    # },
}


