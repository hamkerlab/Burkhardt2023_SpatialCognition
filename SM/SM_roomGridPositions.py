"""
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

from SM_vr_functions import get_object_pos

def load_attributes(annarInterface):
    if annarInterface:
        object_positions = get_object_pos(annarInterface) # gets x and y positions of the three objects (green crane, yellow crane, green racecar)
    else:
        object_positions = [7.818, 1.403, 6.370, 1.688, 7.351, 2.323] # object positions from the simulations in the manuscript

    ObjectAttributes = []

    dict_carYl_0 = {'numID': 0, 'name': 'carCraneYellow', 'Coords2D': [object_positions[2], object_positions[3]], 'Coords3D': [object_positions[2], 3.1, object_positions[3]]}
    dict_carGr_1 = {'numID': 1, 'name': 'carCraneGreen', 'Coords2D': [object_positions[0], object_positions[1]], 'Coords3D': [object_positions[0], 3.1, object_positions[1]]}
    dict_dog_2 =   {'numID': 2, 'name': 'dog',      'Coords2D': [object_positions[4], object_positions[5]], 'Coords3D': [object_positions[4], 3.1, object_positions[5]]} # dog actually is the green racecar, have to change this in code
    dict_book_3 =  {'numID': 3, 'name': 'bookBlue', 'Coords2D': [7.7, 8.8], 'Coords3D': [7.7, 1.9, 8.8]}
    dict_duck_4 =  {'numID': 4, 'name': 'duckYellow', 'Coords2D': [5.1, 9.7], 'Coords3D': [5.1, 2.0, 9.7]}
    dict_penRd_5 = {'numID': 5, 'name': 'pencilRed', 'Coords2D': [10.6, 8.5], 'Coords3D': [10.6, 2.0, 8.5]}
    dict_penBl_6 = {'numID': 6, 'name': 'pencilBlue', 'Coords2D': [11.4, 8.5], 'Coords3D': [11.4, 2.0, 8.5]}
    dict_penGr_7 = {'numID': 7, 'name': 'pencilGreen', 'Coords2D': [11.0, 8.5], 'Coords3D': [11.0, 2.0, 8.5]}
    dict_cookie_8 ={'numID': 8, 'name': 'cookieManikinBlue', 'Coords2D': [9.9, 8.8], 'Coords3D':  [9.9, 1.9, 8.8]}

    ObjectAttributes.append(dict_carYl_0)
    ObjectAttributes.append(dict_carGr_1)
    ObjectAttributes.append(dict_dog_2)
    ObjectAttributes.append(dict_book_3)
    ObjectAttributes.append(dict_duck_4)
    ObjectAttributes.append(dict_penRd_5)
    ObjectAttributes.append(dict_penBl_6)
    ObjectAttributes.append(dict_penGr_7)
    ObjectAttributes.append(dict_cookie_8)

    return ObjectAttributes