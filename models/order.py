from odoo import models, fields, api, exceptions

class LogisticsOrder(models.Model):
    _name = 'logistics.order'
    _description = 'Pesanan Pengiriman'

    name = fields.Char(string="Nomor Pesanan", required=True, readonly=True, default=lambda self: ('New'))
    customer_id = fields.Many2one('res.partner', string="Pelanggan", required=True, states={'draft': [('readonly', False)], 'new': [('readonly', False)]})
     
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
        string='Transaksi Terkait',
        states={'draft': [('readonly', False)]}
    )
    shipment_ids = fields.One2many(
        'logistics.logistics',
        'order_id',
        string='Riwayat Pengiriman',
        states={'draft': [('readonly', False)]}
    )
    tracking_number = fields.Char(string="Nomor Resi", states={'draft': [('readonly', False)]})
    delivery_address = fields.Text(string="Alamat Pengiriman", states={'draft': [('readonly', False)]})
    order_date = fields.Datetime(string="Tanggal Pesanan", default=fields.Datetime.now, states={'draft': [('readonly', False)]})
    total_amount = fields.Float(string="Total Pembayaran", compute='_compute_total_amount', store=True)
    estimate_delivery_time = fields.Datetime(string="Estimasi Waktu Tiba", states={'draft': [('readonly', False)]})
    
    _sql_constraints = [
        ('tracking_number_unique', 'unique(tracking_number)', 'Nomor resi harus unik.')
    ]
    
    # Set fields as readonly by default for existing records
    def _get_default_readonly(self):
        # This controls default readonly state
        return self.id and self.status != 'draft'
    
    @api.model
    def default_get(self, fields_list):
        # This is called when creating a new record
        result = super(LogisticsOrder, self).default_get(fields_list)
        # Set status to 'draft' for new records
        result['status'] = 'draft'
        return result

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('logistics.order') or 'New'
        record = super().create(vals)
        record._update_performance_trigger()  
        return record

    def write(self, vals):
        # If trying to edit fields when not in draft status
        for record in self:
            # Only allow status changes via action methods and computed fields to update
            if record.status != 'draft' and vals.keys() != {'status'} and not all(key in ['total_amount', 'transaction_ids', 'shipment_ids'] for key in vals.keys()):
                editable_fields = ['status', 'total_amount', 'transaction_ids', 'shipment_ids']
                for field in vals.keys():
                    if field not in editable_fields:
                        raise exceptions.UserError(f"Field '{field}' cannot be modified when the order is not in Draft status.")
        
        res = super().write(vals)
        self._update_performance_trigger()
        return res

    def _update_performance_trigger(self):
        for order in self:
            if order.order_date:
                self.env['logistics.performance'].update_or_create_performance(order.order_date)

    def unlink(self):
        # Prevent deletion of non-draft orders
        for record in self:
            if record.status != 'draft':
                raise exceptions.UserError("Hanya pesanan dengan status 'Draft' yang dapat dihapus.")
                
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