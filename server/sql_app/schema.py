from typing import Optional, List, Dict
from pydantic import BaseModel

__all__ = [
    "user_add",
    "user_addOut",
    "user_allOut",
    "user_oneOut",
    "user_update",
    "user_update",
    "user_updateOut",
    "user_deleteOut",
    "token",
    "Omrs",
    "Doc_Omrs",
]

"""
pydantic validation
"""


class user_add(BaseModel):
    user_id: str
    user_name: str
    user_pwd: str
    user_level: int

    class Config:
        schema_extra = {
            "example": {
                "user_id": "test",
                "user_name": "홍길동",
                "user_pwd": "12345",
                "user_level": 2,
            }
        }


class user_addOut(BaseModel):
    status: bool


class user_allOut(BaseModel):
    status: bool
    data: List


class user_oneOut(BaseModel):
    status: bool
    data: Dict


class user_update(BaseModel):
    # user_id: str
    user_name: str
    user_pwd: str
    user_level: int
    authToken: str

    class Config:
        schema_extra = {
            "example": {
                # "user_id": "test",
                "user_name": "",
                "user_pwd": "",
                "user_level": 2,
                "authToken": "",
            }
        }


class user_updateOut(BaseModel):
    status: bool
    data: Dict


class user_delete(BaseModel):
    authToken: str

    class Config:
        schema_extra = {"example": {"authToken": ""}}


class user_deleteOut(BaseModel):
    status: bool


class user_login(BaseModel):
    user_id: str
    user_pwd: str

    class Config:
        schema_extra = {"example": {"user_id": "test", "user_pwd": "12345"}}


class user_loginOut(BaseModel):
    status: bool
    data: Dict


class token(BaseModel):
    Authorization: str

    class Config:
        orm_mode = True


class omr_saveAnswer(BaseModel):
    objectId: str
    s3_path: str
    user_id: str

    class Config:
        schema_extra = {
            "example": {
                "objectId": "6339aa046566bd666e548b57",
                "s3_path": "s3://guidance-data-center/workspace/2022/한국가이던스 오엠알샘플파일 20220902-1/030-SDS진로탐색(고등)/",
                "user_id": "admin",
            }
        }


class modifiedOmrs(BaseModel):
    data: List

    class Config:
        schema_extra = {
            "example": {
                "data": [
                    {
                        "valueList": [
                            {
                                "section": "front",
                                "totalOrder": 1,
                                "type": "성별",
                                "answer": [2],
                            },
                            {
                                "section": "front",
                                "totalOrder": 2,
                                "type": "학교구분",
                                "answer": [1],
                            },
                            {
                                "section": "front",
                                "totalOrder": 3,
                                "type": "생년월일",
                                "answer": ["060524"],
                            },
                            {
                                "section": "front",
                                "totalOrder": 4,
                                "type": "개인번호",
                                "answer": ["10101"],
                            },
                            {
                                "section": "front",
                                "totalOrder": 5,
                                "type": "성명",
                                "answer": ["강희진"],
                            },
                        ],
                        "result_id": "6323bb013cfbbde832e8fead",
                    },
                    {
                        "valueList": [
                            {
                                "section": "front",
                                "totalOrder": 1,
                                "type": "성별",
                                "answer": [2],
                            },
                            {
                                "section": "front",
                                "totalOrder": 2,
                                "type": "학교구분",
                                "answer": [1],
                            },
                            {
                                "section": "front",
                                "totalOrder": 3,
                                "type": "생년월일",
                                "answer": ["060524"],
                            },
                            {
                                "section": "front",
                                "totalOrder": 4,
                                "type": "개인번호",
                                "answer": ["10101"],
                            },
                            {
                                "section": "front",
                                "totalOrder": 5,
                                "type": "성명",
                                "answer": ["이현수"],
                            },
                        ],
                        "result_id": "6323bb013cfbbde832e8feae",
                    },
                    {
                        "valueList": [
                            {
                                "section": "front",
                                "totalOrder": 1,
                                "type": "성별",
                                "answer": [2],
                            },
                            {
                                "section": "front",
                                "totalOrder": 2,
                                "type": "학교구분",
                                "answer": [1],
                            },
                            {
                                "section": "front",
                                "totalOrder": 3,
                                "type": "생년월일",
                                "answer": ["060524"],
                            },
                            {
                                "section": "front",
                                "totalOrder": 4,
                                "type": "개인번호",
                                "answer": ["10101"],
                            },
                            {
                                "section": "front",
                                "totalOrder": 5,
                                "type": "성명",
                                "answer": ["이예인"],
                            },
                        ],
                        "result_id": "6323bb013cfbbde832e8feaf",
                    },
                ],
            }
        }

