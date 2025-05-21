from odoo import models, fields, api, exceptions

class LogisticsTransaction(models.Model):
    _name = 'logistics.transaction'
    _description = 'Transaksi Pembayaran'

    name = fields.Char(string="ID Transaksi", required=True, readonly=True, default='New')
    order_id = fields.Many2one('logistics.order', string="Pesanan Terkait", required=True, readonly=True)
    transaction_date = fields.Datetime(string="Tanggal Transaksi", default=fields.Datetime.now, readonly=True)
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
    ], string="Metode Pembayaran", readonly=True)
    amount = fields.Float(string="Jumlah Pembayaran", readonly=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')
    ], string="State", default='draft', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('logistics.transaction') or 'New'
        
        vals['state'] = 'done'
        
        transaction = super().create(vals)
        transaction._check_order_payment_status()
        transaction._update_performance_trigger()
        return transaction
        
    def write(self, vals):
        for field in vals.keys():
            if field not in ['payment_status', 'state']:
                raise exceptions.UserError(f"Field '{field}' cannot be modified after creation. Only payment status can be updated.")
                
        for record in self:
            if record.payment_status == 'paid' and 'payment_status' in vals:
                if vals['payment_status'] != 'refunded':
                    raise exceptions.UserError("Status pembayaran tidak dapat diubah setelah dibayar kecuali menjadi 'Dikembalikan'.")
        
        res = super().write(vals)
        if 'payment_status' in vals:
            self._check_order_payment_status()
        self._update_performance_trigger()
        return res
    
    def unlink(self):
        for record in self:
            if record.payment_status != 'unpaid':
                raise exceptions.UserError("Hanya transaksi dengan status 'Belum Dibayar' yang dapat dihapus.")
                
        affected_dates = self.mapped('order_id.order_date')
        res = super().unlink()
        for date in affected_dates:
            if date:
                self.env['logistics.performance'].update_or_create_performance(date)
        return res
        
    def _update_performance_trigger(self):
        for trx in self:
            order = trx.order_id
            if order and order.order_date:
                self.env['logistics.performance'].update_or_create_performance(order.order_date)

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