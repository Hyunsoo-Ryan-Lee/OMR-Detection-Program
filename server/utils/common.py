import cv2
import boto3
import settings
import numpy as np
from math import ceil
from detection.functions.utils import read_image_from_s3

__all__ = ["get_s3", "get_s3_client", "get_bucketName", "get_image", "get_error_type"]


def get_s3():
    s3 = boto3.resource(
        "s3",
        region_name=settings.AWS_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    return s3


def get_s3_client():
    s3_client = boto3.client(
        "s3",
        region_name=settings.AWS_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    return s3_client


def get_bucketName():
    bucketName = settings.AWS_S3_BUCKET_NAME

    return bucketName


def get_image(bucketName, omr_img=None):
    result = np.asarray(read_image_from_s3(bucketName, omr_img))

    if len(result.shape) == 3:
        image = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        result = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return result


def get_error_type(total_error):
    error_type = []
    if len(total_error) == 0:
        return error_type
    else:
        for err in total_error:
            if err["content"] == "personal" and "multi" in err["errType"]:
                error_type += ["personal_error", "multi_error"]
            if err["content"] == "personal" and "empty" in err["errType"]:
                error_type += ["personal_error", "empty_error"]
            if err["content"] == "omr" and "multi" in err["errType"]:
                error_type += ["multi_error"]
            if err["content"] == "omr" and "empty" in err["errType"]:
                error_type += ["empty_error"]

    return list(set(error_type))


def make_total_txt(
    values,
    personal_idx,
    txt_order,
    rename_dict,
    content_level,
    personal_info,
    order: bool = False,
):
    sub_txt = ""
    fill_list = [
        "1.적성흥미",
        "2.학습태도",
        "3.갈등대처",
        "1.대인관계시 모습",
        "2.협동방식",
        "3.갈등대처양식",
        "희망직업",
        "대표강점",
    ]
    if not order:
        # print(values["valueList"])
        for val in values["valueList"]:
            if val["totalOrder"] <= personal_idx:
                if "vv" in personal_info[list(personal_info)[val["totalOrder"] - 1]]:
                    if len(val["answer"]) > 1:
                        val["answer"] = ["00"]
                    else:
                        val["answer"] = [val["answer"][0].replace(" ", "00")]
                        val["answer"] = [val["answer"][0].zfill(2)]

                if content_level in ["유아", "초등", "중등", "고등", "대학"] and (
                    "개인번호" in val["type"]
                    or "학년/반/번호" in val["type"]
                    or "학번" in val["type"]
                ):
                    if "*" in val["answer"][0]:
                        return False, False
                val["answer"] = [val["answer"][0].replace(" ", "0")]
                rename_dict[val["totalOrder"]] = val["answer"][0]
                if "성명" in val["type"] or "이름" in val["type"]:
                    val["answer"] = [val["answer"][0].replace("0", " ").ljust(3)]
                if val["totalOrder"] == txt_order[0]:
                    sub_txt += str(*val["answer"]) + "*****"
                elif val["totalOrder"] == txt_order[1]:
                    sub_txt += str(*val["answer"]) + "|"
                else:
                    sub_txt += str(*val["answer"])
            else:
                if val["type"] in fill_list:
                    if len(val["answer"]) > 1:
                        val["answer"] = ["00"]
                    if val["answer"] == [" "]:
                        val["answer"] = ["00"]
                    if " " in val["answer"][0]:
                        val["answer"] = ["00"]
                    else:
                        val["answer"] = [val["answer"][0].zfill(2)]
                if len(val["answer"]) > 1:
                    val["answer"] = ["0"]
                if val["answer"] == [" "]:
                    val["answer"] = ["0"]
                if " " in val["answer"][0]:
                    if val["type"] in [
                        "PART2 진학전략_진학희망지역",
                        "PART2 진학전략_희망대학1",
                        "PART2 진학전략_희망대학2",
                        "PART2 진학전략_희망대학3",
                        "PART2 진학전략_내신성적_국어",
                        "PART2 진학전략_내신성적_수학",
                        "PART2 진학전략_내신성적_영어",
                        "PART2 진학전략_내신성적_사회",
                        "PART2 진학전략_내신성적_과학",
                        "PART2 진학전략_수능성적_국어",
                        "PART2 진학전략_수능성적_수학",
                        "PART2 진학전략_수능성적_탐구",
                        "PART2 진학전략_수능성적_영어",
                        "PART2 진학전략_수능성적_한국사",
                        "PART4 비교과 준비도1",
                    ]:
                        val["answer"] = [val["answer"][0].replace(" ", "0")]
                    else:
                        val["answer"] = ["0"]
                sub_txt += str(*val["answer"])
        sub_txt += "".join(values["specialBack"])
        sub_txt += txt_order[-1]
        return sub_txt, rename_dict

    elif order == "right":
        for val in values["valueList"]:
            if val["totalOrder"] <= personal_idx:
                if content_level in ["유아", "초등", "중등", "고등", "대학"] and (
                    "개인번호" in val["type"]
                    or "학년/반/번호" in val["type"]
                    or "학번" in val["type"]
                ):
                    if "*" in val["answer"][0]:
                        return False, False
                val["answer"] = [val["answer"][0].replace(" ", "0")]
                rename_dict[val["totalOrder"]] = val["answer"][0]
                if "성명" in val["type"] or "이름" in val["type"]:
                    val["answer"] = [val["answer"][0].replace("0", " ").ljust(3)]
                if val["totalOrder"] == txt_order[0]:
                    sub_txt += str(*val["answer"]) + "*****"
                elif val["totalOrder"] == txt_order[1]:
                    sub_txt += str(*val["answer"]) + "|"
                elif val["totalOrder"] == txt_order[2]:
                    sub_txt += str(*val["answer"]) + "|"
                else:
                    sub_txt += str(*val["answer"])
            else:
                if len(val["answer"]) > 1:
                    val["answer"] = ["0"]
                if val["answer"] == [" "]:
                    val["answer"] = ["0"]
                if " " in val["answer"][0]:
                    val["answer"] = ["0"]
                sub_txt += str(*val["answer"])
        sub_txt += txt_order[-1]
        return sub_txt, rename_dict

    elif order == "left":
        for val in values["valueList"]:
            if val["totalOrder"] <= personal_idx:
                if content_level in ["유아", "초등", "중등", "고등", "대학"] and (
                    "개인번호" in val["type"]
                    or "학년/반/번호" in val["type"]
                    or "학번" in val["type"]
                ):
                    if "*" in val["answer"][0]:
                        return False, False
                val["answer"] = [val["answer"][0].replace(" ", "0")]
                rename_dict[val["totalOrder"]] = val["answer"][0]
                if "성명" in val["type"] or "이름" in val["type"]:
                    val["answer"] = [val["answer"][0].replace("0", " ").ljust(3)]
                if val["totalOrder"] == txt_order[0]:
                    sub_txt += str(*val["answer"]) + "|"
                elif val["totalOrder"] == txt_order[1]:
                    sub_txt += str(*val["answer"]) + "*****"
                elif val["totalOrder"] == txt_order[2]:
                    sub_txt += str(*val["answer"]) + "|"
                else:
                    sub_txt += str(*val["answer"])
            else:
                if len(val["answer"]) > 1:
                    val["answer"] = ["0"]
                if val["answer"] == [" "]:
                    val["answer"] = ["0"]
                if " " in val["answer"][0]:
                    val["answer"] = ["0"]
                sub_txt += str(*val["answer"])
        sub_txt += txt_order[-1]
        return sub_txt, rename_dict


def rename_omr(metaDocs, rename_order, rename_dict):

    if metaDocs["double_sided_check"]:
        if metaDocs["content_level"] == "대학":
            rename = "_".join([rename_dict[r] for r in rename_order])
            return rename
        else:
            name = ""
            for r in rename_order[:-1]:
                name += rename_dict[r]
            rename = "_".join(
                [name[0], name[1:3], name[3:], rename_dict[rename_order[-1]]]
            )
            return rename

    elif metaDocs["image_idx"] in [62, 63, 64]:
        rename = "_".join([rename_dict[r] for r in rename_order])
        return rename

    elif metaDocs["content_level"] in ["유아", "초등", "중등", "고등"]:
        name = ""
        for r in rename_order[:-1]:
            name += rename_dict[r]
        rename = "_".join([name[0], name[1:3], name[3:], rename_dict[rename_order[-1]]])
        return rename
    else:
        rename = "_".join([rename_dict[r] for r in rename_order])
        return rename


def rotate_s3_images(s3_path_dir, image_direction):
    # if len(image_direction) == image_direction.count(""):
    #     pass
    # else:
    for idx, img_dir in enumerate(image_direction):
        if img_dir:
            img = np.asarray(read_image_from_s3(get_bucketName(), s3_path_dir[idx]))
            if img_dir == "ccw":
                img = cv2.resize(
                    cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE),
                    (settings.resize_width, settings.resize_height),
                )
                img = cv2.imencode(".jpg", img)[1].tobytes()
            elif img_dir == "cw":
                img = cv2.resize(
                    cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE),
                    (settings.resize_width, settings.resize_height),
                )
                img = cv2.imencode(".jpg", img)[1].tobytes()
        else:
            img = np.asarray(read_image_from_s3(get_bucketName(), s3_path_dir[idx]))
            img = cv2.imencode(".jpg", img)[1].tobytes()

        get_s3_client().delete_object(Bucket=get_bucketName(), Key=s3_path_dir[idx])
        get_s3_client().put_object(
            Bucket=get_bucketName(),
            Key=s3_path_dir[idx],
            Body=img,
            ContentType="image/jpg",
        )


