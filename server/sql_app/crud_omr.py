import json
from datetime import datetime
from pytz import timezone
from sql_app.database import metadata, answer, result
from bson import json_util
from bson.objectid import ObjectId
import time
from detection.functions.coordinate_x import get_x_coordinate
from detection.controller import start_detection

from utils.common import (
    get_s3,
    get_s3_client,
    get_bucketName,
    get_image,
    get_error_type,
    make_total_txt,
    rename_omr,
)


__all__ = [
    "delete_all_results",
    "get_metadata",
    "save_result",
    "send_all_result",
    "send_final_result",
    "send_individual_result",
]


async def delete_all_results():
    metadata.delete_many({})


async def get_metadata():
    meta_list, ordered_meta = list(), list()
    key_list = ["content_level", "content"]
    meta_order = ["유아", "초등", "중등", "고등", "대학", "성인", "기업", "종합"]
    cursor = metadata.find({})
    async for document in cursor:
        document = json.loads(json_util.dumps(document))
        meta_document = {k: v for (k, v) in document.items() if k in key_list}
        meta_document["objectId"] = document["_id"]["$oid"]
        meta_list.append(meta_document)
    meta_list.sort(key=lambda x: (x["content_level"], x["content"]))
    for m in meta_order:
        for d in meta_list:
            if d["content_level"] == m:
                ordered_meta.append(d)

    return ordered_meta


async def save_result(omr, response_ans):
    start = time.time()
    await answer.insert_one(response_ans)  # For test
    # 저장된 판독에 대한 answerId 추출
    cursor = answer.find({}).sort("_id", -1).limit(1)
    async for document in cursor:
        answerId = json.loads(json_util.dumps(document["_id"]))
        s3_path = document["s3_path"]
        objectId = omr["objectId"]
    omr_count = 0
    s3 = get_s3()
    bucketName = get_bucketName()
    bucket = s3.Bucket(bucketName)
    document = await metadata.find_one({"_id": ObjectId(objectId)})
    bucket = s3.Bucket(bucketName)
    path_prefix = s3_path[s3_path.index(bucketName) + len(bucketName) + 1 :]
    print(bucketName)
    s3_path_dir, image_direction = list(), list()
    double_sided = bool()
    for omr in bucket.objects.filter(Prefix=path_prefix):
        s3_path_dir.append(omr.key)

    s3_path_dir = [omr for omr in s3_path_dir if "jpg" in omr or "JPG" in omr]
    s3_path_dir = sorted(
        s3_path_dir, key=lambda x: str(x.split("/")[-1].split(".")[0]).zfill(3)
    )
    s3_path_dir = s3_path_dir[:1]
    if not document["double_sided_check"]:
        double_sided = False
        inspect_val = True
        inspect_trial = 0
        while inspect_val:
            # for s in s3_path_dir:
            _, _, recognition_coord, _ = get_x_coordinate(
                get_image(bucketName, s3_path_dir[0]),
                document["meta"]["height_point"],
                document["meta"]["recog_point"],
                document["meta"]["recog_diff"],
                document["meta"]["recog_len"],
            )
            if len(recognition_coord) == 0:
                s3_path_dir = s3_path_dir[1:] + [s3_path_dir[0]]
                inspect_trial += 1
            else:
                break
            if inspect_trial == len(s3_path_dir):
                return False, False, False, False
        for omr in s3_path_dir:
            print(omr.split("/")[-1])
            image_list = [get_image(bucketName, omr)]
            s3PathDetail = {"front": f"s3://{bucketName}/" + omr}
            omr_count += 1
            try:
                (
                    total_value,
                    total_error,
                    special_back,
                    direction,
                    fatal_list,
                ) = start_detection(image_list, document)

                image_direction.append(direction)
                errorType = get_error_type(total_error)
                if "error" in fatal_list:
                    errorType.append("fatal_error")

                response = {
                    "answerId": answerId["$oid"],
                    "s3PathDetail": s3PathDetail,
                    "valueList": total_value,
                    "errorType": errorType,
                    "errorList": total_error,
                    "specialBack": special_back,
                }
                result.insert_one(response)
            except Exception as e:
                print(e)

    else:
        double_sided = True
        inspect_val = True
        inspect_trial = 0
        while inspect_val:
            _, _, recognition_coord, _ = get_x_coordinate(
                get_image(bucketName, s3_path_dir[0]),
                document["meta"]["height_point"],
                document["meta"]["recog_point"],
                document["meta"]["recog_diff"],
                document["meta"]["recog_len"],
            )
            if len(recognition_coord) == 0:
                s3_path_dir = s3_path_dir[2:] + [s3_path_dir[0], s3_path_dir[1]]
                inspect_trial += 1
            else:
                break
            if inspect_trial == len(s3_path_dir) // 2:
                return False, False, False, False
        for omr_idx in range(0, len(s3_path_dir), 2):
            front_page = s3_path_dir[omr_idx]
            back_page = s3_path_dir[omr_idx + 1]
            print(front_page.split("/")[-1])
            omr_count += 1
            s3PathDetail = {
                "front": f"s3://{bucketName}/" + front_page,
                "back": f"s3://{bucketName}/" + back_page,
            }
            front_img = get_image(bucketName, front_page)
            back_img = get_image(bucketName, back_page)
            image_list = [front_img, back_img]
            (
                total_value,
                total_error,
                specialBack,
                direction,
                fatal_list,
            ) = start_detection(image_list, document, double_sided)
            image_direction.append(direction)
            errorType = get_error_type(total_error)
            if "error" in fatal_list:
                errorType.append("fatal_error")
            response = {
                "answerId": answerId["$oid"],
                "s3PathDetail": s3PathDetail,
                "valueList": total_value,
                "errorType": errorType,
                "errorList": total_error,
                "specialBack": specialBack,
            }
            result.insert_one(response)
    print()
    print(
        "판독 완료 시간 : ",
        datetime.now(timezone("Asia/Seoul")).strftime("%Y.%m.%d %H:%M:%S"),
    )
    print("판독 경로 : ", "/".join(s3_path_dir[0].split("/")[:-1]))
    print(f"판독 개수 : {omr_count} 개")
    print(f"판독 시간 : {round(time.time() - start, 2)} 초")
    print("answerId : ", answerId["$oid"])
    return answerId["$oid"], s3_path_dir, image_direction, double_sided


