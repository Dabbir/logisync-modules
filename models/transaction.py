from odoo import models, fields

class LogisticsTransaction(models.Model):
    _name = 'logistics.transaction'
    _description = 'Transaksi Pembayaran'

    name = fields.Char(string="ID Transaksi", required=True)
    order_id = fields.Many2one('logistics.order', string="Pesanan Terkait", required=True)
    transaction_date = fields.Datetime(string="Tanggal Transaksi", default=fields.Datetime.now)
    payment_status = fields.Selection([
        ('unpaid', 'Belum Dibayar'),
        ('paid', 'Sudah Dibayar'),
        ('refunded', 'Dikembalikan')
    ], string="Status Pembayaran", default='unpaid')
    payment_method = fields.Selection([
        ('credit_card', 'Kartu Kredit'),
        ('bank_transfer', 'Transfer Bank'),
        ('e_wallet', 'E-Wallet'),
        ('cod', 'COD')
    ], string="Metode Pembayaran")
    amount = fields.Float(string="Jumlah Pembayaran")
