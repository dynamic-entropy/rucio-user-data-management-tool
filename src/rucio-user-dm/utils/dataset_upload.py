from utils.file_upload import upload
from utils.rule import add_rule
from utils.logger import get_logger
import logging

logger = get_logger('dataset-upload')

def add_dataset(rucio_client, dataset_name):
    user_scope = f'user.{rucio_client.account}'
    return rucio_client.add_did(scope=user_scope, name=dataset_name, did_type='DATASET')


def attach_files_to_dataset(rucio_client, dataset_name, filenames):
    user_scope = f'user.{rucio_client.account}'
    dids = [{'scope': user_scope, 'name': filename} for filename in filenames]
    return rucio_client.attach_dids(scope=user_scope, name=dataset_name, dids=dids)


def upload_dataset_and_create_rule(rucio_client, dataset_path, dataset_name, rule_params, upload_params):
    from os import listdir, stat
    from os.path import join, isfile
    from utils.utils import get_pfns_temp

    DEFAULT_TEMP_UPLOAD_RSE = "T2_CH_CERN_Temp"

    account_name = rucio_client.account
    temp_rse = DEFAULT_TEMP_UPLOAD_RSE
    if upload_params.get("tempRSE"):
        temp_rse = upload_params["tempRSE"]

    files = []
    file_list = [file for file in listdir(dataset_path) if isfile(join(dataset_path, file))]
    lfn_map = {file: f"/store/user/rucio/{account_name}{dataset_name.split('#')[0]}/{file}" for file in file_list}
    lfns=list(lfn_map.values())
    pfns = get_pfns_temp(temp_rse=temp_rse, lfns=lfns)

    for file in file_list:
        files.append({
            "lfn" : lfn_map[file],
            "pfn" : pfns[lfn_map[file]],
            "file_path": join(dataset_path, file),
        })
    
    #upload files
    try:
        upload(rucio_client, files=files, temp_rse=temp_rse)
    except Exception as e:
        logger.log(logging.ERROR, e)
    

    #create dataset
    dataset_add_status = add_dataset(rucio_client, dataset_name)
    #TODO: convert all print statements to log
    print("dataset_add_status: ", dataset_add_status)


    #attach uploaded files to dataset
    attach_files_to_dataset_status = attach_files_to_dataset(rucio_client, filenames=lfns, dataset_name=dataset_name)
    print("attach_files_to_dataset_status: ", attach_files_to_dataset_status)


    #create rule on dataset
    user_scope = f'user.{rucio_client.account}'
    add_rule(
                rucio_client,
                dids = [{ 'scope':user_scope, 'name':dataset_name }],
                copies=rule_params["copies"], 
                rse=rule_params["rse"], 
                lifetime=rule_params["lifetime"], 
                )

