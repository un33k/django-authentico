import uuid

def get_uuid(length=32):
    return uuid.uuid4().hex[:length]


