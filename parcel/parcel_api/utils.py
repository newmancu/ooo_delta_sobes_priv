import uuid
import json
from django.contrib.sessions.serializers import BaseJSONSerializer
gen_uuid = uuid.uuid4

DUPLICATION_ERROR_CODE = 1062 # for mysql
