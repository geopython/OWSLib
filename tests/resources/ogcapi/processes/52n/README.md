# 52 North OGC API Process server responses

This directory contains static responses from the 52North OGC API Process server. 
Note that calling `GET /process/{processid}/jobs` open a window where we can load an example demo input, execute the request and get the response URL. 

Demo input to the EchoProcess: 
    echoprocess_execute_input.json

http://geoprocessing.demo.52north.org:8080/javaps/rest/processes/org.n52.javaps.test.EchoProcess/echoprocess_execute_input.json -> http://geoprocessing.demo.52north.org:8080/javaps/rest/processes/org.n52.javaps.test.EchoProcess/jobs/<jobid>

## Responses

The static files were obtained by making the following requests. 

- api.json
    http://geoprocessing.demo.52north.org:8080/javaps/rest/api
- capabilities.json
    http://geoprocessing.demo.52north.org:8080/javaps/rest/
- conformancedeclaration.json:
   http://geoprocessing.demo.52north.org:8080/javaps/rest/conformance
- echoprocess_jobs_results.json
    http://geoprocessing.demo.52north.org:8080/javaps/rest/processes/org.n52.javaps.test.EchoProcess/jobs/{jobid}/results
- echoprocess_jobs_status.json
    http://geoprocessing.demo.52north.org:8080/javaps/rest/processes/org.n52.javaps.test.EchoProcess/jobs/{jobid}
- processdescription_multireferencebinaryinputalgorithm.json
    http://geoprocessing.demo.52north.org:8080/javaps/rest/processes/org.n52.javaps.test.MultiReferenceBinaryInputAlgorithm
- processdescription_echoprocess.json
    http://geoprocessing.demo.52north.org:8080/javaps/rest/processes/org.n52.javaps.test.EchoProcess
- processlist.json
    http://geoprocessing.demo.52north.org:8080/javaps/rest/processes  