async def send_all_result(answerId: str):
    result_list = list()
    key_list = ["s3PathDetail", "valueList", "errorType", "errorList", "specialBack"]

    cursor = result.find({"answerId": answerId})
    async for document in cursor:
        document = json.loads(json_util.dumps(document))
        final_document = {k: v for (k, v) in document.items() if k in key_list}
        final_document["result_id"] = document["_id"]["$oid"]
        result_list.append(final_document)

    return result_list


async def send_final_result(answer_id):
    bucketName = get_bucketName()
    finalResult, s3nameBefore, s3nameAfter = [[] for _ in range(3)]

    cursor = result.find({"answerId": answer_id})
    # omrCount = await result.count_documents({"answerId": answer_id})
    document = await answer.find_one({"_id": ObjectId(answer_id)})
    metaDocs = await metadata.find_one({"_id": ObjectId(document["objectId"])})
    personal_info = metaDocs["meta"]["personal_info"]
    doc_idx = 0

    if "txt_fill" in metaDocs.keys():
        txt_fill = metaDocs["txt_fill"]
        async for document in cursor:
            doc_idx += 1
            document = json.loads(json_util.dumps(document))
            rename_dict = dict()
            s3Path = document["s3PathDetail"]
            for s in s3Path:
                s3nameBefore.append(
                    s3Path[s][s3Path[s].index(bucketName) + len(bucketName) + 1 :]
                )
            sub_txt = ""
            for val in document["valueList"]:
                if val["totalOrder"] <= metaDocs["personal_idx"]:
                    if metaDocs["content_level"] in ["유아", "초등", "중등", "고등", "대학"] and (
                        "개인번호" in val["type"]
                        or "학년/반/번호" in val["type"]
                        or "학번" in val["type"]
                    ):
                        if "*" in val["answer"][0]:
                            return False, False, False, False
                    val["answer"] = [val["answer"][0].replace(" ", "0")]
                    rename_dict[val["totalOrder"]] = val["answer"][0]
                    if "성명" in val["type"] or "이름" in val["type"]:
                        val["answer"] = [val["answer"][0].replace("0", " ").ljust(3)]
                    if val["totalOrder"] == metaDocs["txt_order"][0]:
                        sub_txt += str(*val["answer"]) + "*****"
                    elif val["totalOrder"] == metaDocs["txt_order"][1]:
                        sub_txt += str(*val["answer"]) + "|"
                    else:
                        sub_txt += str(*val["answer"])

                else:
                    if (
                        str(val["totalOrder"]) in txt_fill.keys()
                        and txt_fill[str(val["totalOrder"])] >= 10
                    ):
                        sub_txt += "".join(
                            [
                                str(i).zfill(2)
                                if str(i).zfill(2) in val["answer"]
                                else "00"
                                for i in range(1, txt_fill[str(val["totalOrder"])] + 1)
                            ]
                        )
                    elif (
                        str(val["totalOrder"]) in txt_fill.keys()
                        and txt_fill[str(val["totalOrder"])] > 0
                        and txt_fill[str(val["totalOrder"])] < 10
                    ):
                        sub_txt += "".join(
                            [
                                str(i) if str(i) in val["answer"] else "0"
                                for i in range(1, txt_fill[str(val["totalOrder"])] + 1)
                            ]
                        )
                    elif (
                        str(val["totalOrder"]) in txt_fill.keys()
                        and txt_fill[str(val["totalOrder"])] == 0
                        and (
                            val["answer"] == [" "]
                            or len(val["answer"]) > 1
                            or " " in val["answer"][0]
                        )
                    ):
                        sub_txt += "00"
                    else:
                        if len(val["answer"]) > 1:
                            val["answer"] = ["0"]
                        if val["answer"] == [" "]:
                            val["answer"] = ["0"]
                        if " " in val["answer"][0]:
                            val["answer"] = ["0"]
                        sub_txt += str(*val["answer"])
                        # for v in val["answer"]:
                        #     sub_txt += str(v)
            sub_txt += metaDocs["txt_order"][-1]
            finalResult.append(sub_txt)

            rename = rename_omr(metaDocs, metaDocs["rename_order"], rename_dict)

            if metaDocs["double_sided_check"]:
                s3nameAfter.append(f"{rename}_{doc_idx}_1")
                s3nameAfter.append(f"{rename}_{doc_idx}_2")
            else:
                s3nameAfter.append(f"{rename}_{doc_idx}")

    else:
        async for document in cursor:
            doc_idx += 1
            document = json.loads(json_util.dumps(document))
            rename_dict = dict()
            s3Path = document["s3PathDetail"]
            for s in s3Path:
                s3nameBefore.append(
                    s3Path[s][s3Path[s].index(bucketName) + len(bucketName) + 1 :]
                )

            if "right" in metaDocs["txt_order"]:
                sub_txt, rename_dict = make_total_txt(
                    document,
                    metaDocs["personal_idx"],
                    metaDocs["txt_order"],
                    rename_dict,
                    metaDocs["content_level"],
                    metaDocs["meta"]["personal_info"],
                    "right",
                )
                if sub_txt == False:
                    return False, False, False, False
            elif "left" in metaDocs["txt_order"]:
                sub_txt, rename_dict = make_total_txt(
                    document,
                    metaDocs["personal_idx"],
                    metaDocs["txt_order"],
                    rename_dict,
                    metaDocs["content_level"],
                    metaDocs["meta"]["personal_info"],
                    "left",
                )
                if sub_txt == False:
                    return False, False, False, False
            else:
                sub_txt, rename_dict = make_total_txt(
                    document,
                    metaDocs["personal_idx"],
                    metaDocs["txt_order"],
                    rename_dict,
                    metaDocs["content_level"],
                    metaDocs["meta"]["personal_info"],
                )
                if sub_txt == False:
                    return False, False, False, False

            finalResult.append(sub_txt)
            # print(sub_txt[11:14], len(sub_txt))
            rename = rename_omr(metaDocs, metaDocs["rename_order"], rename_dict)
            if metaDocs["double_sided_check"]:
                s3nameAfter.append(f"{rename}_{doc_idx}_1")
                s3nameAfter.append(f"{rename}_{doc_idx}_2")
            else:
                s3nameAfter.append(f"{rename}_{doc_idx}")
    file_name = s3nameBefore[0].split("/")[-2]
    return "\n".join(finalResult), file_name, s3nameBefore, s3nameAfter


def rename_s3_images(answer_id, modified_date, s3nameBefore, s3nameAfter):
    print("start renaming!")
    answer.update_one(
        {"_id": ObjectId(answer_id)}, {"$set": {"modified_date": modified_date}}
    )
    bucket = get_bucketName()
    for ind, omrJpg in enumerate(s3nameBefore):
        if omrJpg.split("/")[-1].split(".")[0] != s3nameAfter[ind]:
            copy_source = {"Bucket": bucket, "Key": omrJpg}
            path = "/".join(omrJpg.split("/")[:-1])
            get_s3_client().copy_object(
                CopySource=copy_source,
                Bucket=bucket,
                Key=f"{path}/{s3nameAfter[ind]}.jpg",
            )
            get_s3_client().delete_object(Bucket=bucket, Key=omrJpg)

