from odoo import models, fields

class LogisticsOrder(models.Model):
    _name = 'logistics.order'
    _description = 'Pesanan Pengiriman'

    name = fields.Char(string="Nomor Pesanan", required=True)
    customer_id = fields.Many2one('res.partner', string="Pelanggan", required=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Dikonfirmasi'),
        ('shipped', 'Dikirim'),
        ('delivered', 'Terkirim')
    ], string="Status", default='draft')
    transaction_ids = fields.One2many(
        'logistics.transaction', 
        'order_id', 
        string='Transaksi Terkait'
    )
    tracking_number = fields.Char(string="Nomor Resi")
    delivery_address = fields.Text(string="Alamat Pengiriman")
    order_date = fields.Datetime(string="Tanggal Pesanan", default=fields.Datetime.now)
    total_amount = fields.Float(string="Total Pembayaran")
    estimate_delivery_time = fields.Datetime(string="Estimasi Waktu Tiba")
    
    _sql_constraints = [
        ('tracking_number_unique', 'unique(tracking_number)', 'Nomor resi harus unik.')
    ]