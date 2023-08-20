import cv2
import math
import numpy as np
from copy import deepcopy
from collections import Counter
from detection.functions.utils import (
    groupby_dict,
    error_number_dict,
    to_ratio,
)


__all__ = ["omr_52_detector"]


def omr_52_detector(
    image,
    recognition_coord: list,
    omr_list: dict,
    sense_value: int,
    total_order: int,
    detection_threshold: int,
    omr_margin,
):
    (_, image_c) = cv2.threshold(image.copy(), sense_value, 255, cv2.THRESH_BINARY)
    THRESH = detection_threshold
    start_point = omr_list["meta"]["start_point"]
    margin = omr_list["meta"]["margin"]
    width = omr_list["meta"]["width"]
    mod = int(margin // 12)
    answer_order = deepcopy(total_order)
    _under = int(np.average([i[1] + i[3] for i in recognition_coord]))
    _under -= margin
    margin += omr_margin
    line_list = sorted([int(_under + i * margin) for i in range(47)])
    margin = int(margin)

    answer52, p_multi, p_empty, type_dict, error_box_info = [{} for _ in range(5)]
    multi_, empty_, empty_tot, back_val_list, back_error_list = [
        list() for _ in range(5)
    ]

    for instance in omr_list["meta"]["omr_52_meta"].items():
        answer = list()
        try:
            xx = recognition_coord[
                instance[1][0][0] : instance[1][0][1] + 1 : instance[1][2]
            ]
            yy = line_list[instance[1][1][0] : instance[1][1][1] + 1 : instance[1][3]]
        except:
            pass

        if "r" in instance[1]:
            yy = list(reversed(yy))

        half_width = width // 2

        if "w" in instance[1]:
            if "n" in instance[1]:
                for y_idx, y in enumerate(yy):
                    box, boxes, all_boxes = list(), list(), list()
                    for x in xx:
                        x_mid = x[0] + x[2] // 2
                        section_img = image_c[
                            y + mod : y + margin - mod,
                            x_mid - half_width + 3 : x_mid + half_width - 3,
                        ]
                        box.append([x_mid - half_width, y, width, margin])
                        all_boxes.append(
                            [
                                answer_order + y_idx + 1,
                                [x_mid - half_width, y, width, margin],
                            ]
                        )
                        boxes.append(int(np.sum(section_img == 0)))
                    if sum(i > THRESH for i in boxes) == 0:
                        answer.append(None)
                        empty_.append(all_boxes)

                        type_dict = error_number_dict(
                            instance[0], type_dict, answer_order + y_idx + 1
                        )
                    elif sum(i > THRESH for i in boxes) > 1:
                        answer.append(
                            [str(i + 1) for i in range(len(boxes)) if boxes[i] > THRESH]
                        )
                        [
                            multi_.append([answer_order + y_idx + 1, box[i]])
                            for i in range(len(boxes))
                            if boxes[i] > THRESH
                        ]
                        type_dict = error_number_dict(
                            instance[0], type_dict, answer_order + y_idx + 1
                        )
                    else:
                        answer.append(str(int(np.argmax(boxes)) + instance[1][4]))
                answer_order += y_idx + 1

            else:
                answer_order += 1
                x_left = min([i[0] for i in xx])
                y_top = min(yy)
                width_ = max([i[0] for i in xx]) - x_left + width + half_width
                height_ = max(yy) - y_top + margin
                error_box_info[instance[0]] = to_ratio(
                    image,
                    [
                        x_left - half_width,
                        y_top - half_width // 2,
                        width_,
                        height_ + half_width,
                    ],
                )
                for y in yy:
                    box, boxes, all_boxes = list(), list(), list()
                    for x in xx:
                        x_mid = x[0] + x[2] // 2
                        section_img = image_c[
                            y + mod : y + margin - mod,
                            x_mid - half_width + 3 : x_mid + half_width - 3,
                        ]
                        box.append([x_mid - half_width, y, width, margin])
                        all_boxes.append(
                            [answer_order, [x_mid - half_width, y, width, margin]]
                        )
                        boxes.append(int(np.sum(section_img == 0)))
                    if sum(i > THRESH for i in boxes) == 0:
                        answer.append(None)
                        empty_.append(all_boxes)
                        type_dict = error_number_dict(
                            instance[0], type_dict, answer_order
                        )
                    elif sum(i > THRESH for i in boxes) > 1:
                        answer.append(None)
                        [
                            multi_.append([answer_order, box[i]])
                            for i in range(len(boxes))
                            if boxes[i] > THRESH
                        ]
                        type_dict = error_number_dict(
                            instance[0], type_dict, answer_order
                        )
                    else:
                        answer.append(str(int(np.argmax(boxes)) + instance[1][4]))

        elif "m" in instance[1]:
            if "n" in instance[1]:
                for inst in instance[1][:2]:
                    xx = recognition_coord[inst[0][0] : inst[0][1] + 1 : instance[1][2]]
                    yy = line_list[inst[1][0] : inst[1][1] + 1 : instance[1][3]]
                    for y_idx, y in enumerate(yy):
                        box, boxes, all_boxes = list(), list(), list()
                        for x in xx:
                            x_mid = x[0] + x[2] // 2
                            section_img = image_c[
                                y + mod : y + margin - mod,
                                x_mid - half_width + 3 : x_mid + half_width - 3,
                            ]
                            box.append([x_mid - half_width, y, width, margin])
                            all_boxes.append(
                                [
                                    answer_order + y_idx + 1,
                                    [x_mid - half_width, y, width, margin],
                                ]
                            )
                            boxes.append(int(np.sum(section_img == 0)))
                        if sum(i > THRESH for i in boxes) == 0:
                            answer.append(None)
                            empty_.append(all_boxes)
                            type_dict = error_number_dict(
                                instance[0], type_dict, answer_order + y_idx + 1
                            )
                        elif sum(i > THRESH for i in boxes) > 1:
                            answer.append(
                                [
                                    str(i + 1)
                                    for i in range(len(boxes))
                                    if boxes[i] > THRESH
                                ]
                            )
                            [
                                multi_.append([answer_order + y_idx + 1, box[i]])
                                for i in range(len(boxes))
                                if boxes[i] > THRESH
                            ]
                            type_dict = error_number_dict(
                                instance[0], type_dict, answer_order + y_idx + 1
                            )
                        else:
                            answer.append(str(int(np.argmax(boxes)) + instance[1][4]))
                    answer_order += y_idx + 1

            else:
                answer_order += 1
                for inst in instance[1][:2]:
                    xx = recognition_coord[inst[0][0] : inst[0][1] + 1 : instance[1][2]]
                    yy = line_list[inst[1][0] : inst[1][1] + 1 : instance[1][3]]

                    for y in yy:
                        box, boxes, all_boxes = list(), list(), list()
                        for x in xx:
                            x_mid = x[0] + x[2] // 2
                            section_img = image_c[
                                y + mod : y + margin - mod,
                                x_mid - half_width + 3 : x_mid + half_width - 3,
                            ]
                            box.append([x_mid - half_width, y, width, margin])
                            all_boxes.append(
                                [answer_order, [x_mid - half_width, y, width, margin]]
                            )
                            boxes.append(int(np.sum(section_img == 0)))
                        if sum(i > THRESH for i in boxes) == 0:
                            answer.append(None)
                            empty_.append(all_boxes)
                            type_dict = error_number_dict(
                                instance[0], type_dict, answer_order
                            )
                        elif sum(i > THRESH for i in boxes) > 1:
                            answer.append(None)
                            [
                                multi_.append([answer_order, box[i]])
                                for i in range(len(boxes))
                                if boxes[i] > THRESH
                            ]
                            type_dict = error_number_dict(
                                instance[0], type_dict, answer_order
                            )
                        else:
                            answer.append(str(int(np.argmax(boxes)) + instance[1][4]))
        else:
            answer_order += 1
            x_left = min([i[0] for i in xx])
            y_top = min(yy)
            width_ = max([i[0] for i in xx]) - x_left + width + half_width
            height_ = max(yy) - y_top + margin
            error_box_info[instance[0]] = to_ratio(
                image,
                [
                    x_left - half_width,
                    y_top - half_width // 2,
                    width_,
                    height_ + half_width,
                ],
            )
            for x in xx:
                box, boxes, all_boxes = list(), list(), list()
                x_mid = x[0] + x[2] // 2
                for y in yy:
                    section_img = image_c[
                        y + mod : y + margin - mod,
                        x_mid - half_width + 3 : x_mid + half_width - 3,
                    ]
                    box.append([x_mid - half_width, y, width, margin])
                    all_boxes.append(
                        [answer_order, [x_mid - half_width, y, width, margin]]
                    )
                    boxes.append(int(np.sum(section_img == 0)))
                if sum(i > THRESH for i in boxes) == 0:
                    answer.append(None)
                    empty_.append(all_boxes)
                    type_dict = error_number_dict(instance[0], type_dict, answer_order)
                elif sum(i > THRESH for i in boxes) > 1:
                    answer.append(None)
                    [
                        multi_.append([answer_order, box[i]])
                        for i in range(len(boxes))
                        if boxes[i] > THRESH
                    ]
                    type_dict = error_number_dict(instance[0], type_dict, answer_order)
                else:
                    answer.append(str(int(np.argmax(boxes)) + instance[1][4]))

        answer52[instance[0]] = answer
    for k, v in answer52.items():
        sub_order = total_order + 1
        if "n" in omr_list["meta"]["omr_52_meta"][k]:
            answer52[k] = [" " if i == None else i for i in answer52[k]]
            for ind, ans in enumerate(answer52[k]):
                if isinstance(ans, list):
                    back_val_list.append(
                        {
                            "section": "back",
                            "totalOrder": sub_order + ind,
                            "type": k,
                            "questionNumber": ind + 1,
                            "answer": ans,
                        }
                    )
                else:
                    back_val_list.append(
                        {
                            "section": "back",
                            "totalOrder": sub_order + ind,
                            "type": k,
                            "questionNumber": ind + 1,
                            "answer": [ans],
                        }
                    )
            total_order = total_order + ind + 1

        else:
            answer52[k] = "".join(list(map(str, v)))
            answer52[k] = answer52[k].replace("None", " ")

            back_val_list.append(
                {
                    "section": "back",
                    "totalOrder": sub_order,
                    "type": k,
                    "questionNumber": 1,
                    "answer": [answer52[k]],
                }
            )
            total_order += 1
    if multi_ or empty_:
        if multi_:
            p_multi = groupby_dict(
                list(map(lambda x: to_ratio(image, x), deepcopy(multi_)))
            )
        if empty_:
            for emp in empty_:
                empty_tot.append(
                    [
                        emp[0][0],
                        [
                            emp[0][1][0],
                            emp[0][1][1],
                            emp[-1][1][0] - emp[0][1][0] + emp[0][1][2],
                            emp[-1][1][1] - emp[0][1][1] + emp[0][1][3],
                        ],
                    ]
                )

            p_empty = groupby_dict(
                list(map(lambda x: to_ratio(image, x), deepcopy(empty_tot)))
            )
    error_list_ = dict(list(p_empty.items()) + list(p_multi.items()))
    errTypeDict = dict()
    for i in set(list(p_multi) + list(p_empty)):
        if (list(p_multi) + list(p_empty)).count(i) > 1:
            errTypeDict[i] = ["multi", "empty"]
        else:
            if i in list(p_multi):
                errTypeDict[i] = ["multi"]
            if i in list(p_empty):
                errTypeDict[i] = ["empty"]

    for err in errTypeDict:
        if [k for k, v in type_dict.items() if err in v][0] in error_box_info.keys():
            back_error_list.append(
                {
                    "section": "back",
                    "content": "omr",
                    "totalOrder": err,
                    "errType": errTypeDict[err],
                    "type": [k for k, v in type_dict.items() if err in v][0],
                    "boxInfo": [
                        error_box_info[[k for k, v in type_dict.items() if err in v][0]]
                    ],
                }
            )
        else:
            back_error_list.append(
                {
                    "section": "back",
                    "content": "omr",
                    "totalOrder": err,
                    "errType": errTypeDict[err],
                    "type": [k for k, v in type_dict.items() if err in v][0],
                    "boxInfo": error_list_[err],
                }
            )

    return back_val_list, back_error_list
