### mmif-docloc-baapb

This plugin finds the location of AAPB files in the CLAMS-Brandeis Datahousing server for the purpose of resolving the 'baapb' scheme in MMIF document URIs. 


#### requirements

* This python package is written as a plugin to [`mmif-python`](https://github.com/clamsproject/mmif-python) and won't work as a standalone package. (requires `mmif-python` >= 1.0.2) 
* This is basically a client implementation for the server application https://github.com/clamsproject/aapb-brandeis-datahousing. 
* The environment variable `BAAPB_RESOLVER_ADDRESS` should store the address (including port number) where the server is running.
