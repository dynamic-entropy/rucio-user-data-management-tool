import logging
from utils.utils import get_pfns_temp
from utils.rule import add_rule
from utils.logger import get_logger
from utils.register import register_temp_replica


logger = get_logger('file-upload')

def upload(rucio_client, files, temp_rse):
    from rucio.client.uploadclient import UploadClient
    uclient = UploadClient(logger=logger)

    items = [{
        "path": file["file_path"],
        "rse": temp_rse,
        "pfn": file["pfn"],
        "name": file["lfn"],
        "did_name": file["lfn"],
        "no_register": True,
        } 
    for file in files
    ]

    blue = "\x1b[35;20m"
    reset = "\x1b[0m"

    #trying to upload file
    uclient.upload(items)

    #collecting metadata about file
    files = uclient._collect_and_validate_file_info(items)

    #registering uploaded replicas in rucio catalogue
    for file in files:
        register_temp_replica(rucio_client, uclient, file)




def upload_file_and_create_rule(rucio_client, file_path, lfn, upload_params, rule_params):
    from os import stat

    DEFAULT_TEMP_UPLOAD_RSE = "T2_CH_CERN_Temp"
    account_name = rucio_client.account
    temp_rse = DEFAULT_TEMP_UPLOAD_RSE
    if upload_params.get("tempRSE"):
        temp_rse = upload_params["tempRSE"]

    pfns = get_pfns_temp(temp_rse=temp_rse, lfns=[lfn])

    files = [{   
        "lfn" : lfn,
        "pfn" : pfns[lfn],
        "file_path": file_path,
    }]

    try:
        upload(rucio_client, files=files, temp_rse=upload_params["tempRSE"])
    except Exception as e:
        logger.log(logging.ERROR, e)



    user_scope = f'user.{account_name}'
    add_rule(
                rucio_client,
                dids = [{ 'scope':user_scope, 'name':lfn }],
                copies=rule_params["copies"], 
                rse=rule_params["rse"], 
                lifetime=rule_params["lifetime"], 
                )  

