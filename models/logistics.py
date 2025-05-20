from odoo import models, fields, api, exceptions

class LogisticsShipment(models.Model):
    _name = 'logistics.logistics'
    _description = 'Data Riwayat Pengiriman'

    name = fields.Char(string="ID Logistik", required=True)
    order_id = fields.Many2one(
        'logistics.order',
        string="Pesanan",
        required=True,
        ondelete='cascade',
        domain=[('status', '!=', 'draft')]  # only allow orders not in draft
    )
    timestamp = fields.Datetime(string="Waktu Update", required=True, default=fields.Datetime.now)
    location = fields.Char(string="Lokasi", required=True)
    logistics_partner_id = fields.Many2one('logistics.partner', string="Mitra Logistik", required=True, ondelete='cascade')
    status = fields.Selection([
        ('pickup', 'Barang Diambil'),
        ('in_transit', 'Dalam Perjalanan'),
        ('arrived_hub', 'Tiba di Hub'),
        ('out_for_delivery', 'Keluar untuk Dikirim'),
        ('delivered', 'Terkirim'),
        ('failed', 'Gagal Dikirim'),
    ], string="Status Pengiriman", required=True)
    note = fields.Text(string="Catatan Tambahan")

    @api.model
    def create(self, vals):
        order = self.env['logistics.order'].browse(vals.get('order_id'))
        if order and order.status == 'draft':
            raise exceptions.UserError("Data logistik hanya dapat ditambahkan jika status pesanan bukan 'Draft'.")
        shipment = super().create(vals)
        shipment._update_order_status()
        return shipment

    def write(self, vals):
        res = super().write(vals)
        self._update_order_status()
        return res

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