def rotate_s3_double_images(s3_path_dir, image_direction):
    for idx, img_dir in enumerate(image_direction):
        if img_dir:
            img_front = np.asarray(
                read_image_from_s3(get_bucketName(), s3_path_dir[idx * 2])
            )
            img_back = np.asarray(
                read_image_from_s3(get_bucketName(), s3_path_dir[idx * 2 + 1])
            )
            if img_dir == "ccw":
                img_front = cv2.resize(
                    cv2.rotate(img_front, cv2.ROTATE_90_COUNTERCLOCKWISE),
                    (settings.resize_width, settings.resize_height),
                )
                img_back = cv2.resize(
                    cv2.rotate(img_back, cv2.ROTATE_90_COUNTERCLOCKWISE),
                    (settings.resize_width, settings.resize_height),
                )
                img_front = cv2.imencode(".jpg", img_front)[1].tobytes()
                img_back = cv2.imencode(".jpg", img_back)[1].tobytes()
            elif img_dir == "cw":
                img_front = cv2.resize(
                    cv2.rotate(img_front, cv2.ROTATE_90_COUNTERCLOCKWISE),
                    (settings.resize_width, settings.resize_height),
                )
                img_back = cv2.resize(
                    cv2.rotate(img_back, cv2.ROTATE_90_COUNTERCLOCKWISE),
                    (settings.resize_width, settings.resize_height),
                )
                img_front = cv2.imencode(".jpg", img_front)[1].tobytes()
                img_back = cv2.imencode(".jpg", img_back)[1].tobytes()
        else:
            img_front = np.asarray(
                read_image_from_s3(get_bucketName(), s3_path_dir[idx * 2])
            )
            img_back = np.asarray(
                read_image_from_s3(get_bucketName(), s3_path_dir[idx * 2 + 1])
            )
            img_front = cv2.imencode(".jpg", img_front)[1].tobytes()
            img_back = cv2.imencode(".jpg", img_back)[1].tobytes()

        get_s3_client().delete_object(Bucket=get_bucketName(), Key=s3_path_dir[idx * 2])
        get_s3_client().delete_object(
            Bucket=get_bucketName(), Key=s3_path_dir[idx * 2 + 1]
        )
        get_s3_client().put_object(
            Bucket=get_bucketName(),
            Key=s3_path_dir[idx * 2],
            Body=img_front,
            ContentType="image/jpg",
        )
        get_s3_client().put_object(
            Bucket=get_bucketName(),
            Key=s3_path_dir[idx * 2 + 1],
            Body=img_back,
            ContentType="image/jpg",
        )


