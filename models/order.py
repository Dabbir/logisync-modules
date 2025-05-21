from odoo import models, fields, api, exceptions

class LogisticsOrder(models.Model):
    _name = 'logistics.order'
    _description = 'Pesanan Pengiriman'

    # name = fields.Char(string="Nomor Pesanan", required=True)
    name = fields.Char(string="Nomor Pesanan", required=True, readonly=True, default=lambda self: ('New'))
    customer_id = fields.Many2one('res.partner', string="Pelanggan", required=True)
     
    status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Dikonfirmasi'),
        ('shipped', 'Dikirim'),
        ('delivered', 'Terkirim'),
        ('bermasalah', 'Bermasalah')
    ], string="Status", default='draft', readonly=True)
    transaction_ids = fields.One2many(
        'logistics.transaction', 
        'order_id', 
        string='Transaksi Terkait'
    )
    shipment_ids = fields.One2many(
        'logistics.logistics',
        'order_id',
        string='Riwayat Pengiriman'
    )
    tracking_number = fields.Char(string="Nomor Resi")
    delivery_address = fields.Text(string="Alamat Pengiriman")
    order_date = fields.Datetime(string="Tanggal Pesanan", default=fields.Datetime.now)
    total_amount = fields.Float(string="Total Pembayaran", compute='_compute_total_amount', store=True)
    estimate_delivery_time = fields.Datetime(string="Estimasi Waktu Tiba")
    
    _sql_constraints = [
        ('tracking_number_unique', 'unique(tracking_number)', 'Nomor resi harus unik.')
    ]

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('logistics.order') or 'New'
        record = super().create(vals)
        record._update_performance_trigger()  
        return record

    
    def write(self, vals):
        res = super().write(vals)
        self._update_performance_trigger()
        return res

    def _update_performance_trigger(self):
        for order in self:
            if order.order_date:
                self.env['logistics.performance'].update_or_create_performance(order.order_date)


    def unlink(self):
        affected_dates = self.mapped('order_date')
        res = super().unlink()
        for date in affected_dates:
            if date:
                self.env['logistics.performance'].update_or_create_performance(date)
        return res

    @api.depends('transaction_ids.amount')
    def _compute_total_amount(self):
        for order in self:
            total = sum(order.transaction_ids.mapped('amount'))
            order.total_amount = total

    def action_confirm(self):
        for order in self:
            if order.status != 'draft':
                continue
                
            if not order.transaction_ids:
                raise exceptions.UserError("Tidak dapat mengkonfirmasi pesanan karena belum ada transaksi.")
                
            all_paid = all(transaction.payment_status == 'paid' for transaction in order.transaction_ids)
            if not all_paid:
                raise exceptions.UserError("Tidak dapat mengkonfirmasi pesanan karena ada transaksi yang belum dibayar.")
                
            order.write({'status': 'confirmed'})

    def action_ship(self):
        for order in self:
            if order.status != 'confirmed':
                raise exceptions.UserError("Order must be confirmed before shipping.")
            if order.shipment_ids:
                order.write({'status': 'shipped'})
            else:
                raise exceptions.UserError("Tidak dapat mengubah status menjadi 'Dikirim' karena belum ada data logistik.")
                
    def action_deliver(self):
        for order in self:
            if order.status != 'shipped':
                raise exceptions.UserError("Order must be shipped before delivery.")
            order.write({'status': 'delivered'})
            
    def action_mark_problematic(self):
        for order in self:
            if order.status not in ['shipped', 'delivered']:
                raise exceptions.UserError("Hanya pesanan dengan status 'Dikirim' atau 'Terkirim' yang dapat ditandai bermasalah.")
            order.write({'status': 'bermasalah'})

    def get_current_location(self):
        self.ensure_one()
        last_update = self.shipment_ids.sorted(key=lambda s: s.timestamp or fields.Datetime.now(), reverse=True)
        return last_update[0].location if last_update else False
    
    @api.constrains('estimate_delivery_time', 'order_date')
    def _check_estimate_delivery_time(self):
        for record in self:
            if record.estimate_delivery_time and record.order_date:
                if record.estimate_delivery_time <= record.order_date:
                    raise exceptions.ValidationError(
                        "Estimasi Waktu Tiba harus lebih besar dari Tanggal Pesanan."
                    )