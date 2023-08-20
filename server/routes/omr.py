from datetime import datetime
from pytz import timezone

from fastapi import APIRouter, Body, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sql_app.schema import omr_saveAnswer
from sql_app.crud_omr import (
    delete_all_results,
    get_metadata,
    save_result,
    send_final_result,
    rename_s3_images,
)

from utils.common import rotate_s3_images, rotate_s3_double_images

from sql_app.database import result, answer, metadata
from bson import json_util
from bson.objectid import ObjectId
import json


router = APIRouter()


## collection 내용 삭제
@router.delete("/delete", response_class=JSONResponse, name="collection 내용 삭제")
async def delete_results():
    await delete_all_results()


@router.get("/index", response_class=JSONResponse, name="판독 대상/검사 정보")
async def get_meta_list():
    response = await get_metadata()
    return {"status": True, "data": response}


## answer collection에 검사 실행 내역 저장
@router.post("/answer/", response_class=JSONResponse, name="answer collection 저장")
async def save_answer(
    background_tasks: BackgroundTasks, omr: omr_saveAnswer = Body(...)
):
    omr = jsonable_encoder(omr)
    # print(datetime.now(timezone("Asia/Seoul")).strftime("%Y.%m.%d %H:%M:%S"))
    response_ans = {
        "objectId": omr["objectId"],
        "s3_path": omr["s3_path"],
        "user_id": omr["user_id"],
        "datetime": datetime.now(timezone("Asia/Seoul")).strftime("%Y.%m.%d:%H:%M:%S"),
        "modified_date": "",
    }
    answer_id, s3_path_dir, image_direction, double_sided = await save_result(
        omr, response_ans
    )
    if answer_id:
        if double_sided:
            background_tasks.add_task(
                rotate_s3_double_images, s3_path_dir, image_direction
            )
        else:
            background_tasks.add_task(rotate_s3_images, s3_path_dir, image_direction)

        return {"status": True, "data": {"answer_id": answer_id}}
    else:
        return {"status": False}


def get_value_list(document):
    value_list = list()
    for value in document["valueList"]:
        _type = value.get("type", "")
        _question_number = value.get("questionNumber", None)
        if _question_number:
            # _type = f"{_type[:2]}.." if len(_type) > 2 else _type
            _type = f"{_type}{_question_number}"
        _answer = " ".join(list(map(str, value.get("answer", []))))
        value_list.append([_type, _answer])
    return value_list


@router.get(
    "/answer/v2/{answer_id}", response_class=JSONResponse, name="판독결과 전체 return-v2"
)
async def send_answer_V2(answer_id, atype: str = "normal"):
    cursor = result.find(
        {
            "answerId": answer_id,
            "errorType": {"$size": 0}
            if atype == "normal"
            else (
                {"$not": {"$size": 0}}
                if atype == "all"
                else {"$elemMatch": {"$eq": f"{atype}"}}
            ),
        }
    )

    error_list = list()
    result_list = list()

    async for document in cursor:
        document = json.loads(json_util.dumps(document))
        ret_doc = dict()
        ret_doc["resultId"] = document["_id"]["$oid"]
        error_list.append(document["_id"]["$oid"])
        if document.get("specialBack", None):
            ret_doc["specialBack"] = "".join(document["specialBack"])[:10]
        ret_doc["valueList"] = get_value_list(document)
        result_list.append(ret_doc)

    return {"status": True, "data": {"result": result_list, "errors": error_list}}


@router.get(
    "/result/v2/{result_id}", response_class=JSONResponse, name="판독결과 상세 return-v2"
)
async def send_result(result_id):
    document = await result.find_one({"_id": ObjectId(result_id)})
    document = json.loads(json_util.dumps(document))
    ret_doc = dict()
    ret_doc["resultId"] = document["_id"]["$oid"]
    ret_doc["s3PathDetail"] = document["s3PathDetail"]
    ret_doc["valueList"] = document["valueList"]
    ret_doc["errorList"] = document["errorList"]

    answer_id = document["answerId"]
    ans_document = await answer.find_one({"_id": ObjectId(answer_id)})
    ans_document = json.loads(json_util.dumps(ans_document))

    meta_document = await metadata.find_one({"_id": ObjectId(ans_document["objectId"])})
    meta_document = json.loads(json_util.dumps(meta_document))

    meta_type = meta_document["content_level"]
    ret_doc["metaType"] = meta_type

    return {"status": True, "data": ret_doc}


@router.put(
    "/result/v2/{result_id}", response_class=JSONResponse, name="판독결과 상세 return-v2"
)
async def update_result(result_id, data=Body(...)):
    document = await result.find_one({"_id": ObjectId(result_id)})

    value_list = document["valueList"]
    # print(data)
    for idx, elem in enumerate(data):
        answer, total_order = elem["answer"], elem["totalOrder"]
        for val in value_list:
            if total_order == val["totalOrder"]:
                val["answer"] = answer
                break
    _ = await result.update_one(
        {"_id": ObjectId(result_id)}, {"$set": {"valueList": value_list,}},
    )

    return {"status": True}


@router.get("/answer/v2/{answer_id}/save", response_class=JSONResponse, name="txt 저장")
async def send_final_ans_V2(answer_id, background_tasks: BackgroundTasks):
    print(datetime.now(timezone("Asia/Seoul")).strftime("%Y.%m.%d  %H:%M:%S"))

    print("answer_id: ", answer_id)
    modified_date = datetime.now(timezone("Asia/Seoul")).strftime("%Y.%m.%d:%H:%M:%S")
    response, file_name, s3nameBefore, s3nameAfter = await send_final_result(answer_id)
    if response:
        background_tasks.add_task(
            rename_s3_images, answer_id, modified_date, s3nameBefore, s3nameAfter
        )
        [
            print(s3nameAfter[idx], " : ", len(data), data[-30:])
            for idx, data in enumerate(response.split("\n"))
        ]
        return {
            "status": True,
            "data": {"txt": response, "fileName": file_name},
        }
    else:
        return {"status": False}

