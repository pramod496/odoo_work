# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.payment.controllers.portal import portal as payment_portal
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv import expression
from werkzeug.exceptions import NotFound, Forbidden
from odoo.tools import consteq, plaintext2html
import base64,io


def _has_token_access(res_model, res_id, token=''):
    record = request.env[res_model].browse(res_id).sudo()
    token_field = request.env[res_model]._mail_post_token_field
    return (token and record and consteq(record[token_field], token))


def _message_post_helper(res_model='', res_id=None, message='', token='', nosubscribe=True, **kw):
    """ Generic chatter function, allowing to write on *any* object that inherits mail.thread.
        If a token is specified, all logged in users will be able to write a message regardless
        of access rights; if the user is the public user, the message will be posted under the name
        of the partner_id of the object (or the public user if there is no partner_id on the object).

        :param string res_model: model name of the object
        :param int res_id: id of the object
        :param string message: content of the message

        optional keywords arguments:
        :param string token: access token if the object's model uses some kind of public access
                             using tokens (usually a uuid4) to bypass access rules
        :param bool nosubscribe: set False if you want the partner to be set as follower of the object when posting (default to True)

        The rest of the kwargs are passed on to message_post()
    """
    record = request.env[res_model].browse(res_id)
    author_id = request.env.user.partner_id.id if request.env.user.partner_id else False
    if token:
        if request.env.user._is_public():
            if kw.get('pid') and consteq(kw.get('hash'), record._sign_token(int(kw.get('pid')))):
                author_id = kw.get('pid')
            else:
                # TODO : After adding the pid and sign_token in access_url when send invoice by email, remove this line
                # TODO : Author must be Public User (to rename to 'Anonymous')
                author_id = record.partner_id.id if hasattr(record, 'partner_id') and record.partner_id.id else author_id
        else:
            if not author_id:
                raise NotFound()
    kw.pop('csrf_token', None)   
    if kw.get('partner_ids'):
        pass
    else:
        kw['partner_ids'] = [record.partner_id.id, request.env.user.company_id.partner_id.id]       
    return record.with_context(mail_create_nosubscribe=nosubscribe).sudo().message_post(body=message,
                                                                                   message_type=kw.pop('message_type', "comment"),
                                                                                   subtype=kw.pop('subtype', "mt_comment"),
                                                                                   author_id=author_id,                                                                                   
                                                                                   **kw)


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):

        values = super(CustomerPortal, self)._prepare_portal_layout_values()

        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']
        
        order_count = SaleOrder.search_count([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sale', 'done','confirm_sale'])
        ])

        values.update({
            'order_count': order_count,
        })
        return values


    @http.route(['/my/orders/<int:order_id>'], type='http', auth="public", website=True)
    def portal_order_page(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=order_sudo, report_type=report_type, report_ref='sale.action_report_saleorder', download=download)

        # use sudo to allow accessing/viewing orders for public user
        # only if he knows the private token
        now = fields.Date.today()

        # Log only once a day
        if order_sudo and request.session.get('view_quote_%s' % order_sudo.id) != now and request.env.user.share and access_token:
            request.session['view_quote_%s' % order_sudo.id] = now
            body = _('Quotation viewed by customer')
            _message_post_helper(res_model='sale.order', res_id=order_sudo.id, message=body, token=order_sudo.access_token, message_type='notification', subtype="mail.mt_note", partner_ids=order_sudo.user_id.sudo().partner_id.ids)

        domain = []
        # Only search into website_message_ids, so apply the same domain to perform only one search
        # extract domain from the 'website_message_ids' field
        field_domain = request.env['sale.order']._fields['website_message_ids'].domain
        if callable(field_domain):
            field_domain = field_domain(request.env['sale.order'])
        domain = expression.AND([domain, field_domain, [('res_id', '=', order_sudo.id)]])
        Message = request.env['mail.message'].sudo().search(domain,order="id desc")       
        
        values = {
            'sale_order': order_sudo,
            'model': order_sudo._name,
            'message': message,
            'msg_ids':Message,
            'token': access_token,
            'return_url': '/shop/payment/validate',
            'bootstrap_formatting': True,
            'partner_id': order_sudo.partner_id.id,
            'report_type': 'html',
        }

        if order_sudo.has_to_be_paid():
            domain = expression.AND([
                ['&', ('website_published', '=', True), ('company_id', '=', order_sudo.company_id.id)],
                ['|', ('specific_countries', '=', False), ('country_ids', 'in', [order_sudo.partner_id.country_id.id])]
            ])
            acquirers = request.env['payment.acquirer'].sudo().search(domain)

            values['acquirers'] = acquirers.filtered(lambda acq: (acq.payment_flow == 'form' and acq.view_template_id) or
                                                     (acq.payment_flow == 's2s' and acq.registration_view_template_id))
            values['pms'] = request.env['payment.token'].search(
                [('partner_id', '=', order_sudo.partner_id.id),
                ('acquirer_id', 'in', acquirers.filtered(lambda acq: acq.payment_flow == 's2s').ids)])

        if order_sudo.state in ('draft', 'sent', 'cancel'):
            history = request.session.get('my_quotations_history', [])
        else:
            history = request.session.get('my_orders_history', [])
        values.update(get_records_pager(history, order_sudo))

        return request.render('sale_order_status_n.portal_orders_status',values)
    
    @http.route(['/SO/chatter_post'], type='http', auth="public", website=True)
    def SoChatterPost(self, **kwargs):         
        attachment_ids = []
        attached_files = request.httprequest.files.getlist('files')
        for attachment in attached_files:
            if attachment.filename:
                attached_file = attachment.read()            
                attachment_value = {
                    'name': attachment.filename,
                    'res_model': kwargs['res_model'],
                    'res_id': int(kwargs['res_id']),
                    'datas': base64.encodestring(attached_file),
                    'datas_fname': attachment.filename,                
                }
                attach_id = request.env['ir.attachment'].sudo().create(attachment_value)
                attachment_ids.append(attach_id.id)                        

        message = kwargs['message']
        if message or attachment_ids:
            # message is received in plaintext and saved in html
            if message:
                message = plaintext2html(message)
            post_values = {
                'res_model': kwargs['res_model'],
                'res_id': int(kwargs['res_id']),
                'message': message,
                'send_after_commit': False,
                'attachment_ids': attachment_ids,
            }            
            message = _message_post_helper(**post_values)
        url = request.httprequest.referrer        

        return request.redirect(url)          
        
    @http.route([
        '/attach/download',
    ], type='http', auth='public')
    def download_attachment(self, attachment_id):
        # Check if this is a valid attachment id
        attachment = request.env['ir.attachment'].sudo().search_read(
            [('id', '=', int(attachment_id))],
            ["name", "datas", "file_type", "res_model", "res_id", "type", "url"]
        )
        if attachment:
            attachment = attachment[0]
        if attachment["datas"]:
            data = io.BytesIO(base64.standard_b64decode(attachment["datas"]))
            return http.send_file(data, filename=attachment['name'], as_attachment=True)
        else:
            return request.not_found()        
        
           
