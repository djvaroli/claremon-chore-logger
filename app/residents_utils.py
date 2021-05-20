
from redis_utils import get_redis_client


def get_phone_number_resident(
        phone_number: str
) -> str:
    hash_name = f"claremon-chore-logger::phone_number>resident"
    redis_client = get_redis_client()

    resident = None
    if redis_client.hexists(hash_name, key=phone_number):
        resident = redis_client.hget(name=hash_name, key=phone_number).decode()

    return resident


def get_residents_names():
    hash_name = f"claremon-chore-logger::phone_number>resident"
    redis_client = get_redis_client()

    resident_names = list()
    if redis_client.exists(hash_name):
        residents_encoded = redis_client.hgetall(hash_name)
        for phone, resident_name in residents_encoded.items():
            resident_names.append(resident_name.decode().lower())

    return resident_names
