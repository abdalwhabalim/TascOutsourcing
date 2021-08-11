# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta

from odoo import models, fields, api, _
from ast import literal_eval
import datetime
from datetime import datetime
from datetime import timedelta

class CustomerDocument(models.Model):
    _name = 'customer.document'
    _description = 'Customer Documents'
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = 'document_name'

    def mail_reminder(self):
        list=[]
        now = datetime.now() + timedelta(days=1)
        today = fields.Date.today()
        date_now = now.date()
        match = self.search([])
        with_user = self.env['ir.config_parameter'].sudo()
        customer_notify_ids = with_user.get_param('employee_documents_expiry.customer_notify_ids')
        customer_notify_ids=literal_eval(customer_notify_ids) if customer_notify_ids else False
        print('tesssssssssssssssssssssssssssssssssssssssssssssssssssss', customer_notify_ids)
        move_res_model_id = self.env['ir.model'].search([('model', '=', 'customer.document')], limit=1).id
        for customer in customer_notify_ids:
            print('aaaaaaaaaaaaaaaaaaaaaa',customer)
            document_ids = self.env['res.users'].search([('id', '=', customer)])
            if document_ids:
                print('document_idsdocument_idsdocument_ids',document_ids.login)
                for i in match:
                    if i.reminder_date:
                        print('ssssssssssssssssssssssssssssssssssss',i.reminder_date)
                        print('dddddddddddddddddddddddddddddddddd',today)
                        exp_date = i.reminder_date - timedelta(days=7)
                        print('eeeeeeeeeeeeeeeeeeeeeeeeeeeee',exp_date)
                        if i.reminder_date == today:
                            schedule_activity = self.env['mail.activity'].create({
                                'note': (('Reminder notification for the expiry of Customer %s Document') % (i.customer_ref.name)),
                                'res_id': i.id,
                                'res_model_id': move_res_model_id,
                                'summary': (('Reminder notification for the expiry of Customer %s Document') % (i.customer_ref.name)),
                                'date_deadline': i.reminder_date,
                                'user_id': document_ids.id,
                            })
                            schedule_activity.action_close_dialog()
                            mail_content = "  Hello  " + i.customer_ref.name + ",Document " + i.name + "is going to expire on " + \
                                           str(i.expiry_date) + ". Please renew it before expiry date"
                            main_content = {
                                'subject': _('Customer Document-%s Expired On %s') % (i.name, i.expiry_date),
                                'author_id': self.env.user.partner_id.id,
                                'body_html': mail_content,
                                'email_to': document_ids.login,
                                # 'email_to': i.employee_ref.work_email,
                            }
                            self.env['mail.mail'].create(main_content).send()
        for a in match:
            if a.reminder_date:
                exp_date = a.reminder_date - timedelta(days=7)
                if a.reminder_date == today:

                    mail_content = "  Hello  " + a.customer_ref.name + ",Document " + a.name + "is going to expire on " + \
                                   str(a.expiry_date) + ". Please renew it before expiry date"
                    main_content = {
                        'subject': _('Document-%s Expired On %s') % (a.name, a.expiry_date),
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': a.customer_ref.email,
                        # 'email_to': i.employee_ref.work_email,
                    }
                    self.env['mail.mail'].create(main_content).send()

    @api.onchange('expiry_date')
    def check_expr_date(self):
        for each in self:
            exp_date = each.expiry_date
            if exp_date and exp_date < date.today():
                return {
                    'warning': {
                        'title': _('Document Expired.'),
                        'message': _("Your Document Is Already Expired.")
                    }
                }

    name = fields.Char(string='Document Number', required=True, copy=False)
    # document_name = fields.Many2one('customer.checklist', string='Document Type', required=True)
    description = fields.Text(string='Description', copy=False)
    expiry_date = fields.Date(string='Expiry Date', copy=False)
    reminder_date = fields.Date(string='Reminder Date', compute='get_reminder_date')
    customer_ref = fields.Many2one('res.partner',string="Customer Name")
    customer_name = fields.Char(related='customer_ref.name',string="Customer Name")
    cust_attachment_id = fields.Many2many('ir.attachment', 'cust_attach_rel', 'cust_id3', 'attchc_id3', string="Attachment",
                                         help='You can attach the copy of your document', copy=False)
    issue_date = fields.Date(string='Issue Date', default=fields.Date.context_today, copy=False)

    model_name = fields.Many2one('ir.model', help="Choose the model name", string="Model",
                                 ondelete='cascade',domain="[('model', '=','res.partner')]")
    model_field = fields.Many2one('ir.model.fields', string='Document Type', help="Choose the field",
                                  domain="[('model_id', '=','res.partner')]",
                                  # ('ttype', 'in', ['datetime', 'date'])]",
                                  required=True, ondelete='cascade')
    document_name = fields.Char(string='Document Name', related='model_field.field_description',readonly=True)

    def get_reminder_date(self):
        for i in self:
            document_threshhold = self.env['document.threshhold'].search([('document_name', '=', i.document_name)])
            for document in document_threshhold:
                if document_threshhold:
                    date_format = '%Y-%m-%d'
                    orig_date = str(i.expiry_date)
                    dtObj = datetime.strptime(orig_date, date_format)
                    days = timedelta(days=int(document.reminder_threshold))
                    reminder_date = dtObj - days
                    print('Expiry dateeee',i.expiry_date)
                    print('days',days)
                    print('reminder date',reminder_date)
                    i.reminder_date = reminder_date


class ResPartner(models.Model):
    _inherit = 'res.partner'


    def _document_count(self):
        for each in self:
            document_ids = self.env['customer.document'].search([('customer_ref', '=', each.id)])
            each.document_count = len(document_ids)


    def document_view(self):
        self.ensure_one()
        domain = [
            ('customer_ref', '=', self.id)]
        return {
            'name': _('Documents'),
            'domain': domain,
            'res_model': 'customer.document',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click to Create for New Documents
                        </p>'''),
            'limit': 80,
            'context': "{'default_customer_ref': '%s'}" % self.id
        }

    document_count = fields.Integer(compute='_document_count', string='# Documents')


class CustomerAttachment(models.Model):
    _inherit = 'ir.attachment'

    cust_attach_rel = fields.Many2many('customer.document', 'cust_attachment_id', 'cust_id3', 'attchc_id3',
                                      string="Attachment", invisible=1)
