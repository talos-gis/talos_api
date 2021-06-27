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
from .trans import Trans
from .visibility_adapter import pre_request_visibility, pre_response_visibility
from .xyz import XYZ
from .crop_color import GdalDem
from .ras_val import RasterValue
from .geod_profile import GeodProfile
from .viewshed import Viewshed
from .los import LOS
from .calc import Calc
from .tester import Tester
from .gdalinfo import GdalInfo
from .sandbox import Sandbox

from .p2p_loss_adapter import pre_request_p2p_loss, pre_response_p2p_loss
from .ros_adapter import pre_request_ros, pre_response_ros
from .elevation_point_adapter import pre_request_elevation_point, pre_response_elevation_point
from .geod_profile_adapter import pre_request_profile, pre_response_profile

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
    Trans(),
    XYZ(),
    GdalDem(),
    RasterValue(),
    GeodProfile(),
    Viewshed(),
    LOS(),
    Calc(),
    Tester(),
    Sandbox(),
    GdalInfo(),
]

preprocessosrs = {
    'Visibility': ('viewshed', pre_request_visibility, pre_response_visibility),
    'ExtendedVisibility': ('viewshed', pre_request_visibility, pre_response_visibility),
    'ros': ('los', pre_request_ros, pre_response_ros),
    'Points2PLoss': ('los', pre_request_p2p_loss, pre_response_p2p_loss),
    'ElevationPoint': ('ras_val', pre_request_elevation_point, pre_response_elevation_point),
    'Profile': ('geod_profile', pre_request_profile, pre_response_profile),
}

# For the process list on the home page
process_descriptor = {}
for process in processes:
    abstract = process.abstract
    identifier = process.identifier
    process_descriptor[identifier] = abstract
