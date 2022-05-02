import logging
from utils.logger import get_logger


logger = get_logger('file-register')

def register_temp_replica(rucio_client, uclient, file):
        """
        Registers the given file in Rucio. Creates a dataset if
        needed. Registers the file DID and creates the replication
        rule if needed. Adds a replica to the file did.
        (This function is meant to be used as class internal only)

        :param file: dictionary describing the file
        :param registered_dataset_dids: set of dataset dids that were already registered
        :param ignore_availability: ignore the availability of a RSE

        :raises DataIdentifierAlreadyExists: if file DID is already registered and the checksums do not match
        """
                
        logger.log(logging.DEBUG, 'Registering file')

        # verification whether the scope exists
        account_scopes = []
        try:
            account_scopes = rucio_client.list_scopes_for_account(rucio_client.account)
        except Exception as e:
            print(e)
        if account_scopes and file['did_scope'] not in account_scopes:
            logger.log(logging.WARNING, 'Scope {} not found for the account {}.'.format(file['did_scope'], rucio_client.account))

        rse = file['rse']
        file_scope = file['did_scope']
        file_name = file['did_name']
        file_did = {'scope': file_scope, 'name': file_name}
        file['state'] = 'A'
        replica_for_api = uclient._convert_file_for_api(file)

        try:
            # if the remote checksum is different this did must not be used
            meta = rucio_client.get_metadata(file_scope, file_name)
            logger.log(logging.INFO, 'File DID already exists')
            logger.log(logging.DEBUG, 'local checksum: %s, remote checksum: %s' % (file['adler32'], meta['adler32']))

            if str(meta['adler32']).lstrip('0') != str(file['adler32']).lstrip('0'):
                logger.log(logging.ERROR, 'Local checksum %s does not match remote checksum %s' % (file['adler32'], meta['adler32']))
                raise Exception("Did Already exists")

            # add file to rse if it is not registered yet
            replicastate = list(rucio_client.list_replicas([file_did], all_states=True))
            if rse not in replicastate[0]['rses']:
                rucio_client.add_replicas(rse=rse, files=[replica_for_api])
                logger.log(logging.INFO, 'Successfully added replica in Rucio catalogue at %s' % rse)
        except Exception as e:
            logger.log(logging.DEBUG, 'File DID does not exist')
            rucio_client.add_replicas(rse=rse, files=[replica_for_api])
            logger.log(logging.INFO, 'Successfully added replica in Rucio catalogue at %s' % rse)
