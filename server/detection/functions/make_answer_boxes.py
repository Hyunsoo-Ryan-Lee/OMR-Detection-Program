import cv2
import numpy as np
import settings

__all__ = ["answer_boxes"]


def answer_boxes(
    image,
    recognition_coord: list,
    question_x_dict: dict,
    question_y_dict: dict,
    omr_list: dict,
    sense_value: int,
    double_sided: bool = False,
):
    (_, image_c) = cv2.threshold(image.copy(), sense_value, 255, cv2.THRESH_BINARY)
    margin = int(omr_list["meta"]["margin"])
    width = int(omr_list["meta"]["width"])
    mod = int(margin // 12)
    allow_value = settings.allow_value
    boxes_dict, box_coords_dict = dict(), dict()
    thresh_min, thresh_max = list(), list()

    if double_sided:
        for n in range(len(omr_list["meta"]["double_sided"]["answer_list_x"])):
            box, boxes, box_coords = [[] for _ in range(3)]
            for idx, xx in enumerate(
                omr_list["meta"]["double_sided"]["answer_list_x"][f"x_{n+1}"][:-1]
            ):
                question_x = recognition_coord[
                    xx[0] : xx[1]
                    + 1 : omr_list["meta"]["double_sided"]["answer_list_x"][f"x_{n+1}"][
                        -1
                    ]
                ]
                for y in question_y_dict[f"y_{n+1}"][
                    : omr_list["meta"]["double_sided"]["answer_number"][f"a_{n+1}"][idx]
                ]:
                    for x in question_x:
                        x_mid = x[0] + x[2] // 2
                        half_width = width // 2
                        section_img = image_c[
                            y + mod : y + margin - mod,
                            x_mid - half_width + 2 : x_mid + half_width - 2,
                        ]
                        box.append(section_img)
                        box_coords.append([x_mid - half_width, y, width, margin])
            boxes_dict[f"b_{n+1}"] = box
            box_coords_dict[f"b_{n+1}"] = box_coords
        return boxes_dict, box_coords_dict

    if omr_list["meta"]["type"] == 1:
        for n in range(len(omr_list["meta"]["answer_list_x"])):
            box, box_coords = [[] for _ in range(2)]
            if "r" in omr_list["meta"]["answer_list_x"][f"x_{n+1}"]:
                for idx, xx in enumerate(
                    omr_list["meta"]["answer_list_x"][f"x_{n+1}"][:-2]
                ):
                    question_x = recognition_coord[
                        xx[0] : xx[1]
                        + 1 : omr_list["meta"]["answer_list_x"][f"x_{n+1}"][-2]
                    ][::-1]
                    for y in question_y_dict[f"y_{n+1}"][
                        : omr_list["meta"]["answer_number"][f"a_{n+1}"][idx]
                    ]:
                        boxes = []
                        for x in question_x:
                            x_mid = x[0] + x[2] // 2
                            half_width = width // 2
                            section_img = image_c[
                                y + mod : y + margin - mod,
                                x_mid - half_width + 2 : x_mid + half_width - 2,
                            ]
                            box.append(section_img)
                            boxes.append(int(np.sum(section_img == 0)))
                            box_coords.append([x_mid - half_width, y, width, margin])
                        t_boxes = list(
                            set(
                                [max(boxes)]
                                + [i for i in boxes if i < max(boxes) * allow_value]
                            )
                        )
                        if len(t_boxes) == 1 and t_boxes[0] <= 1:
                            pass
                        else:
                            thresh_max.append(t_boxes.pop(np.argmax(t_boxes)))
                        thresh_min += t_boxes

            elif "ww" in omr_list["meta"]["answer_list_x"][f"x_{n+1}"]:
                for idx, xx in enumerate(
                    omr_list["meta"]["answer_list_x"][f"x_{n+1}"][:-2]
                ):
                    question_x = recognition_coord[
                        xx[0] : xx[1]
                        + 1 : omr_list["meta"]["answer_list_x"][f"x_{n+1}"][-2]
                    ]
                    for y in question_y_dict[f"y_{n+1}"][
                        : omr_list["meta"]["answer_number"][f"a_{n+1}"][idx]
                    ]:
                        boxes = []
                        for x in question_x:
                            x_mid = x[0] + x[2] // 2
                            half_width = width // 2
                            section_img = image_c[
                                y + mod : y + margin - mod,
                                x_mid - half_width + 2 : x_mid + half_width - 2,
                            ]
                            box.append(section_img)
                            boxes.append(int(np.sum(section_img == 0)))
                            box_coords.append([x_mid - half_width, y, width, margin])
                        t_boxes = list(
                            set(
                                [max(boxes)]
                                + [i for i in boxes if i < max(boxes) * allow_value]
                            )
                        )
                        if len(t_boxes) == 1 and t_boxes[0] <= 1:
                            pass
                        else:
                            thresh_max.append(t_boxes.pop(np.argmax(t_boxes)))
                        thresh_min += t_boxes

            elif (
                "v" in omr_list["meta"]["answer_list_x"][f"x_{n+1}"]
                or "vv" in omr_list["meta"]["answer_list_x"][f"x_{n+1}"]
            ):
                for idx, xx in enumerate(
                    omr_list["meta"]["answer_list_x"][f"x_{n+1}"][:-1]
                ):
                    question_x = recognition_coord[xx[0] : xx[1] + 1]
                    for x in question_x:
                        boxes = []
                        x_mid = x[0] + x[2] // 2
                        half_width = width // 2
                        for y in question_y_dict[f"y_{n+1}"]:
                            section_img = image_c[
                                y + mod : y + margin - mod,
                                x_mid - half_width + 2 : x_mid + half_width - 2,
                            ]
                            box.append(section_img)
                            boxes.append(int(np.sum(section_img == 0)))
                            box_coords.append([x_mid - half_width, y, width, margin])
                        t_boxes = list(
                            set(
                                [max(boxes)]
                                + [i for i in boxes if i < max(boxes) * allow_value]
                            )
                        )
                        if len(t_boxes) == 1 and t_boxes[0] <= 1:
                            pass
                        else:
                            thresh_max.append(t_boxes.pop(np.argmax(t_boxes)))
                        thresh_min += t_boxes
            else:
                for idx, xx in enumerate(
                    omr_list["meta"]["answer_list_x"][f"x_{n+1}"][:-1]
                ):
                    question_x = recognition_coord[
                        xx[0] : xx[1]
                        + 1 : omr_list["meta"]["answer_list_x"][f"x_{n+1}"][-1]
                    ]
                    for y in question_y_dict[f"y_{n+1}"][
                        : omr_list["meta"]["answer_number"][f"a_{n+1}"][idx]
                    ]:
                        boxes = []
                        for x in question_x:
                            x_mid = x[0] + x[2] // 2
                            half_width = width // 2
                            section_img = image_c[
                                y + mod : y + margin - mod,
                                x_mid - half_width + 2 : x_mid + half_width - 2,
                            ]
                            box.append(section_img)
                            boxes.append(int(np.sum(section_img == 0)))
                            box_coords.append([x_mid - half_width, y, width, margin])
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
            boxes_dict[f"b_{n+1}"] = box
            box_coords_dict[f"b_{n+1}"] = box_coords

    if omr_list["meta"]["type"] == 2:
        for n in range(len(question_x_dict)):
            box, box_coords = [[] for _ in range(2)]
            xx = question_x_dict[f"x_{n+1}"]
            # Check vertical
            if "v" in xx or "vv" in xx:
                boxes = []
                for yy in question_y_dict[f"y_{n+1}"]:
                    x_mid = xx[0] + xx[2] // 2
                    half_width = width // 2
                    section_img = image_c[
                        yy + mod : yy + margin - mod,
                        x_mid - half_width + 2 : x_mid + half_width - 2,
                    ]
                    box.append(section_img)
                    boxes.append(int(np.sum(section_img == 0)))
                    box_coords.append([x_mid - half_width, yy, width, margin])
                t_boxes = list(
                    set(
                        [max(boxes)]
                        + [i for i in boxes if i < max(boxes) * allow_value]
                    )
                )
                if len(t_boxes) == 1 and t_boxes[0] <= 1:
                    pass
                else:
                    thresh_max.append(t_boxes.pop(np.argmax(t_boxes)))
                thresh_min += t_boxes
            else:
                for yy in question_y_dict[f"y_{n+1}"]:
                    boxes = []
                    for xx in question_x_dict[f"x_{n+1}"]:
                        x_mid = xx[0] + xx[2] // 2
                        half_width = width // 2
                        section_img = image_c[
                            yy + mod : yy + margin - mod,
                            x_mid - half_width + 2 : x_mid + half_width - 2,
                        ]
                        box.append(section_img)
                        boxes.append(int(np.sum(section_img == 0)))
                        box_coords.append([x_mid - half_width, yy, width, margin])
                    t_boxes = list(
                        set(
                            [max(boxes)]
                            + [i for i in boxes if i < max(boxes) * allow_value]
                        )
                    )
                    # if omr_list["meta"]["question_title"][f"t_{n+1}"] == "언어이해력(독해력)":
                    #     print(boxes)
                    if len(t_boxes) == 1 and t_boxes[0] <= 1:
                        pass
                    else:
                        thresh_max.append(t_boxes.pop(np.argmax(t_boxes)))
                    thresh_min += t_boxes

            boxes_dict[f"b_{n+1}"] = box
            box_coords_dict[f"b_{n+1}"] = box_coords

    return boxes_dict, box_coords_dict, thresh_max, thresh_min
