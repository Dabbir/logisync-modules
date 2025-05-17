from odoo import models, fields

class LogisticsPerformance(models.Model):
    _name = 'logistics.performance'
    _description = 'Performa Logistik'

    date_range_start = fields.Date(string="Awal Periode")
    date_range_end = fields.Date(string="Akhir Periode")
    on_time_rate = fields.Float(string="Tingkat Ketepatan Waktu (%)")
    avg_delivery_time = fields.Float(string="Rata-rata Waktu Kirim (jam)")
    avg_estimated_delivery_time = fields.Float(string="Rata-rata Estimasi Waktu Tiba (jam)")
    logistics_cost_per_order = fields.Float(string="Biaya Logistik per Order")
    total_orders = fields.Integer(string="Jumlah Order")
    logistics_partner_id = fields.Many2one('logistics.partner', string="Mitra Logistik")
