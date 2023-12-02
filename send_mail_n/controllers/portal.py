# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.payment.controllers.portal import portal as payment_portal
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv import expression


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        x = 0
        workorder_count=0
        mrp_orders = request.env['mrp.production'].sudo().search([('partner_id','=',partner.id)])
        #mrp_orders = request.env['mrp.production'].sudo.(search([('partner_id','=',partner.id)]))
        for order in mrp_orders:
            work_order = request.env['mrp.workorder'].sudo().search([('production_id','=',order.id)])
            for work in work_order:
                x=x+1
        workorder_count =x

        values.update({
            'workorder_count': workorder_count,
        })
        return values

    #
    # Quotations and Sales Orders
    #
    @http.route(['/my/workorders', '/my/workorders/page/<int:page>'], type='http', auth="user", website=True)
    def portal_work_orders(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        WorkOrder = request.env['mrp.workorder']

        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id])
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_finished desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }
        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('mrp.workorder', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_start), ('create_date', '<=', date_finished)]

        # count for pager
        order_count = WorkOrder.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/workorders",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=order_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        orders = WorkOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_orders_history'] = orders.ids[:100]
        x = 0
        workorder_count=0
        
        mrp_workorders = request.env['mrp.workorder'].sudo().search([('partner_id','=',partner.id)])
        #mrp_orders = request.env['mrp.production'].sudo.(search([('partner_id','=',partner.id)]))
        #for order in mrp_orders:
            #work_orders = request.env['mrp.workorder'].sudo().search([('production_id','=',order.id)])
            #for work in work_orders:
                #x=x+1
        #workorder_count =x


        values.update({
            'date': date_begin,
            'orders': mrp_workorders.sudo(),
            'page_name': 'workorder',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/workorders',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("send_mail_n.portal_work_orders", values)