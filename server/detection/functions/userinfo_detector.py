import math
import cv2
import numpy as np

from detection.functions.utils import (
    groupby_dict,
    to_ratio,
    make_korean_name,
)
from copy import deepcopy


def personal_info(
    image,
    recognition_coord: list,
    omr_list: dict,
    sense_value: int,
    detection_threshold: int,
    omr_margin,
):
    (_, image_c) = cv2.threshold(image.copy(), sense_value, 255, cv2.THRESH_BINARY)
    THRESH = detection_threshold
    start_point = omr_list["meta"]["start_point"]
    margin = omr_list["meta"]["margin"]
    width = omr_list["meta"]["width"]
    mod = int(margin // 12)
    _under = int(np.average([i[1] + i[3] for i in recognition_coord]))
    if omr_list["image_idx"] == 34:
        pass
    elif omr_list["image_idx"] == 59:
        _under -= 2
    elif omr_list["image_idx"] in [86, 90]:
        _under -= margin * 2
    else:
        _under -= margin + 3

    margin += omr_margin
    line_list = sorted([int(_under + i * margin) for i in range(47)])
    margin = int(margin)

    error_box_info, personal_total, personal_final_list, personal_error_list = (
        dict(),
        dict(),
        list(),
        list(),
    )

    multi_, empty_, empty_tot, p_multi, p_empty = [[] for _ in range(5)]
    name_keys = [
        name
        for name in omr_list["meta"]["personal_info"].keys()
        if "성명" in name or "이름" in name
    ]

    for inst_key, instance in omr_list["meta"]["personal_info"].items():
        answer = list()

        # y값이 한개일 때 처리
        if len(instance[1]) == 1:
            box, boxes, all_boxes = [[] for _ in range(3)]
            xx = recognition_coord[instance[0][0] : instance[0][1] + 1 : instance[2]]
            yy = line_list[instance[1][0]]
            half_width = width // 2
            if instance[-1] == -1:
                yy = [y - (margin // 2) for y in yy]
            x_left = min([i[0] for i in xx])
            width_ = max([i[0] for i in xx]) - x_left + width + half_width
            height_ = margin
            error_box_info[inst_key] = to_ratio(
                image, [x_left - half_width, yy, width_, height_]
            )
            for x in xx:
                x_mid = x[0] + x[2] // 2
                section_img = image_c[
                    yy + mod : yy + margin - mod,
                    x_mid - half_width + 2 : x_mid + half_width - 2,
                ]
                box.append([x_mid - half_width, yy, width, margin])
                boxes.append(int(np.sum(section_img == 0)))
                all_boxes.append([inst_key, [x_mid - half_width, yy, width, margin]])
            if sum(i > THRESH for i in boxes) == 0:
                answer.append(None)
                empty_.append(all_boxes)
            elif sum(i > THRESH for i in boxes) > 1:
                answer.append(None)
                [
                    multi_.append([inst_key, box[i]])
                    for i in range(len(boxes))
                    if boxes[i] > THRESH
                ]
            else:
                if instance[-1] == "vv":
                    answer.append(str(int(np.argmax(boxes)) + instance[3]).zfill(2))
                else:
                    answer.append(int(np.argmax(boxes)) + instance[3])
        # x값이 한개일 때 처리
        if len(instance[0]) == 1:
            box, boxes, all_boxes = [[] for _ in range(3)]
            xx = recognition_coord[instance[0][0]]
            yy = line_list[instance[1][0] : instance[1][1] + 1 : instance[2]]
            x_mid = xx[0] + xx[2] // 2
            half_width = width // 2
            if instance[-1] == -1:
                yy = [y - (margin // 2) for y in yy]
            y_top = min(yy)
            width_ = width
            height_ = max(yy) - y_top + margin
            error_box_info[inst_key] = to_ratio(
                image, [xx[0] - half_width, y_top, width_, height_]
            )
            for y in yy:
                section_img = image_c[
                    y + mod : y + margin - mod,
                    x_mid - half_width + 2 : x_mid + half_width - 2,
                ]
                box.append([x_mid - half_width, y, width, margin])
                boxes.append(int(np.sum(section_img == 0)))
                all_boxes.append([inst_key, [x_mid - half_width, y, width, margin]])
            if sum(i > THRESH for i in boxes) == 0:
                answer.append(None)
                empty_.append(all_boxes)
            elif sum(i > THRESH for i in boxes) > 1:
                answer.append(None)
                [
                    multi_.append([inst_key, box[i]])
                    for i in range(len(boxes))
                    if boxes[i] > THRESH
                ]
            else:
                if instance[-1] == "vv":
                    answer.append(str(int(np.argmax(boxes)) + instance[3]).zfill(2))
                else:
                    answer.append(int(np.argmax(boxes)) + instance[3])

        # x,y list일 때 처리
        if not len(instance[1]) == 1 and not len(instance[0]) == 1:
            if (omr_list["image_idx"] == 13 and inst_key == "개인번호") or (
                omr_list["image_idx"] == 42 and inst_key == "개인번호"
            ):
                rec_coord = deepcopy(recognition_coord)
                rec_coord.pop(2)
                xx = rec_coord[instance[0][0] : instance[0][1] + 1 : instance[2]]
            else:
                xx = recognition_coord[
                    instance[0][0] : instance[0][1] + 1 : instance[2]
                ]
            yy = line_list[instance[1][0] : instance[1][1] + 1 : instance[3]]
            # 간격이 약간 밀려있을 때
            if instance[-1] == -1:
                yy = [y - (margin // 2) for y in yy]

            # 67번 시험지 전용
            if instance[-1] == -2:
                xx_ = deepcopy(xx)
                xx = xx_[:4] + xx_[5:7] + xx_[8:]

            # 90번 시험지 전용
            if instance[-1] == -3:
                yy = [y - (margin // 2) for y in yy]
                xx_ = deepcopy(xx)
                xx_add = xx_.pop(4)
                xx_add[0] = 406
                xx_.append(xx_add)
                xx = xx_
            # 26번 시험지 전용
            if len(instance[1]) == 4:
                yy += line_list[instance[1][2] : instance[1][3] + 1]

            half_width = width // 2

            if len(instance) == 5 or -2 in instance or -3 in instance:
                x_left = min([i[0] for i in xx])
                y_top = min(yy)
                width_ = max([i[0] for i in xx]) - x_left + width + half_width
                height_ = max(yy) - y_top + margin
                error_box_info[inst_key] = to_ratio(
                    image,
                    [
                        x_left - half_width,
                        y_top - half_width // 2,
                        width_,
                        height_ + half_width,
                    ],
                )
                if len(instance[1]) == 4:
                    yy += line_list[instance[1][2] : instance[1][3] + 1]

                for x in xx:
                    box, boxes, all_boxes = [[] for _ in range(3)]
                    x_mid = x[0] + x[2] // 2
                    for y in yy:
                        section_img = image_c[
                            y + mod : y + margin - mod,
                            x_mid - half_width + 2 : x_mid + half_width - 2,
                        ]
                        box.append([x_mid - half_width, y, width, margin])
                        all_boxes.append(
                            [inst_key, [x_mid - half_width, y, width, margin]]
                        )
                        boxes.append(int(np.sum(section_img == 0)))

                    if sum(i > THRESH for i in boxes) == 0:
                        answer.append(None)
                        empty_.append(all_boxes)
                    elif sum(i > THRESH for i in boxes) > 1:
                        answer.append(None)
                        [
                            multi_.append([inst_key, box[i]])
                            for i in range(len(boxes))
                            if boxes[i] > THRESH
                        ]
                    else:
                        answer.append(int(np.argmax(boxes)) + instance[4])
            elif instance[-1] == "w":
                x_left = min([i[0] for i in xx])
                y_top = min(yy)
                width_ = max([i[0] for i in xx]) - x_left + width + half_width
                height_ = max(yy) - y_top + margin
                error_box_info[inst_key] = to_ratio(
                    image,
                    [
                        x_left - half_width,
                        y_top - half_width // 2,
                        width_,
                        height_ + half_width,
                    ],
                )
                for y in yy:
                    box, boxes, all_boxes = [[] for _ in range(3)]
                    for x in xx:
                        x_mid = x[0] + x[2] // 2
                        section_img = image_c[
                            y + mod : y + margin - mod,
                            x_mid - half_width + 2 : x_mid + half_width - 2,
                        ]
                        box.append([x_mid - half_width, y, width, margin])
                        all_boxes.append(
                            [inst_key, [x_mid - half_width, y, width, margin]]
                        )
                        boxes.append(int(np.sum(section_img == 0)))

                    if sum(i > THRESH for i in boxes) == 0:
                        answer.append(None)
                        empty_.append(all_boxes)
                    elif sum(i > THRESH for i in boxes) > 1:
                        answer.append(None)
                        [
                            multi_.append([inst_key, box[i]])
                            for i in range(len(boxes))
                            if boxes[i] > THRESH
                        ]
                    else:
                        answer.append(int(np.argmax(boxes)) + instance[4])

            else:
                box, boxes, all_boxes = [[] for _ in range(3)]
                x_left = min([i[0] for i in xx])
                y_top = min(yy)
                width_ = max([i[0] for i in xx]) - x_left + width + half_width
                height_ = max(yy) - y_top + margin
                error_box_info[inst_key] = to_ratio(
                    image,
                    [
                        x_left - half_width,
                        y_top - half_width // 2,
                        width_,
                        height_ + half_width,
                    ],
                )
                if instance[-1] == "vv":
                    for x in xx:
                        x_mid = x[0] + x[2] // 2
                        for y in yy:
                            section_img = image_c[
                                y + mod : y + margin - mod,
                                x_mid - half_width + 2 : x_mid + half_width - 2,
                            ]
                            box.append([x_mid - half_width, y, width, margin])
                            all_boxes.append(
                                [inst_key, [x_mid - half_width, y, width, margin]]
                            )
                            boxes.append(int(np.sum(section_img == 0)))
                else:
                    for y in yy:
                        for x in xx:
                            x_mid = x[0] + x[2] // 2
                            section_img = image_c[
                                y + mod : y + margin - mod,
                                x_mid - half_width + 2 : x_mid + half_width - 2,
                            ]
                            box.append([x_mid - half_width, y, width, margin])
                            all_boxes.append(
                                [inst_key, [x_mid - half_width, y, width, margin]]
                            )
                            boxes.append(int(np.sum(section_img == 0)))

                box = box[: instance[5]]
                boxes = boxes[: instance[5]]

                if sum(i > THRESH for i in boxes) == 0:
                    answer.append(None)
                    empty_.append(all_boxes)
                elif sum(i > THRESH for i in boxes) > 1:
                    answer.append(None)
                    [
                        multi_.append([inst_key, box[i]])
                        for i in range(len(boxes))
                        if boxes[i] > THRESH
                    ]
                else:
                    if instance[-1] == "vv":
                        answer.append(str(int(np.argmax(boxes)) + instance[4]).zfill(2))
                    else:
                        answer.append(int(np.argmax(boxes)) + instance[4])

        personal_total[inst_key] = answer
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
                            emp[0][1][2],
                            emp[-1][1][1] - emp[0][1][1] + emp[0][1][3],
                        ],
                    ]
                )

            p_empty = groupby_dict(
                list(map(lambda x: to_ratio(image, x), deepcopy(empty_tot)))
            )
        for name in name_keys:
            full_name, name_error = make_korean_name(personal_total[name])
            personal_total[name] = full_name.ljust(3)
            if name_error == "":
                if isinstance(p_multi, dict):
                    p_multi.pop(name, None)
                if isinstance(p_empty, dict):
                    p_empty.pop(name, None)
    else:
        personal_total = {
            **personal_total,
            **{k: make_korean_name(personal_total[k])[0] for k in name_keys},
        }
    for k, v in personal_total.items():
        if isinstance(v, list):
            personal_total[k] = "".join(list(map(str, v)))
        personal_total[k] = personal_total[k].replace("None", " ")

    personal_order = dict()
    for ind, p in enumerate(personal_total):
        personal_final_list.append(
            {
                "section": "front",
                "totalOrder": ind + 1,
                "type": p,
                "answer": [personal_total[p]],
            }
        )
        personal_order[p] = ind + 1
        total_order = ind + 1
    errTypeDict, errTypeDictCoord = dict(), dict()
    for i in set(list(p_multi) + list(p_empty)):
        if (list(p_multi) + list(p_empty)).count(i) > 1:
            errTypeDict[i] = ["multi", "empty"]
            errTypeDictCoord[i] = p_multi[i] + p_empty[i]
        else:
            if i in list(p_multi):
                errTypeDict[i] = ["multi"]
                errTypeDictCoord[i] = p_multi[i]
            if i in list(p_empty):
                errTypeDict[i] = ["empty"]
                errTypeDictCoord[i] = p_empty[i]

    for err in errTypeDict:
        personal_error_list.append(
            {
                "section": "front",
                "content": "personal",
                "totalOrder": personal_order[err],
                "errType": errTypeDict[err],
                "type": err,
                "boxInfo": error_box_info[err],
            }
        )

    check_list = [
        "개인번호",
        "학생 학년/반/번호",
        "자녀의 학년/반/번호",
        "임시배정번호",
        "학번/기관번호",
        "개인번호/학번",
        "학번",
        "수험번호",
        "응시번호",
    ]
    fatal_list = []
    [fatal_list.append("error") for k in list(errTypeDict) if k in check_list]

    return personal_final_list, personal_error_list, total_order, fatal_list
