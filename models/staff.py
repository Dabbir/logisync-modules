from odoo import models, fields

class LogisticsStaff(models.Model):
    _name = 'logistics.staff'
    _description = 'Staf Logistik'

    user_id = fields.Many2one('res.users', string="Pengguna", required=True)
    contact_number = fields.Char(string="No Kontak")
    position = fields.Char(string="Jabatan")
    assigned_area = fields.Char(string="Wilayah Tugas")
    schedule = fields.Text(string="Jadwal Kerja")