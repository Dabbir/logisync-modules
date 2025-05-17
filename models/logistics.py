from odoo import models, fields

class LogisticsShipment(models.Model):
    _name = 'logistics.logistics'
    _description = 'Data Riwayat Pengiriman'

    name = fields.Char(string="ID Logistik", required=True)
    order_id = fields.Many2one('logistics.order', string="Pesanan", required=True, ondelete='cascade')
    timestamp = fields.Datetime(string="Waktu Update", required=True, default=fields.Datetime.now)
    location = fields.Char(string="Lokasi", required=True)
    status = fields.Selection([
        ('pickup', 'Barang Diambil'),
        ('in_transit', 'Dalam Perjalanan'),
        ('arrived_hub', 'Tiba di Hub'),
        ('out_for_delivery', 'Keluar untuk Dikirim'),
        ('delivered', 'Terkirim'),
        ('failed', 'Gagal Dikirim'),
    ], string="Status Pengiriman", required=True)
    note = fields.Text(string="Catatan Tambahan")
