import math
import cv2
import numpy as np
from copy import deepcopy
from collections import Counter
import settings


def get_threshold_value(
    image,
    recognition_coord: list,
    omr_list: dict,
    sense_value: int,
    omr_margin,
    answer_max,
    answer_min,
):
    # 판독 위한 기본 정보 셋팅 영역
    (_, image_c) = cv2.threshold(image.copy(), sense_value, 255, cv2.THRESH_BINARY)
    start_point = omr_list["meta"]["start_point"]
    margin = omr_list["meta"]["margin"]
    width = omr_list["meta"]["width"]
    mod = int(margin // 12)
    # mod = 3
    allow_value = settings.allow_value
    _under = int(np.average([i[1] + i[3] for i in recognition_coord]))
    if omr_list["image_idx"] == 34:
        pass
    elif omr_list["image_idx"] == 59:
        _under -= 2
    elif omr_list["image_idx"] in [86, 90]:
        _under -= margin * 2
    elif omr_list["image_idx"] in [79, 80]:
        _under -= margin
        _under += 5
    else:
        _under -= margin

    margin += omr_margin
    line_list = sorted([int(_under + i * margin) for i in range(47)])
    margin = int(margin)

    thresh_min, thresh_max = list(), list()

    for inst_key, instance in omr_list["meta"]["personal_info"].items():
        # y값이 한개일 때 처리
        if len(instance[1]) == 1:
            box, boxes, all_boxes = [[] for _ in range(3)]
            xx = recognition_coord[instance[0][0] : instance[0][1] + 1 : instance[2]]
            yy = line_list[instance[1][0]]
            half_width = width // 2
            if instance[-1] == -1:
                yy = [y - (margin // 2) for y in yy]
            for x in xx:
                x_mid = x[0] + x[2] // 2
                section_img = image_c[
                    yy + mod : yy + margin - mod,
                    x_mid - half_width + 3 : x_mid + half_width - 3,
                ]
                box.append([x_mid - half_width, yy, width, margin])
                boxes.append(int(np.sum(section_img == 0)))
                all_boxes.append([inst_key, [x_mid - half_width, yy, width, margin]])
            black = [i for i in boxes if i >= max(boxes) * allow_value]
            white = [i for i in boxes if i < max(boxes) * allow_value]
            thresh_max += list(set(black))
            thresh_min += list(set(white))
            # t_boxes = list(
            #     set([max(boxes)] + [i for i in boxes if i < max(boxes) * allow_value])
            # )
            # if len(t_boxes) == 1 and t_boxes[0] <= 1:
            #     pass
            # else:
            #     thresh_max.append(t_boxes.pop(np.argmax(t_boxes)))
            # thresh_min += t_boxes

        # x값이 한개일 때 처리
        if len(instance[0]) == 1:
            box, boxes, all_boxes = [[] for _ in range(3)]
            xx = recognition_coord[instance[0][0]]
            yy = line_list[instance[1][0] : instance[1][1] + 1 : instance[2]]
            x_mid = xx[0] + xx[2] // 2
            half_width = width // 2
            if instance[-1] == -1:
                yy = [y - (margin // 2) for y in yy]
            for y in yy:
                section_img = image_c[
                    y + mod : y + margin - mod,
                    x_mid - half_width + 3 : x_mid + half_width - 3,
                ]
                box.append([x_mid - half_width, y, width, margin])
                boxes.append(int(np.sum(section_img == 0)))
                all_boxes.append([inst_key, [x_mid - half_width, y, width, margin]])
            black = [i for i in boxes if i >= max(boxes) * allow_value]
            white = [i for i in boxes if i < max(boxes) * allow_value]
            thresh_max += list(set(black))
            thresh_min += list(set(white))
            # t_boxes = list(
            #     set([max(boxes)] + [i for i in boxes if i < max(boxes) * allow_value])
            # )
            # if len(t_boxes) == 1 and t_boxes[0] <= 1:
            #     pass
            # else:
            #     thresh_max.append(t_boxes.pop(np.argmax(t_boxes)))
            # thresh_min += t_boxes

        # x,y list일 때 처리
        if not len(instance[1]) == 1 and not len(instance[0]) == 1:
            xx = recognition_coord[instance[0][0] : instance[0][1] + 1 : instance[2]]
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

            if len(instance) == 5 or -2 in instance:
                if len(instance[1]) == 4:
                    yy += line_list[instance[1][2] : instance[1][3] + 1]

                for x in xx:
                    box, boxes, all_boxes = [[] for _ in range(3)]
                    x_mid = x[0] + x[2] // 2
                    for y in yy:
                        section_img = image_c[
                            y + mod : y + margin - mod,
                            x_mid - half_width + 3 : x_mid + half_width - 3,
                        ]
                        box.append([x_mid - half_width, y, width, margin])
                        all_boxes.append(
                            [inst_key, [x_mid - half_width, y, width, margin]]
                        )
                        boxes.append(int(np.sum(section_img == 0)))
                    black = [i for i in boxes if i >= max(boxes) * allow_value]
                    white = [i for i in boxes if i < max(boxes) * allow_value]
                    thresh_max += list(set(black))
                    thresh_min += list(set(white))
                    # t_boxes = list(
                    #     set(
                    #         [max(boxes)]
                    #         + [i for i in boxes if i < max(boxes) * allow_value]
                    #     )
                    # )
                    # if len(t_boxes) == 1 and t_boxes[0] <= 1:
                    #     pass
                    # else:
                    #     thresh_max.append(t_boxes.pop(np.argmax(t_boxes)))
                    # thresh_min += t_boxes

            elif instance[-1] == "w":
                for y in yy:
                    box, boxes, all_boxes = [[] for _ in range(3)]
                    for x in xx:
                        x_mid = x[0] + x[2] // 2
                        section_img = image_c[
                            y + mod : y + margin - mod,
                            x_mid - half_width + 3 : x_mid + half_width - 3,
                        ]
                        box.append([x_mid - half_width, y, width, margin])
                        all_boxes.append(
                            [inst_key, [x_mid - half_width, y, width, margin]]
                        )
                        boxes.append(int(np.sum(section_img == 0)))
                    black = [i for i in boxes if i >= max(boxes) * allow_value]
                    white = [i for i in boxes if i < max(boxes) * allow_value]
                    thresh_max += list(set(black))
                    thresh_min += list(set(white))
                    # t_boxes = list(
                    #     set(
                    #         [max(boxes)]
                    #         + [i for i in boxes if i < max(boxes) * allow_value]
                    #     )
                    # )
                    # if len(t_boxes) == 1 and t_boxes[0] <= 1:
                    #     pass
                    # else:
                    #     thresh_max.append(t_boxes.pop(np.argmax(t_boxes)))
                    # thresh_min += t_boxes

            else:
                box, boxes, all_boxes = [[] for _ in range(3)]
                if instance[-1] == "vv":
                    for x in xx:
                        x_mid = x[0] + x[2] // 2
                        for y in yy:
                            section_img = image_c[
                                y + mod : y + margin - mod,
                                x_mid - half_width + 3 : x_mid + half_width - 3,
                            ]
                            box.append([x_mid - half_width, y, width, margin])
                            all_boxes.append(
                                [inst_key, [x_mid - half_width, y, width, margin]]
                            )
                            boxes.append(int(np.sum(section_img == 0)))
                        black = [i for i in boxes if i >= max(boxes) * allow_value]
                        white = [i for i in boxes if i < max(boxes) * allow_value]
                        thresh_max += list(set(black))
                        thresh_min += list(set(white))
                        # t_boxes = list(
                        #     set(
                        #         [max(boxes)]
                        #         + [i for i in boxes if i < max(boxes) * allow_value]
                        #     )
                        # )
                        # if len(t_boxes) == 1 and t_boxes[0] <= 1:
                        #     pass
                        # else:
                        #     thresh_max.append(t_boxes.pop(np.argmax(t_boxes)))
                        # thresh_min += t_boxes
                else:
                    for y in yy:
                        for x in xx:
                            x_mid = x[0] + x[2] // 2
                            section_img = image_c[
                                y + mod : y + margin - mod,
                                x_mid - half_width + 3 : x_mid + half_width - 3,
                            ]
                            box.append([x_mid - half_width, y, width, margin])
                            all_boxes.append(
                                [inst_key, [x_mid - half_width, y, width, margin]]
                            )
                            boxes.append(int(np.sum(section_img == 0)))
                box = box[: instance[5]]
                boxes = boxes[: instance[5]]
                black = [i for i in boxes if i >= max(boxes) * allow_value]
                white = [i for i in boxes if i < max(boxes) * allow_value]
                thresh_max += list(set(black))
                thresh_min += list(set(white))
                # t_boxes = list(
                #     set(
                #         [max(boxes)]
                #         + [i for i in boxes if i < max(boxes) * allow_value]
                #     )
                # )
                # if len(t_boxes) == 1 and t_boxes[0] <= 1:
                #     pass
                # else:
                #     thresh_max.append(t_boxes.pop(np.argmax(t_boxes)))
                # thresh_min += t_boxes
    omr_thresh_max = thresh_max + answer_max
    omr_thresh_min = thresh_min + answer_min
    thresh_min_ratio = len([i for i in omr_thresh_min if i <= 5]) / len(omr_thresh_min)
    omr_thresh_max.sort()
    omr_thresh_min.sort()
    omr_thresh_max = [i for i in omr_thresh_max if i != max(omr_thresh_max)]
    # print(omr_thresh_min)
    # print()
    # print(omr_thresh_max)
    # print()
    # print("thresh_min_ratio : ", thresh_min_ratio)
    if len(omr_thresh_max) == 0:
        return max(omr_thresh_min) + 1, 0, [0], 0
    minor_value_ratio = len(
        [i for i in omr_thresh_max if i < max(omr_thresh_max) * (allow_value * 1)]
    ) / len(omr_thresh_max)
    total_thresh_max = [
        i for i in omr_thresh_max if i >= max(omr_thresh_max) * allow_value
    ]
    # print("minor_value_ratio : ", minor_value_ratio)

    if len([i for i in omr_thresh_max if i < max(omr_thresh_max) * allow_value]) >= int(
        len(omr_thresh_max) * 0.2
    ):
        total_thresh_max = [
            i for i in omr_thresh_max if i >= max(omr_thresh_max) * (allow_value * 0.5)
        ]
    # print(total_thresh_max)
    try:
        if min(total_thresh_max) > max(omr_thresh_min):
            threshold = (min(total_thresh_max) + max(omr_thresh_min)) * 2 // 3
            # threshold = (
            #     max(omr_thresh_min) + (min(total_thresh_max) - max(omr_thresh_min)) // 2
            # )
        else:
            threshold = max(max(omr_thresh_min), min(omr_thresh_max))
            # threshold = 70
    except Exception as e:
        print(e)
        threshold = 30
    # print(
    #     min(omr_thresh_max), max(omr_thresh_min), threshold,
    # )
    return threshold, minor_value_ratio, total_thresh_max, thresh_min_ratio
