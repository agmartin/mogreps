import boto3
import json
import os, errno
from sqlalchemy.engine import reflection
from sqlalchemy import MetaData, Table, ForeignKeyConstraint
from sqlalchemy.schema import DropConstraint, AddConstraint



SQS_URL = 'https://sqs.us-east-1.amazonaws.com/332774875883/mogreps-inbound'
SQS = boto3.client('sqs', region_name='us-east-1')


def get_file_from_event(event):

    s3_client = boto3.client('s3')

    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        download_path = '/tmp/{}'.format(key)

        s3_client.download_file(bucket, key, download_path)

    return download_path


def get_file(key):
    dl_path = os.path.join(os.getcwd(), 'raw_data')

    try:
        os.makedirs(dl_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    file_path = os.path.join(dl_path, key)
    s3 = boto3.resource('s3')
    s3.Bucket('mogreps-inbound').download_file(key, file_path)

    return file_path


def get_fn_from_message(message):
    message_dict = json.loads(message['Body'])
    file_key = message_dict['Records'][0]['s3']['object']['key']
    return file_key


def delete_from_queue(receipt):
    SQS.delete_message(
        QueueUrl=SQS_URL,
        ReceiptHandle=receipt
    )


def check_for_message():
    response = SQS.receive_message(
        QueueUrl=SQS_URL,
        AttributeNames=['SentTimestamp'],
        MaxNumberOfMessages=1,
        MessageAttributeNames=['All'],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )

    if response:
        if 'Messages' in response:
            message = response['Messages'][0]
            receipt_handle = message['ReceiptHandle']
            file_key = get_fn_from_message(message)
            # delete_from_queue(receipt_handle)
            return file_key
        else:
            return False
    else:
        return False


def drop_foreign_keys(table_name, engine):
    print('starting FK drop')
    inspector = reflection.Inspector.from_engine(engine)
    fake_metadata = MetaData()

    fks = []
    tables = []

    for fk in inspector.get_foreign_keys(table_name):
        if fk['name']:
            fks.append(ForeignKeyConstraint((),(),name=fk['name']))

    t = Table(table_name, fake_metadata, *fks)

    print('openning conn')
    connection = engine.connect()
    transaction = connection.begin()
    for fkc in fks:
        connection.execute(DropConstraint(fkc))
    transaction.commit()
    connection.close()
    print('closing conn')


def restore_foreign_keys(table_name, engine):
    import models
    orig_meta = models.Base.metadata.tables[table_name]
    constraints = list(orig_meta.constraints)
    fks = [item for item in constraints if isinstance(item, ForeignKeyConstraint)]

    connection = engine.connect()
    transaction = connection.begin()
    for fkc in fks:
        connection.execute(AddConstraint(fkc))
    transaction.commit()
    connection.close()






