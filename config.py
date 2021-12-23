import os
from pytz import timezone

# Config
KALEIDOS_RESOURCE_BASE_URI = "http://kanselarij.vo.data.gift/"
SIGNINGHUB_RESOURCE_BASE_URI = os.environ.get("SIGNINGHUB_API_URL", KALEIDOS_RESOURCE_BASE_URI).strip("/") + "/"
TIMEZONE = timezone('Europe/Brussels')

# Constants
APPLICATION_GRAPH = "http://mu.semte.ch/application"
KANSELARIJ_GRAPH = "http://mu.semte.ch/graphs/organizations/kanselarij"

class __Mode:
    __MODE = os.environ.get("MODE")

    @property
    def dev(self):
        return self.__MODE == "development"

mode = __Mode()
