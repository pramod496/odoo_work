from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def _default_config_file_path(self):
        return self.company_id.conf_file

    def _default_region_name(self):
        return self.company_id.region_name

    def _default_aws_access_key_id(self):
        return self.company_id.aws_access_key_id

    def _default_aws_secret_access_key(self):
        return self.company_id.aws_secret_access_key

    def _default_bucket_name(self):
        return self.company_id.bucket_name

    def _default_file_object(self):
        return self.company_id.Object

    def _default_date_interval(self):
        return self.company_id.date_interval if self.company_id.date_interval else 0

    conf_file = fields.Char(String='Configuration File Full Path', help='/etc/odoo-server.conf', default=_default_config_file_path)
    region_name = fields.Char(String='AWS Region', help='ap-south-1', default=_default_region_name)
    aws_access_key_id = fields.Char(String='AWS Access Key Id', default=_default_aws_access_key_id)
    aws_secret_access_key = fields.Char(String='AWS Secret Access Key', default=_default_aws_secret_access_key)
    bucket_name = fields.Char(String='Bucket', default=_default_bucket_name)
    Object = fields.Char(String='Folder Name', default=_default_file_object)
    date_interval = fields.Integer(String='Delete All Logs Before/Days', default=_default_date_interval)

    @api.constrains('conf_file')
    def save_conf_file(self):
        self.company_id.conf_file = self.conf_file

    @api.constrains('region_name')
    def save_region_name(self):
        self.company_id.region_name = self.region_name

    @api.constrains('aws_access_key_id')
    def save_aws_access_key_id(self):
        self.company_id.aws_access_key_id = self.aws_access_key_id

    @api.constrains('aws_secret_access_key')
    def save_aws_secret_access_key(self):
        self.company_id.aws_secret_access_key = self.aws_secret_access_key

    @api.constrains('bucket_name')
    def save_bucket_name(self):
        self.company_id.bucket_name = self.bucket_name

    @api.constrains('Object')
    def save_Object(self):
        self.company_id.Object = self.Object

    @api.constrains('date_interval')
    def save_date_interval(self):
        self.company_id.date_interval = self.date_interval
