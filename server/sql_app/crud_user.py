from cmath import e
import json

from utils import create_access_token, Hash
from sql_app.database import collection_user

from bson import json_util
from bson.objectid import ObjectId

__all__ = [
    "create_user",
    "get_all_users",
    "get_one_user",
    "update_user",
    "delete_user",
    "login_user",
]


async def create_user(user_data: dict) -> dict:
    status = True

    user_data["user_pwd"] = Hash.bcrypt(user_data["user_pwd"])

    new_user = await collection_user.find_one({"user_id": user_data["user_id"]})

    if new_user:
        status = False
    else:
        # Generate User Token
        token = create_access_token(data={"sub": user_data["user_id"]})

        user_data["authToken"] = token

        # Insert Document
        await collection_user.insert_one(user_data)

    return {"status": status}


async def get_all_users():
    users = []
    users_data = collection_user.find({})
    async for user in users_data:
        users.append(user)

    users = json.loads(json_util.dumps(users))
    return {"status": True, "data": users}


async def get_one_user(_id: str):
    status = True
    user_data = await collection_user.find_one({"_id": ObjectId(_id)})

    if user_data:
        user_data = json.loads(json_util.dumps(user_data))
    else:
        status = False
        user_data = {}

    return {"status": status, "data": user_data}


async def update_user(_id, user_data: dict):
    status = True

    try:
        chk_user = await collection_user.find_one({"_id": ObjectId(_id)})

        is_user_admin = await collection_user.find_one(
            {"authToken": user_data["authToken"]}
        )

        if chk_user:
            if (
                chk_user["authToken"] == user_data["authToken"]
                or is_user_admin["user_level"] == 1
            ):
                user_data["user_pwd"] = Hash.bcrypt(user_data["user_pwd"])

                await collection_user.update_one(
                    {"_id": ObjectId(_id)},
                    {
                        "$set": {
                            "user_name": user_data["user_name"],
                            "user_pwd": user_data["user_pwd"],
                            "user_level": user_data["user_level"],
                        }
                    },
                )

                result_data = await collection_user.find_one({"_id": ObjectId(_id)})
                result_data = json.loads(json_util.dumps(result_data))

            else:
                status = False
                result_data = {}
    except:
        status = False
        result_data = {}

    return {"status": status, "data": result_data}


async def delete_user(_id, user_data: dict):
    status = True

    try:
        chk_user = await collection_user.find_one({"_id": ObjectId(_id)})
        if chk_user:
            is_user_admin = await collection_user.find_one(
                {"authToken": user_data["authToken"]}
            )

            if (
                chk_user["authToken"] == user_data["authToken"]
                or is_user_admin["user_level"] == 1
            ):
                await collection_user.delete_one({"_id": ObjectId(_id)})
            else:
                status = False
    except:
        status = False

    return {"status": status}


async def login_user(user_data: dict):
    status = True

    result_data = await collection_user.find_one({"user_id": user_data["user_id"]})

    chk_pwd = Hash.verify_password(user_data["user_pwd"], result_data["user_pwd"])

    if chk_pwd:
        if result_data:
            result_data = json.loads(json_util.dumps(result_data))
        else:
            status = False
            result_data = {}
    else:
        status = False
        result_data = {}

    return {"status": status, "data": result_data}
