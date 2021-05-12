from osgeo import gdal

from gdalos.geod_profile import geod_profile
from osgeo_utils.samples.gdallocationinfo import LocationInfoSRS
from pywps import FORMATS
from pywps.app import Process
from pywps.inout import LiteralOutput
from .process_defaults import process_defaults, LiteralInputD
from pywps.app.Common import Metadata
from pywps.response.execute import ExecuteResponse
from processes import process_helper
import processes.io_generator as iog


class GeodProfile(Process):
    def __init__(self):
        process_id = 'geod_profile'
        defaults = process_defaults(process_id)

        inputs = \
            iog.io_crs(defaults) + \
            iog.of_pointcloud(defaults) + \
            iog.raster_input(defaults) + \
            iog.xy(defaults, suffixes=(1, 2)) + \
            [
                LiteralInputD(defaults, 'srs', 'SRS or coordinate kind: [4326|ll|xy|pl|epsg code]', data_type='string',
                              min_occurs=1, max_occurs=1, default=4326),
                LiteralInputD(defaults, 'npts', 'number of points ', data_type='integer', min_occurs=1, max_occurs=1,
                              default=0),
                LiteralInputD(defaults, 'del_s', 'delimiter distance between each two successive points ',
                              data_type='float', min_occurs=1, max_occurs=1, default=0),
                LiteralInputD(defaults, 'interpolate', 'interpolate ', data_type='boolean', min_occurs=1, max_occurs=1,
                              default=True),
            ]
        outputs = [LiteralOutput('output', 'raster values at the requested coordinates', data_type=None)]

        super().__init__(
            self._handler,
            identifier=process_id,
            version='1.1.0',
            title='raster values',
            abstract='get raster values at given coordinates',
            profile='',
            metadata=[Metadata('raster')],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response: ExecuteResponse):
        raster_filename, ds = process_helper.open_ds_from_wps_input(request.inputs['r'][0])

        band: gdal.Band = ds.GetRasterBand(request.inputs['bi'][0].data)
        if band is None:
            raise Exception('band number out of range')

        srs = request.inputs['srs'][0].data.lower() if 'srs' in request.inputs else None
        if srs == 'pl':
            srs = LocationInfoSRS.PixelLine
        elif srs == 'xy':
            srs = LocationInfoSRS.SameAsDS_SRS
        elif srs == 'll':
            srs = LocationInfoSRS.SameAsDS_SRS_GeogCS
        else:
            try:
                srs = int(srs)
            except Exception:
                pass

        x1, y1, x2, y2 = tuple(process_helper.get_input_data_array(request.inputs[a]) for a in ['x1', 'y1', 'x2', 'y2'])

        npts = request.inputs['npts'][0].data
        del_s = request.inputs['del_s'][0].data

        if not (len(x1) == len(y1) == len(x2) == len(y2)):
            raise Exception(f'the length of x1={len(x1)},y1={len(y1)},x2={len(x2)},y2={len(y2)} should be equal')
        values = []
        for lon1, lat1, lon2, lat2 in zip(x1, y1, x2, y2):
            geod_res, raster_res = \
                geod_profile(ds, lon1=lon1, lat1=lat1, lon2=lon2, lat2=lat2,
                             srs=srs, npts=npts, del_s=del_s)
            res = geod_res.lons, geod_res.lats, raster_res[0]
            values.append(res)
        del ds

        response.outputs['output'].output_format = FORMATS.JSON
        response.outputs['output'].data = values

        return response
