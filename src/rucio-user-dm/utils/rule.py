from utils.logger import get_logger

logger = get_logger('add-rule')

def add_rule(rucio_client, dids, copies, rse, lifetime):
    try:
        rule_id = rucio_client.add_replication_rule(dids, copies, rse, lifetime=lifetime)
        logger.info(f"Rule id: {rule_id}")
        logger.info(f"Rule Info: https://cms-rucio-webui.cern.ch/rule?rule_id={rule_id[0]}")
    except Exception as e:
        print(e)