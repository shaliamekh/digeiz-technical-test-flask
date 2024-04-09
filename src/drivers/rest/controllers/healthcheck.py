from flask_restful import Resource


class HealthCheck(Resource):
    @staticmethod
    def get() -> dict[str, str]:
        return {"status": "OK"}
