import settings

__all__ = ["mongoConnector"]


class mongoConnector(object):
    host_name = settings.MONGO_HOST
    port = settings.MONGO_PORT
    user = settings.MONGO_USER
    pwd = settings.MONGO_PWD

    @classmethod
    def connect(self):
        import motor.motor_asyncio

        MONGO_URI = f"mongodb://{mongoConnector.user}:{mongoConnector.pwd}@{mongoConnector.host_name}:{mongoConnector.port}"
        client = motor.motor_asyncio.AsyncIOMotorClient(
            MONGO_URI, serverSelectionTimeoutMS=5000
        )

        return client
