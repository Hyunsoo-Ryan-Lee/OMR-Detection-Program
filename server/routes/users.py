from fastapi import APIRouter, Body, HTTPException
from fastapi.encoders import jsonable_encoder

from bson import json_util
from bson.objectid import ObjectId

from sql_app.schema import (
    user_add,
    user_addOut,
    user_allOut,
    user_oneOut,
    user_deleteOut,
    user_delete,
    user_updateOut,
    user_update,
    user_loginOut,
    user_login,
)
from sql_app.crud_user import (
    create_user,
    get_all_users,
    get_one_user,
    update_user,
    delete_user,
    login_user,
)

router = APIRouter()


@router.post("/users/", response_model=user_addOut, name="사용자 등록")
async def add_user_data(user: user_add = Body(...)):
    user = jsonable_encoder(user)
    result = await create_user(user)

    return result


@router.get(
    "/users/",
    response_model=user_allOut,
    response_model_exclude={"data": {"__all__": {"user_pwd", "authToken"}}},
    name="전체 사용자 조회",
)
async def get_all_user_data():
    result = await get_all_users()

    return result


@router.get(
    "/users/{id}",
    response_model=user_oneOut,
    response_model_exclude={"data": {"user_pwd", "authToken"}},
    name="사용자 조회",
)
async def get_one_user_data(id: str):
    result = await get_one_user(id)

    return result


@router.delete("/users/{id}", response_model=user_deleteOut, name="사용자 삭제")
async def delete_user_data(id: str, user_data: user_delete = Body(...)):
    user_data = jsonable_encoder(user_data)
    result = await delete_user(id, user_data)

    return result


@router.put(
    "/users/{id}",
    response_model=user_updateOut,
    response_model_exclude={"data": {"_id", "user_pwd", "authToken"}},
    name="사용자 수정",
)
async def update_user_data(id: str, user_data: user_update = Body(...)):
    user_data = jsonable_encoder(user_data)
    result = await update_user(id, user_data)

    return result


@router.post(
    "/login/",
    response_model=user_loginOut,
    response_model_exclude={"data": {"user_pwd"}},
    name="사용자 로그인",
)
async def user_login_data(user_data: user_login = Body(...)):
    user_data = jsonable_encoder(user_data)
    result = await login_user(user_data)

    return result
