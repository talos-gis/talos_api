from .sayhello import SayHello
from .ultimate_question import UltimateQuestion
from .sleep import Sleep
from .feature_count import FeatureCount
from .centroids import Centroids
from .buffer import Buffer
from .area import Area
from .bboxinout import Box
from .jsonprocess import TestJson

from .info import GetInfo
from .ls import ls
from .invert import Invert
from .crop_color import GdalDem
from .rasval import RasterValue
from .viewshed import Viewshed
from .los import LOS
from .calc import Calc
from .tester import Tester

# For the process list on the home page
processes = [
    SayHello(),
    UltimateQuestion(),
    Sleep(),
    FeatureCount(),
    Centroids(),
    Buffer(),
    Area(),
    Box(),
    TestJson(),

    GetInfo(),
    ls(),
    Invert(),
    GdalDem(),
    RasterValue(),
    Viewshed(),
    LOS(),
    Calc(),
    Tester(),
]

# For the process list on the home page
process_descriptor = {}
for process in processes:
    abstract = process.abstract
    identifier = process.identifier
    process_descriptor[identifier] = abstract
