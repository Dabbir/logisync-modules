from odoo import models, fields, api, exceptions

class LogisticsShipment(models.Model):
    _name = 'logistics.logistics'
    _description = 'Data Riwayat Pengiriman'

    name = fields.Char(string="ID Logistik", required=True, readonly=True, default=lambda self: ('New'))

    order_id = fields.Many2one(
        'logistics.order',
        string="Pesanan",
        required=True,
        ondelete='cascade',
        domain=[('status', '!=', 'draft')],
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    timestamp = fields.Datetime(string="Waktu Update", required=True, default=fields.Datetime.now, readonly=True)
    location = fields.Char(string="Lokasi", required=True, readonly=True)
    logistics_partner_id = fields.Many2one('logistics.partner', string="Mitra Logistik", required=True, ondelete='cascade', readonly=True)
    status = fields.Selection([
        ('pickup', 'Barang Diambil'),
        ('in_transit', 'Dalam Perjalanan'),
        ('arrived_hub', 'Tiba di Hub'),
        ('out_for_delivery', 'Keluar untuk Dikirim'),
        ('delivered', 'Terkirim'),
        ('failed', 'Gagal Dikirim'),
    ], string="Status Pengiriman", required=True)
    note = fields.Text(string="Catatan Tambahan")

    # Add a state field to control the editable states
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')
    ], string="State", default='draft', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', ('New')) == ('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('logistics.logistics') or ('New')

        order = self.env['logistics.order'].browse(vals.get('order_id'))
        if order and order.status == 'draft':
            raise exceptions.UserError("Data logistik hanya dapat ditambahkan jika status pesanan bukan 'Draft'.")

        vals['state'] = 'done'
        
        shipment = super().create(vals)
        shipment._update_order_status()
        shipment._update_performance_trigger()
        return shipment

    def write(self, vals):
        for field in vals.keys():
            if field not in ['status', 'note', 'state']:
                raise exceptions.UserError(f"Field '{field}' cannot be modified after creation. Only status and notes can be updated.")
        
        res = super().write(vals)
        self._update_order_status()
        self._update_performance_trigger()
        return res   

    def unlink(self):
        affected_dates = self.mapped('order_id.order_date')
        res = super().unlink()
        for date in affected_dates:
            if date:
                self.env['logistics.performance'].update_or_create_performance(date)
        return res

    def _update_performance_trigger(self):
        for shipment in self:
            order = shipment.order_id
            if order and order.order_date:
                self.env['logistics.performance'].update_or_create_performance(order.order_date)

    def _update_order_status(self):
        for shipment in self:
            order = shipment.order_id
            if not order:
                continue

            if order.status == 'confirmed':
                order.write({'status': 'shipped'})

            if shipment.status == 'delivered' and order.status != 'delivered':
                shipment_location = (shipment.location or "").strip().lower()
                delivery_address = (order.delivery_address or "").strip().lower()
                if shipment_location and delivery_address and shipment_location in delivery_address:
                    order.write({'status': 'delivered'})

            if shipment.status == 'failed' and order.status != 'bermasalah':
                order.write({'status': 'bermasalah'})