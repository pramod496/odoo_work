from odoo import models, fields, api
import os
import logging
import datetime
_logger = logging.getLogger(__name__)
try:
    import boto3
except:
    _logger.debug('boto3 package is required!!')

import logging
from botocore.exceptions import ClientError


class Company(models.Model):
    _inherit = 'res.company'

    conf_file = fields.Char(String='Configuration File Full Path', help='/etc/odoo-server.conf')
    region_name = fields.Char(String='AWS Region', help='ap-south-1')
    aws_access_key_id = fields.Char(String='AWS Access Key Id')
    aws_secret_access_key = fields.Char(String='AWS Secret Access Key')
    bucket_name = fields.Char(String='Bucket')
    Object = fields.Char(String='Folder Name')
    date_interval = fields.Integer(String='Delete All Logs Before/Days', default='4')

    def get_s3_connection(self):
        # Get the S3 connection object
        s3 = boto3.resource(
            service_name='s3',
            region_name=str(self.region_name),
            aws_access_key_id=str(self.aws_access_key_id),
            aws_secret_access_key=str(self.aws_secret_access_key)
        )
        bucket = s3.Bucket(str(self.bucket_name))
        return bucket

    def upload_logs_to_aws(self):
        # obj = self.search([('aws_access_key_id', '!=', False)])
        # path, file_name = os.path.split(obj.conf_file)
        # os.chdir(path)

    # Read the Configuration File and Trace the log file
    #     try:
    #         with open(file_name, 'r') as f:
    #             lines = f.readlines()
    #             for line in lines:
    #                 if line.split(' ')[0] == 'logfile':
    #                     logfile = line.split(' ')[2].strip()
    #
    #             logfile_path, log_file = os.path.split(logfile)
    #             os.chdir(logfile_path)
    #     except EnvironmentError as w:
    #         logging.error(w)

    # Connect to S3 and upload the log File to S3 Bucket
    #     bucket = obj.get_s3_connection()
    #     try:
    #         bucket.upload_file(Filename=logfile_path + '/' + log_file, Key=str(obj.Object) + '/' + str(datetime.datetime.now()) + '.log')
    #     except ClientError as e:
    #         logging.error(e)

    # Truncate The Log File and Restart the system
        try:
            # os.system('echo %s|sudo -S %s' % ('odoo', 'sudo truncate -s 0 ' + logfile))
            os.system('echo %s|sudo -S %s' % ('odoo', 'sudo systemctl reboot'))
        except Exception as e:
            logging.error(e)


    def delete_old_log_files(self):
        obj = self.search([('aws_access_key_id', '!=', False)])
        if not obj:
            raise
        bucket = obj.get_s3_connection()
        for object_summary in bucket.objects.filter(Prefix=str(obj.Object) + "/"):
            key = object_summary.key.split('/')[1]
            if key:
                obj_date = datetime.datetime.strptime(key[:-4:1], '%Y-%m-%d %H:%M:%S.%f')
                if (datetime.datetime.now() - obj_date).days >= obj.date_interval:
                    try:
                        object_summary.delete()
                    except ClientError as e:
                        logging.error(e)