# def rotate_s3_double_images(s3_path_dir, image_direction):
#     if ceil(len(image_direction) / 2) == int(image_direction.count("")):
#         pass
#     else:
#         for idx, img_dir in enumerate(image_direction):
#             if img_dir:
#                 img_front = np.asarray(
#                     read_image_from_s3(get_bucketName(), s3_path_dir[idx * 2])
#                 )
#                 img_back = np.asarray(
#                     read_image_from_s3(get_bucketName(), s3_path_dir[idx * 2 + 1])
#                 )
#                 if img_dir == "ccw":
#                     img_front = cv2.resize(
#                         cv2.rotate(img_front, cv2.ROTATE_90_COUNTERCLOCKWISE),
#                         (settings.resize_width, settings.resize_height),
#                     )
#                     img_back = cv2.resize(
#                         cv2.rotate(img_back, cv2.ROTATE_90_COUNTERCLOCKWISE),
#                         (settings.resize_width, settings.resize_height),
#                     )
#                     img_front = cv2.imencode(".jpg", img_front)[1].tobytes()
#                     img_back = cv2.imencode(".jpg", img_back)[1].tobytes()
#                 elif img_dir == "cw":
#                     img_front = cv2.resize(
#                         cv2.rotate(img_front, cv2.ROTATE_90_COUNTERCLOCKWISE),
#                         (settings.resize_width, settings.resize_height),
#                     )
#                     img_back = cv2.resize(
#                         cv2.rotate(img_back, cv2.ROTATE_90_COUNTERCLOCKWISE),
#                         (settings.resize_width, settings.resize_height),
#                     )
#                     img_front = cv2.imencode(".jpg", img_front)[1].tobytes()
#                     img_back = cv2.imencode(".jpg", img_back)[1].tobytes()

#                 get_s3_client().delete_object(
#                     Bucket=get_bucketName(), Key=s3_path_dir[idx * 2]
#                 )
#                 get_s3_client().delete_object(
#                     Bucket=get_bucketName(), Key=s3_path_dir[idx * 2 + 1]
#                 )
#                 get_s3_client().put_object(
#                     Bucket=get_bucketName(),
#                     Key=s3_path_dir[idx * 2],
#                     Body=img_front,
#                     ContentType="image/jpg",
#                 )
#                 get_s3_client().put_object(
#                     Bucket=get_bucketName(),
#                     Key=s3_path_dir[idx * 2 + 1],
#                     Body=img_back,
#                     ContentType="image/jpg",
#                 )
