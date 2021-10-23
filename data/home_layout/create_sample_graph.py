'''
Author: Yifan Tang (tangyf96@outlook.com)
Date: 2021-10-23 17:13:25
LastEditTime: 2021-10-23 17:53:53
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /smart_home/data/home_layout/create_sample_graph.py
'''

import copy 
import numpy as np
import pickle

def create_map_for_area(area_length, area_width, sample_dist):
    length_num = int(area_length / sample_dist) + 1
    width_num = int(area_width / sample_dist) + 1

    # 1. Define the number of sample points for the area
    sample_point_def = []
    area_one_sample_num = length_num * width_num
    print("Area one sample num:{}".format(area_one_sample_num))
    cur_width_points = []
    for i in range(1, area_one_sample_num+1, 1):
        if i % length_num == 0:
            cur_width_points.append(i)
            sample_point_def.append(copy.deepcopy(cur_width_points))
            cur_width_points.clear()
            continue
        cur_width_points.append(i)

    # 2. Define the x, y coordinate
    length_dist_map = []
    for i in np.arange(0.0, area_length, sample_dist):
        length_dist_map.append(i)

    width_dist_map = []
    for i in np.arange(0.0, area_width, sample_dist):
        width_dist_map.append(i)

    ## The origin of the coordinate for Area 1 is the upper-left corner of area 1
    # 3. Create the grid map
    grid = {}
    for row in range(len(width_dist_map)):
        for col in range(len(length_dist_map)):
            grid[sample_point_def[row][col]] = (width_dist_map[row], length_dist_map[col])

    return grid

if __name__ == "__main__":
    sample_dist = 50.0
    area_one_length = 489.
    area_one_width = 312.
    area_two_length = 80.
    area_two_width = 312.
    area_one_map = create_map_for_area(area_length=area_one_length, area_width=area_one_width, sample_dist=sample_dist)

    area_two_map = create_map_for_area(area_length=area_two_length, area_width=area_two_width, sample_dist=sample_dist)

    with open("/home/tyf/Documents/smart_home/data/home_layout/sample_points.pkl", 'wb') as f:
        data = {'area_one':area_one_map, 'area_two':area_two_map}
        pickle.dump(data, f)