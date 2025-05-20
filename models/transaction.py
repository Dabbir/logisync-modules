from odoo import models, fields, api, exceptions

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
    
    @api.model
    def create(self, vals):
        transaction = super().create(vals)
        transaction._check_order_payment_status()
        return transaction
        
    def write(self, vals):
        res = super().write(vals)
        if 'payment_status' in vals:
            self._check_order_payment_status()
        return res
        
    def _check_order_payment_status(self):
        for transaction in self:
            order = transaction.order_id
            if order and order.status == 'draft':
                all_paid = all(t.payment_status == 'paid' for t in order.transaction_ids)
                if all_paid and order.transaction_ids:
                    try:
                        order.action_confirm()
                    except exceptions.UserError:
                        pass
            
            if transaction.payment_status == 'refunded' and order:
                order.write({'status': 'bermasalah'})