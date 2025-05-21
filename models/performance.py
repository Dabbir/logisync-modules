from odoo import models, fields, api
from datetime import datetime

class LogisticsPerformance(models.Model):
    _name = 'logistics.performance'
    _description = 'Performa Logistik Bulanan'
    _order = 'year desc, month desc'

    month = fields.Integer(string="Bulan", required=True)
    year = fields.Integer(string="Tahun", required=True)

    date_range_start = fields.Date(string="Awal Periode")
    date_range_end = fields.Date(string="Akhir Periode")

    on_time_rate = fields.Float(string="Tingkat Ketepatan Waktu (%)")
    avg_delivery_time = fields.Float(string="Rata-rata Waktu Kirim (jam)")
    avg_estimated_delivery_time = fields.Float(string="Rata-rata Estimasi Waktu Tiba (jam)")
    logistics_cost_per_order = fields.Float(string="Biaya Logistik per Order")
    total_orders = fields.Integer(string="Jumlah Order")

    # Rekap jumlah order per status
    total_draft = fields.Integer(string="Draft")
    total_confirmed = fields.Integer(string="Dikonfirmasi")
    total_shipped = fields.Integer(string="Dikirim")
    total_delivered = fields.Integer(string="Terkirim")
    total_bermasalah = fields.Integer(string="Bermasalah")

    _sql_constraints = [
        ('unique_month_year', 'unique(month, year)', 'Data performa untuk bulan dan tahun ini sudah ada.')
    ]

    @api.model
    def update_or_create_performance(cls, target_date):
        """Update or create performance report for a given date (any date in the month)."""
        month = target_date.month
        year = target_date.year

        # range tanggal
        date_start = datetime(year, month, 1).date()
        if month == 12:
            date_end = datetime(year + 1, 1, 1).date()
        else:
            date_end = datetime(year, month + 1, 1).date()

        # Ambil atau buat report
        report = cls.search([('month', '=', month), ('year', '=', year)], limit=1)
        if not report:
            report = cls.create({
                'month': month,
                'year': year,
                'date_range_start': date_start,
                'date_range_end': date_end,
            })
        report._recalculate()

    def _recalculate(self):
        for rec in self:
            start = rec.date_range_start
            end = rec.date_range_end

            orders = self.env['logistics.order'].search([
                ('order_date', '>=', start),
                ('order_date', '<', end)
            ])

            total_orders = len(orders)
            rec.total_orders = total_orders

            # Status breakdown
            rec.total_draft = len(orders.filtered(lambda o: o.status == 'draft'))
            rec.total_confirmed = len(orders.filtered(lambda o: o.status == 'confirmed'))
            rec.total_shipped = len(orders.filtered(lambda o: o.status == 'shipped'))
            rec.total_delivered = len(orders.filtered(lambda o: o.status == 'delivered'))
            rec.total_bermasalah = len(orders.filtered(lambda o: o.status == 'bermasalah'))

            # Rata-rata estimasi waktu
            estimated_times = []
            delivery_times = []
            on_time_count = 0

            for order in orders:
                if order.estimate_delivery_time and order.order_date:
                    est_hours = (order.estimate_delivery_time - order.order_date).total_seconds() / 3600
                    estimated_times.append(est_hours)

                if order.shipment_ids:
                    pickup = order.shipment_ids.filtered(lambda s: s.status == 'pickup')
                    delivered = order.shipment_ids.filtered(lambda s: s.status == 'delivered')
                    if pickup and delivered:
                        dt = (delivered[-1].timestamp - pickup[0].timestamp).total_seconds() / 3600
                        delivery_times.append(dt)

                        # Hitung ketepatan waktu
                        if order.estimate_delivery_time and delivered[-1].timestamp <= order.estimate_delivery_time:
                            on_time_count += 1

            rec.avg_estimated_delivery_time = sum(estimated_times) / len(estimated_times) if estimated_times else 0
            rec.avg_delivery_time = sum(delivery_times) / len(delivery_times) if delivery_times else 0
            rec.on_time_rate = (on_time_count / len(delivery_times) * 100) if delivery_times else 0

            # Biaya logistik
            transactions = self.env['logistics.transaction'].search([
                ('order_id', 'in', orders.ids),
                ('payment_status', '=', 'paid'),
            ])
            total_payment = sum(transactions.mapped('amount'))
            rec.logistics_cost_per_order = total_payment / total_orders if total_orders else 0
