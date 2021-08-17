from rfmodel.geod.geod_profile import geod_profile
from pywps import FORMATS
from pywps.app import Process
from .process_defaults import process_defaults, LiteralInputD
from pywps.app.Common import Metadata
from pywps.response.execute import ExecuteResponse
from processes import process_helper
import processes.io_generator as iog
from .process_helper import get_request_data


class GeodProfile(Process):
    def __init__(self):
        process_id = 'geod_profile'
        defaults = process_defaults(process_id)

        inputs = \
            iog.input_srs(defaults) + \
            iog.raster_input(defaults) + \
            iog.xy(defaults, suffixes=(1, 2)) + \
            [
                LiteralInputD(defaults, 'npts', 'number of points ', data_type='integer', min_occurs=0, max_occurs=1,
                              default=0),
                LiteralInputD(defaults, 'del_s', 'delimiter distance between each two successive points',
                              data_type='float', min_occurs=0, max_occurs=1, default=0),
                LiteralInputD(defaults, 'interpolate', 'interpolate', data_type='boolean', min_occurs=1, max_occurs=1,
                              default=True),
            ]
        outputs = iog.output_r() + \
                  iog.output_value(['x', 'y', 'output'])

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
        ovr_idx = process_helper.get_ovr(request.inputs, ds)

        band_nums = request.inputs['bi'][0].data

        srs = process_helper.get_location_info_srs(request.inputs)

        x1, y1, x2, y2 = tuple(process_helper.get_input_data_array(request.inputs[a]) for a in ['x1', 'y1', 'x2', 'y2'])

        npts = get_request_data(request.inputs, 'npts') or 0
        del_s = get_request_data(request.inputs, 'del_s') or 0

        if not (len(x1) == len(y1) == len(x2) == len(y2)):
            raise Exception(f'the length of x1={len(x1)},y1={len(y1)},x2={len(x2)},y2={len(y2)} should be equal')
        x = []
        y = []
        output = []
        for lon1, lat1, lon2, lat2 in zip(x1, y1, x2, y2):
            geod_res, raster_res = \
                geod_profile(ds, band_nums=band_nums, lon1=lon1, lat1=lat1, lon2=lon2, lat2=lat2, ovr_idx=ovr_idx,
                             srs=srs, npts=npts, del_s=del_s)
            x.append(geod_res.lons)
            y.append(geod_res.lats)
            output.append(raster_res)
        del ds

        response.outputs['r'].data = raster_filename

        response.outputs['x'].data_format = FORMATS.JSON
        response.outputs['x'].data = x

        response.outputs['y'].data_format = FORMATS.JSON
        response.outputs['y'].data = y

        response.outputs['output'].data_format = FORMATS.JSON
        response.outputs['output'].data = output

        return response
