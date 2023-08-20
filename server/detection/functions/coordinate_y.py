import math
from collections import Counter
import numpy as np

__all__ = ["get_y_coordinate"]


def get_y_coordinate(
    recognition_coord: list, omr_list: dict, omr_margin, double_sided: bool = False,
):
    question_x_dict = dict()
    question_y_dict = dict()
    # y_freq = sorted(
    #     dict(Counter([i[1] for i in recognition_coord])).items(),
    #     key=lambda item: -item[1],
    # )[0][0]
    start_point = omr_list["meta"]["start_point"]
    margin = omr_list["meta"]["margin"]
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
    dict_int = 0

    if double_sided:
        for n in range(len(omr_list["meta"]["double_sided"]["answer_list_y"])):
            question_y = list()
        for i in omr_list["meta"]["double_sided"]["answer_list_y"][f"y_{n+1}"][:-1]:
            question_y += line_list[
                i[0] : i[1]
                + 1 : omr_list["meta"]["double_sided"]["answer_list_y"][f"y_{n+1}"][-1]
            ]
        question_y_dict[f"y_{n+1}"] = question_y

        return question_x_dict, question_y_dict

    if omr_list["meta"]["type"] == 2:
        for n in range(len(omr_list["meta"]["answer_list_y"])):
            if (
                "v" in omr_list["meta"]["answer_list_x"][f"x_{n+1}"]
                or "vv" in omr_list["meta"]["answer_list_x"][f"x_{n+1}"]
            ):
                question_x = recognition_coord[
                    omr_list["meta"]["answer_list_x"][f"x_{n+1}"][0]
                ] + ["v"]
                question_x_dict[f"x_{dict_int+1}"] = question_x
                y_index = omr_list["meta"]["answer_list_y"][f"y_{n+1}"][0]
                question_y = line_list[y_index[0] : y_index[1] + 1]
                question_y_dict[f"y_{dict_int+1}"] = question_y
                dict_int += 1
            else:
                for nn in range(len(omr_list["meta"]["answer_list_y"][f"y_{n+1}"])):
                    question_x, question_y = list(), list()
                    for i in omr_list["meta"]["answer_list_y"][f"y_{n+1}"][f"r_{nn+1}"][
                        :-1
                    ]:
                        question_y += line_list[
                            i[0] : i[1]
                            + 1 : omr_list["meta"]["answer_list_y"][f"y_{n+1}"][
                                f"r_{nn+1}"
                            ][-1]
                        ]
                        dict_int += 1
                        question_y_dict[f"y_{dict_int}"] = question_y

                    for j in omr_list["meta"]["answer_list_x"][f"x_{n+1}"][f"r_{nn+1}"][
                        :-1
                    ]:
                        question_x = recognition_coord[j[0] : j[1] + 1]
                        question_x_dict[f"x_{dict_int}"] = question_x

    else:
        for n in range(len(omr_list["meta"]["answer_list_y"])):
            question_y = list()
            for i in omr_list["meta"]["answer_list_y"][f"y_{n+1}"][:-1]:
                question_y += line_list[
                    i[0] : i[1] + 1 : omr_list["meta"]["answer_list_y"][f"y_{n+1}"][-1]
                ]
            question_y_dict[f"y_{n+1}"] = question_y

    return question_x_dict, question_y_dict

