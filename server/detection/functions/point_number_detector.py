import cv2
import math
import settings
import numpy as np
from copy import deepcopy
from detection.functions.utils import (
    groupby_dict,
    to_ratio,
)

__all__ = ["point_number_detect"]


def point_number_detect(
    image,
    recognition_coord: list,
    omr_list: dict,
    sense_value: int,
    total_order: int,
    detection_threshold: int,
    omr_margin,
):
    (_, image_c) = cv2.threshold(image.copy(), sense_value, 255, cv2.THRESH_BINARY)

    sub_order = 0
    THRESH = detection_threshold
    start_point = omr_list["meta"]["start_point"]
    margin = omr_list["meta"]["margin"]
    width = omr_list["meta"]["width"]
    mod = int(omr_list["meta"]["margin"] // 12)

    _under = int(np.average([i[1] + i[3] for i in recognition_coord]))
    if omr_list["meta"]["image_idx"] == 34:
        pass
    elif omr_list["meta"]["image_idx"] == 59:
        _under -= 2
    elif omr_list["meta"]["image_idx"] in [86, 90]:
        _under -= margin * 2
    else:
        _under -= margin

    margin += omr_margin
    line_list = sorted([int(_under + i * margin) for i in range(47)])
    margin = int(margin)

    point_number_meta = omr_list["meta"]["point_number"]

    final_val_list, final_error_list, empty_, multi_ = [[] for _ in range(4)]
    o_empty_dict, o_multi_dict = [{} for _ in range(2)]

    for number, instance in enumerate(point_number_meta):
        sub_order += 1
        xx = recognition_coord[
            instance[1][0][0] : instance[1][0][1] + 1 : instance[1][2]
        ]
        yy = line_list[instance[1][1][0] : instance[1][1][1] + 1 : instance[1][3]]
        half_width = width // 2
        point_answer = list()
        for x in xx:
            box, boxes, all_boxes = [[] for _ in range(3)]
            x_mid = x[0] + x[2] // 2
            for y in yy:
                section_img = image_c[
                    y + mod : y + margin - mod,
                    x_mid - half_width + 2 : x_mid + half_width - 2,
                ]
                box.append([x_mid - half_width, y, width, margin])
                all_boxes.append([number + 1, [x_mid - half_width, y, width, margin]])
                boxes.append(int(np.sum(section_img == 0)))

            if sum(i > THRESH for i in boxes) == 0:
                point_answer.append(" ")
                empty_ += all_boxes

            elif sum(i > THRESH for i in boxes) > 1:
                point_answer.append(" ")
                [
                    multi_.append([number + 1, box[i]])
                    for i in range(len(boxes))
                    if boxes[i] > THRESH
                ]
            else:
                point_answer.append(str(int(np.argmax(boxes))))

        Val = [".".join(point_answer)] if " " not in point_answer else [" "]

        final_val_list.append(
            {
                "section": "front",
                "totalOrder": total_order + sub_order,
                "type": "2부",
                "questionNumber": str(instance[0]),
                "answer": Val,
            }
        )

    if multi_:
        o_multi_dict = groupby_dict(
            list(map(lambda x: to_ratio(image, x), deepcopy(multi_)))
        )
        for m in o_multi_dict:
            final_error_list.append(
                {
                    "section": "front",
                    "content": "omr",
                    "errType": ["multi"],
                    "totalOrder": total_order + int(m),
                    "boxInfo": o_multi_dict[m],
                }
            )

    if empty_:
        o_empty_dict = groupby_dict(
            list(map(lambda x: to_ratio(image, x), deepcopy(empty_)))
        )
        for e in o_empty_dict:
            e_box = [
                o_empty_dict[e][0][0],
                o_empty_dict[e][0][1],
                o_empty_dict[e][0][2],
                o_empty_dict[e][-1][1] - o_empty_dict[e][0][1] + o_empty_dict[e][0][3],
            ]
            final_error_list.append(
                {
                    "section": "front",
                    "content": "omr",
                    "errType": ["empty"],
                    "totalOrder": total_order + int(e),
                    "boxInfo": [e_box],
                }
            )
    total_order_front = total_order + sub_order
    return final_val_list, final_error_list, total_order_front
