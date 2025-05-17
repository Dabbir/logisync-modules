from odoo import models, fields

class LogisticsPartner(models.Model):
    _name = 'logistics.partner'
    _description = 'Mitra Logistik'

    name = fields.Char(string="Nama Mitra", required=True)
    contact_info = fields.Char(string="Kontak")
