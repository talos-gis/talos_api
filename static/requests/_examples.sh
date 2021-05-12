shopt -s expand_aliases
server=http://localhost:5000/wps

## GET
# GetCapabilities
curl "$server?service=wps&request=getcapabilities"

# describeprocess
curl "$server?service=wps&version=1.0.0&request=describeprocess&identifier=viewshed"

# Get Info
curl "$server?service=wps&version=1.0.0&request=execute&Identifier=info&storeExecuteResponse=trueRawDataOutput=output&RawDataOutput=output"

# say hello
curl "$server?service=wps&version=1.0.0&request=execute&Identifier=say_hello&storeExecuteResponse=true&DataInputs=name=Idan&RawDataOutput=output"

#ls
curl "$server?service=wps&version=1.0.0&request=execute&Identifier=ls&storeExecuteResponse=true&DataInputs=dir=./static/data/maps&DataInputs=pattern=*.tif&RawDataOutput=output"

# ras_val
curl "$server?service=wps&version=1.0.0&request=execute&Identifier=ras_val&storeExecuteResponse=true&DataInputs=x=35.1;y=32.1&RawDataOutput=output"
curl "$server?service=wps&version=1.0.0&request=execute&Identifier=ras_val&storeExecuteResponse=true&DataInputs=x=35.1;y=32.1;r=@xlink:href=file:./static/data/maps/srtm1_x35_y32.tif&RawDataOutput=output"
curl -H "Content-type: xml" -X POST -d@./data/requests/ras_val.xml $server

## color crop
curl -H "Content-type: xml" -X POST -d@./data/requests/crop_color_czml.xml $server # -o ./outputs/crop_color_czml.czml && cat ./outputs/crop_sample_czml.czml
curl -H "Content-type: xml" -X POST -d@./data/requests/crop_color_o.xml $server -o outputs/crop_color_o.tif

# calc
curl -H "Content-type: xml" -X POST -d@./data/requests/calc_comb.xml $server -o outputs/calc_comb.tif

# viewshed with sampled data
curl "$server?service=wps&version=1.0.0&request=execute&Identifier=viewshed&storeExecuteResponse=true&DataInputs=ox=35.21317;oy=32.03437;oz=100;tz=0;md=1&RawDataOutput=tif"
curl "$server?service=wps&version=1.0.0&request=execute&Identifier=viewshed&storeExecuteResponse=true&DataInputs=r=@xlink:href=file:./static/data/maps/srtm1_x33-62_y23-39.tif;ox=35.21317;oy=32.03437;oz=100;tz=0;md=1"
curl "$server?service=wps&version=1.0.0&request=execute&Identifier=viewshed&storeExecuteResponse=true&DataInputs=r=@xlink:href=file:./static/data/maps/srtm1_x35_y32.tif;ox=35.21317;oy=32.03437;oz=100;tz=0;md=1" # -o ./outputs/viewshed.tif && cat ./outputs/viewshed.tif
curl -H "Content-type: xml" -X POST -d@./data/requests/viewshed.xml $server -o outputs/viewshed.tif
curl -H "Content-type: xml" -X POST -d@./data/requests/viewshed_comb.xml $server -o outputs/viewshed_comb.tif
curl -H "Content-type: xml" -X POST -d@./data/requests/viewshed_comb_czml.xml $server -o outputs/viewshed_comb.czml


## clear request cache
rm ./logs/pywps-logs.sqlite3

# Sand Castle
#https://sandcastle.cesium.com/?src=CZML%20Polyline.html&label=CZML

# sleep
curl "%server%?service=wps&version=1.0.0&request=execute&Identifier=sleep&storeExecuteResponse=true&DataInputs=seconds=2&RawDataOutput=output"


http://localhost:5000/wps?request=DescribeProcess&service=WPS&identifier=all&version=1.0.0
http://localhost:5000/wps?service=wps&version=1.0.0&request=execute&Identifier=say_hello&storeExecuteResponse=true&DataInputs=name=Idan&RawDataOutput=output
http://localhost:5000/wps/say_hello?service=wps&version=1.0.0&request=execute&storeExecuteResponse=true&DataInputs=name=Idan
http://localhost:5000/processes/say_hello?DataInputs=name=Idan&RawDataOutput=output

http://localhost:5000/wps/
http://localhost:5000/processes
http://localhost:5000/processes/say_hello
http://localhost:5000/jobs/
http://localhost:5000/jobs/say_hello
http://localhost:5000/jobs/say_hello/output
http://localhost:5000/jobs/say_hello?DataInputs=name=Idan&RawDataOutput=output
http://localhost:5000/jobs/say_hello/output?DataInputs=name=Idan
http://localhost:5000/jobs/say_hello?DataInputs=name=Idan&f=xml

https://github.com/opengeospatial/ogcapi-processes
https://github.com/opengeospatial/ogcapi-processes/blob/master/implementations.adoc
https://app.swaggerhub.com/apis/geoprocessing/ogcapi-processes/1.0-draft.6-SNAPSHOT#/ProcessDescription/getProcessDescription
https://demo.pygeoapi.io/master/openapi?f=html#/hello-world/describeHello-worldProcess


https://demo.pygeoapi.io/master/processes?f=json
https://demo.pygeoapi.io/master/processes?f=html

https://app.swaggerhub.com/apis/geoprocessing/ogcapi-processes/1.0-draft.6-SNAPSHOT#/ConformanceDeclaration/getConformanceClasses
http://geoprocessing.demo.52north.org:8080/javaps/rest/
http://geoprocessing.demo.52north.org:8080/javaps/rest/processes
http://geoprocessing.demo.52north.org:8080/javaps/rest/processes/org.n52.javaps.test.EchoProcess
