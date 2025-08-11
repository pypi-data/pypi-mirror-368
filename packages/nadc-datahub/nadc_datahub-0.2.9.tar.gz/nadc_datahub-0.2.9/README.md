# datahub
All data can be addressed using *dataset, datatype and metadatas*. 
A dataset is associated with a certain project, such as EP, Sitian.
Datatype refers to the type of data, such as image, spectrum, light curve, etc. Different dataset may have different datatypes.
Metadatas are the metadata of the data, such as the observation time, observation id, etc.

For example, the image observed by the EP WXT CMOS 13 with obsid 13600000582 can be addressed as:
```
{
    "dataset": "EP_TDIC",
    "datatype": "image",
    "metadatas": {
        "obsid": 13600000582,
        "instrument": "WXT"
        "CMOS": 13,
        "version": "v1"
    }
}
```

# Example
First of all, install : `pip install nadc-datahub`
All datasets are inherited from the base class `DataSet`, which defined the basic interface of all datasets. Includes:
1. authentication: `auth(username="", password="",token="")`
1. download: `download(datatype, metadatas:Dict)`
1. check authentication: `authorized()`

Here is an example of how to use the EP_TDIC dataset:

## preparation

1. import : `from nadc_datahub import EP_TDIC`
1. set data download strategy: `ep = EP_TDIC.get_entry("csdb")`
1. authenticate: `ep.auth("username", "password")`
1. check for authentication: `ep.authorized()`
1. download data: `ep.download("/tmp/img.fits","image", {"obsid": 13600000582})`

## Download data
Three levels of ep data can be downloaded:
1. CMOS Level： `ep.get_obs_data(output, obs_id, cmos_id, version, data_level)`
1. Source Level： `ep.get_src_data(output, obs_id, cmos_id, version, src_idx_in_det)`
1. File Level： `ep.get_file(output, obs_id, cmos_id, version)`
