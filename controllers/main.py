from odoo import http, _
from odoo.http import request

class LogisyncController(http.Controller):
    
    @http.route('/', type='http', auth='public', website=True)
    def logisync_homepage(self, **kw):
        """LogiSync Homepage"""
        return request.render('logisync-modules.logisync_homepage', {})

    @http.route('/tracking', type='http', auth='public', website=True)
    def tracking_form(self, **kw):
        """Halaman untuk mencari status pengiriman"""
        return request.render('logisync-modules.tracking_form', {})
    
    @http.route('/tracking/result', type='http', auth='public', website=True)
    def tracking_result(self, **post):
        """Menampilkan hasil tracking berdasarkan nomor resi"""
        tracking_number = post.get('tracking_number', False)
        
        if not tracking_number:
            return request.render('logisync-modules.tracking_form', {
                'error': 'Silahkan masukkan nomor resi'
            })
        
        order = request.env['logistics.order'].sudo().search([
            ('tracking_number', '=', tracking_number)
        ], limit=1)
        
        if not order:
            return request.render('logisync-modules.tracking_form', {
                'error': 'Nomor resi tidak ditemukan'
            })
        
        shipment_history = request.env['logistics.logistics'].sudo().search([
            ('order_id', '=', order.id)
        ], order='timestamp desc')
        
        est_delivery_date = ''
        if order.estimate_delivery_time:
            est_delivery_date = order.estimate_delivery_time.strftime('%d %b %Y, %H:%M')
        
        return request.render('logisync-modules.tracking_result', {
            'order': order,
            'shipment_history': shipment_history,
            'est_delivery_date': est_delivery_date,
            'last_status': shipment_history[0] if shipment_history else False
        })