import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import users, omr


origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://15.164.11.235",
    "http://15.164.11.235:3000",
    "http://3.39.11.111",
    "http://3.39.11.111:3000",
    "http://3.39.210.140",
    "http://3.39.210.140:3000",
]


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router, prefix="/api", tags=["user"])
app.include_router(omr.router, prefix="/api", tags=["omr"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, debug=True, reload=True)
