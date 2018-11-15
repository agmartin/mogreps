class SecureCredsGetter:

    def __init__(self):
        import boto3
        self.ssm_client = boto3.client('ssm')

    def get_secret(self, key):
        resp = self.ssm_client.get_parameter(Name=key, WithDecryption=True)
        return resp['Parameter']['Value']

    def get_pg_creds(self):
        pg_user = self.get_secret('postgresUser')
        pg_pass = self.get_secret('postgresPass')
        return(pg_user, pg_pass)

    def get_database_dict(self):
        pgu, pgpa = self.get_pg_creds()

        db_dict = {
            'drivername': 'postgres+psycopg2',
            'host': 'mogreps.crngu8ksxmab.us-east-1.rds.amazonaws.com',
            'port': 5432,
            'username': pgu,
            'password': pgpa,
            'database': 'dev'
        }

        return db_dict
