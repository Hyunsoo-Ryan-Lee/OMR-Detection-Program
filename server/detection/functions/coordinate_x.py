from collections import Counter
from copy import deepcopy
import math
import cv2
import numpy as np
import settings
from detection.functions.utils import (
    detect_recog_points,
    draw_bbox,
    set_approx,
)

__all__ = ["get_x_coordinate"]

r_cand = []
r_area = []
r_diff = []
r_coord = []


def get_x_coordinate(image, height_point, recog_point, recog_diff, recog_len):
    global r_cand
    global r_area
    global r_diff
    global r_coord
    len_approx_range = (4, 8)
    area_range = (170, 350)
    ratio_range = (1.5, 5)
    criteria_list, recognition_points = list(), list()
    direction = ""
    if image.shape[0] < image.shape[1]:
        image = cv2.resize(image, (1758, 1240))
    else:
        image = cv2.resize(image, (1240, 1758))
    image_a = image.copy()
    sigma_params = 1
    _, recog_cand, recog_area = draw_bbox(
        image_a, len_approx_range, area_range, ratio_range, 11, 17
    )
    x_recog_cnt = len([i[1][1] for i in recog_area if i[1][1] <= 80])
    if x_recog_cnt > 5:
        r_cand = deepcopy(recog_cand)
        r_area = deepcopy(recog_area)
    else:
        if r_cand:
            recog_cand = deepcopy(r_cand)
            recog_area = deepcopy(r_area)
        else:
            return False, False, [], False
    if len(recog_cand) < 5:
        sigma_params = 1
        image_ccw90 = cv2.rotate(image_a, cv2.ROTATE_90_COUNTERCLOCKWISE)
        image_ccw90 = cv2.resize(image_ccw90, (1758, 1240))
        _, recog_cand, recog_area = draw_bbox(
            image_ccw90, len_approx_range, area_range, ratio_range, 11, 17
        )
        if not recog_cand:
            while not recog_cand:
                _, recog_cand, recog_area = draw_bbox(
                    image_ccw90,
                    len_approx_range,
                    area_range,
                    ratio_range,
                    -1,
                    sigma_params,
                )
                sigma_params += 1
        recog_y_point = [i[1][1] for i in recog_area if i[1][1] <= 80]
        y_cnt = dict(Counter(recog_y_point))
        y_criteria = sorted(y_cnt.items(), key=lambda item: -item[1])[0][0]
        direction = "ccw"
        image_mod = image_ccw90.copy()

        if y_criteria > int(image_ccw90.shape[0] // 2):
            image_cw90 = cv2.rotate(image_a, cv2.ROTATE_90_CLOCKWISE)
            image_cw90 = cv2.resize(image_cw90, (1758, 1240))
            _, recog_cand, recog_area = draw_bbox(
                image_cw90, len_approx_range, area_range, ratio_range, 11, 17
            )
            if not recog_cand:
                while not recog_cand:
                    _, recog_cand, recog_area = draw_bbox(
                        image_cw90,
                        len_approx_range,
                        area_range,
                        ratio_range,
                        -1,
                        sigma_params,
                    )
                    sigma_params += 1
            recog_y_point = [i[1][1] for i in recog_area if i[1][1] <= 80]
            y_cnt = dict(Counter(recog_y_point))
            y_criteria = sorted(y_cnt.items(), key=lambda item: -item[1])[0][0]
            direction = "cw"
            image_mod = image_cw90.copy()
    else:
        recog_y_point = [i[1][1] for i in recog_area if i[1][1] <= 80]
        y_cnt = dict(Counter(recog_y_point))
        y_criteria = sorted(y_cnt.items(), key=lambda item: -item[1])[0][0]
        image_mod = image_a.copy()
    recognition_coord = list()
    for coord, w, h in recog_cand:
        x, y = coord[-1][0]
        if abs(y_criteria - y) <= 3:
            criteria_list.append([x, y, w, h])
    criteria_list = sorted(criteria_list, key=lambda x: x[0])
    # print("criteria_list : ", len(criteria_list))
    angle = math.degrees(
        math.atan2(
            (criteria_list[-1][1] - criteria_list[0][1]),
            criteria_list[-1][0] - criteria_list[0][0],
        )
    )
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    image_mod = cv2.warpAffine(
        image_mod, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR
    )
    y_list = [
        i
        for i in detect_recog_points(image_mod.copy(), criteria_list)
        if i < int(image_mod.shape[1] * 0.98)
    ]
    # print("y_list : ", len(y_list))
    if len(y_list) == recog_len:
        r_diff = [y_list[i + 1] - y_list[i] for i in range(len(y_list) - 1)]
        r_coord = deepcopy(y_list)
    else:
        if r_coord:
            arr = [abs(i - min(y_list)) for i in r_coord]
        else:
            arr = [abs(i - min(y_list)) for i in recog_point]
        if r_diff:
            recog_diff = deepcopy(r_diff)
        else:
            pass
        if arr.index(min(arr)) == 0:
            y_list = [min(y_list)] + [
                min(y_list) + sum(recog_diff[:i]) for i in range(1, len(recog_diff) + 1)
            ]
        else:
            y_first = min(y_list) - sum(recog_diff[: arr.index(min(arr))])
            y_list = [y_first] + [
                y_first + sum(recog_diff[:i]) for i in range(1, len(recog_diff) + 1)
            ]

    for i in y_list:
        a = [i, criteria_list[0][1], criteria_list[0][2], criteria_list[0][3]]
        recognition_points.append(set_approx(*a))
        recognition_coord.append(a)
    coord_diff = recognition_coord[0][1] - height_point
    return image_mod, direction, recognition_coord, coord_diff


def omr_whitespace_adjust(image, omr_list, double_sided_check: bool = False):
    height_point = omr_list["height_point"]
    recog_point = omr_list["recog_point"]
    recog_diff = omr_list["recog_diff"]
    recog_len = omr_list["recog_len"]
    omr_margin = omr_list["margin"]
    if double_sided_check:
        recog_startend = omr_list["recog_startend_back"]
    else:
        recog_startend = omr_list["recog_startend"]

    image, direction, recognition_coord, coord_diff = get_x_coordinate(
        image, height_point, recog_point, recog_diff, recog_len
    )

    if len(recognition_coord) == 0:
        return False, False, False, False

    if len(recognition_coord) > 1:
        x_start_diff = recog_startend[0] - recognition_coord[0][0]
        x_end_diff = recognition_coord[-1][0] - recog_startend[-1]
        _diff = int(x_start_diff + x_end_diff)
        # print(recog_len, len(recognition_coord), _diff)
        omr_margin = 0

    if abs(x_start_diff) < recog_diff[0] // 2 and abs(x_end_diff) < recog_diff[-1] // 2:
        if omr_margin < 25:
            if _diff < -3 and _diff >= -6:
                omr_margin = -0.07
            elif _diff < -6 and _diff >= -10:
                omr_margin = -0.13
            elif _diff < -10:
                omr_margin = -0.2
        else:
            if _diff < -3 and _diff >= -7:
                omr_margin = -0.1
            elif _diff < -7 and _diff >= -12:
                omr_margin = -0.2
    # print(omr_margin)

    return image, direction, recognition_coord, omr_margin


# def omr_whitespace_adjust(image, omr_list, double_sided_check: bool = False):

#     height_point = omr_list["height_point"]
#     recog_point = omr_list["recog_point"]
#     recog_diff = omr_list["recog_diff"]
#     recog_len = omr_list["recog_len"]

#     if double_sided_check:
#         recog_startend = omr_list["recog_startend_back"]
#     else:
#         recog_startend = omr_list["recog_startend"]
#     # print("recog_startend : ", recog_startend)
#     image, direction, recognition_coord, coord_diff = get_x_coordinate(
#         image, height_point, recog_point, recog_diff, recog_len
#     )
#     if len(recognition_coord) == 0:
#         return False, False, False, False
#     x_start_diff = recognition_coord[0][0] - recog_startend[0]
#     x_end_diff = recognition_coord[-1][0] - recog_startend[-1]
#     # 판독된 x좌표들의 간격이 기준보다 좁을 때
#     y_total_diff = int(
#         settings.resize_height * abs(x_start_diff - x_end_diff) / settings.resize_width
#     )
#     # print("x_diff : ", x_start_diff - x_end_diff, "y_diff : ", y_total_diff)
#     if (recognition_coord[-1][0] - recognition_coord[0][0]) < np.diff(recog_startend):
#         if x_start_diff >= 0:
#             if x_end_diff >= 0:
#                 mod_img = image[
#                     y_total_diff // 2 : image.shape[0] - y_total_diff // 2,
#                     x_start_diff : image.shape[1] + x_end_diff,
#                 ]
#             else:
#                 mod_img = image[
#                     y_total_diff // 2 : image.shape[0] - y_total_diff // 2,
#                     x_start_diff : image.shape[1] - x_end_diff,
#                 ]

#         # x_start_diff, x_end_diff 모두 음수
#         else:
#             x_coord_mid = int(abs(x_start_diff + x_end_diff))
#             # 여백 중심으로 이미지 중간으로 이동
#             mod_img = cv2.copyMakeBorder(
#                 image, 0, 0, x_coord_mid // 2, 0, cv2.BORDER_CONSTANT
#             )
#             mod_img = image[
#                 y_total_diff // 2 : image.shape[0] - y_total_diff // 2,
#                 x_coord_mid // 2 : image.shape[1] - x_coord_mid // 2,
#             ]
#         mod_img = cv2.resize(mod_img, (settings.resize_width, settings.resize_height))
#         image, direction, recognition_coord, coord_diff = get_x_coordinate(
#             mod_img, height_point, recog_point, recog_diff, recog_len
#         )

#     # # 판독된 x좌표들의 간격이 기준보다 넓을 때
#     elif (recognition_coord[-1][0] - recognition_coord[0][0]) > np.diff(recog_startend):
#         if x_start_diff <= 0:
#             if x_end_diff >= 0:
#                 mod_img = cv2.copyMakeBorder(
#                     image,
#                     y_total_diff // 2,
#                     y_total_diff // 2,
#                     abs(x_start_diff),
#                     x_end_diff,
#                     cv2.BORDER_CONSTANT,
#                 )
#             else:
#                 mod_img = cv2.copyMakeBorder(
#                     image,
#                     y_total_diff // 2,
#                     y_total_diff // 2,
#                     int(abs((x_start_diff + x_end_diff) // 2)),
#                     0,
#                     cv2.BORDER_CONSTANT,
#                 )
#                 mod_img = image[
#                     :, : image.shape[1] - int(abs((x_start_diff + x_end_diff) // 2)),
#                 ]
#         else:
#             mod_img = cv2.copyMakeBorder(
#                 image,
#                 y_total_diff // 2,
#                 y_total_diff // 2,
#                 0,
#                 int(abs((x_start_diff + x_end_diff) // 2)),
#                 cv2.BORDER_CONSTANT,
#             )
#             mod_img = image[
#                 :, int(abs((x_start_diff + x_end_diff) // 2)) :,
#             ]
#         mod_img = cv2.resize(mod_img, (settings.resize_width, settings.resize_height))
#         image, direction, recognition_coord, coord_diff = get_x_coordinate(
#             mod_img, height_point, recog_point, recog_diff, recog_len
#         )

#     return image, direction, recognition_coord, coord_diff
