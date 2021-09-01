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
                    # if i.first_reminder_date:
                    #     exp_date = i.first_reminder_date - timedelta(days=7)
                    if i.first_reminder_date == today:
                        schedule_activity = self.env['mail.activity'].create({
                            'note': (('First Reminder notification for the expiry of Customer %s Document') % (i.customer_ref.name)),
                            'res_id': i.id,
                            'res_model_id': move_res_model_id,
                            'summary': (('First Reminder notification for the expiry of Customer %s Document') % (i.customer_ref.name)),
                            'date_deadline': i.first_reminder_date,
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
                    if i.second_reminder_date == today:
                        schedule_activity = self.env['mail.activity'].create({
                            'note': (('Second Reminder notification for the expiry of Customer %s Document') % (i.customer_ref.name)),
                            'res_id': i.id,
                            'res_model_id': move_res_model_id,
                            'summary': (('Second Reminder notification for the expiry of Customer %s Document') % (i.customer_ref.name)),
                            'date_deadline': i.second_reminder_date,
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
                    if i.third_reminder_date == today:
                        schedule_activity = self.env['mail.activity'].create({
                            'note': (('Third Reminder notification for the expiry of Customer %s Document') % (i.customer_ref.name)),
                            'res_id': i.id,
                            'res_model_id': move_res_model_id,
                            'summary': (('Third Reminder notification for the expiry of Customer %s Document') % (i.customer_ref.name)),
                            'date_deadline': i.third_reminder_date,
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
            # if a.reminder_date:
            #     exp_date = a.reminder_date - timedelta(days=7)
            if a.first_reminder_date == today or a.second_reminder_date == today or a.third_reminder_date == today:
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
    first_reminder_date = fields.Date(string='First Reminder Date', compute='get_reminder_date')
    second_reminder_date = fields.Date(string='Second Reminder Date', compute='get_reminder_date')
    third_reminder_date = fields.Date(string='Third Reminder Date', compute='get_reminder_date')
    customer_ref = fields.Many2one('res.partner',string="Customer Name")
    customer_name = fields.Char(related='customer_ref.name',string="Customer Name")
    cust_attachment_id = fields.Many2many('ir.attachment', 'cust_attach_rel', 'cust_id3', 'attchc_id3', string="Attachment",
                                         help='You can attach the copy of your document', copy=False)
    issue_date = fields.Date(string='Issue Date', default=fields.Date.context_today, copy=False)

    model_name = fields.Many2one('ir.model', help="Choose the model name", string="Model",
                                 ondelete='cascade',domain="[('model', '=','res.partner')]")
    # model_field = fields.Many2one('ir.model.fields', string='Document Type', help="Choose the field",
    #                               domain="[('model_id', '=','document.threshhold')]",
    #                               # ('ttype', 'in', ['datetime', 'date'])]",
    #                               required=True, ondelete='cascade')

    # document_name = fields.Char(string='Document Name', related='model_field.field_description',readonly=True)
    model_field = fields.Many2one('document.threshhold', string='Document Type',domain="[('form_type', '=','customer')]")
    document_name = fields.Char(string='Document Name', related='model_field.name', readonly=True)


    def get_reminder_date(self):
        self.first_reminder_date = 0
        self.second_reminder_date = 0
        self.third_reminder_date = 0
        for i in self:
            document_threshhold = self.env['document.threshhold'].search([('name', '=', i.document_name),
                                                                          ('form_type', '=','customer')])
            for document in document_threshhold:
                if document_threshhold:
                    date_format = '%Y-%m-%d'
                    orig_date = str(i.expiry_date)
                    dtObj = datetime.strptime(orig_date, date_format)
                    first_reminder = timedelta(days=int(document.first_reminder_threshold))
                    second_reminder = timedelta(days=int(document.second_reminder_threshold))
                    third_reminder = timedelta(days=int(document.third_reminder_threshold))
                    first_reminder_date = dtObj - first_reminder
                    second_reminder_date = dtObj - second_reminder
                    third_reminder_date = dtObj - third_reminder
                    print('Expiry dateeee', i.expiry_date)
                    print('days', first_reminder)
                    print('reminder date', first_reminder_date)
                    i.first_reminder_date = first_reminder_date
                    i.second_reminder_date = second_reminder_date
                    i.third_reminder_date = third_reminder_date


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # type = fields.Selection([('monthlyretainer', 'Monthly Retainer'), ('payasyougo', 'Per Transaction Pricing'), ('hybrid', 'Hybrid'),], string='Type')
    customer_def_type = fields.Selection([('monthlyretainer', 'Monthly Retainer'), ('payasyougo', 'Per Transaction Pricing'),
                                          ('hybrid', 'Hybrid'),], string='Billing Type')
    manager_license = fields.Char(string='Manager on License')
    poc_name = fields.Many2one('res.partner', string='POC Name')
    poc_contact_number = fields.Char(string='POC Contact Number')
    poc_email = fields.Char(string='POC Email id')
    contract_start_date = fields.Date("Contract Start Date")
    contract_end_date = fields.Date("Contract End Date")
    location = fields.Many2one('res.country', string='Location')
    trade_license_number = fields.Char(string='Trade License Number')
    trade_license_issue_date = fields.Date("Trade License Issue Date")
    trade_license_expiry_date = fields.Date("Trade License Expiry Date")
    naqodi_amwal_expiry = fields.Date("Naqodi/ Amwal Expiry")
    edirham_card_expiry = fields.Date("edirham card Expiry")
    esignature_card_expiry = fields.Date("Esignature Card Expiry")
    establishment_card_expiry = fields.Date("Establishment Card Expiry")
    immigration_card_expiry = fields.Date("Immigration Card Expiry")
    custom_card_expiry = fields.Date("Custom Card Expiry")
    tenancy_contract_issue_date = fields.Date("Tenancy Contract Issue Date")
    tenancy_contract_expiry = fields.Date("Tenancy Contract Expiry")
    ejari_start_date = fields.Date("Ejari Start Date")
    ejari_expiry = fields.Date("Ejari Expiry")
    ministry_of_economy_expiry = fields.Date("Ministry Of Economy Expiry")
    chamber_of_commerce_expiry = fields.Date("Chamber of Commerce Expiry")
    iso_certification_issue_date = fields.Date("ISO Certification Issue Date")
    iso_certification_expiry = fields.Date("ISO Certificate Expiry")
    vat_certificate_issue_date = fields.Date("VAT Certificate Issue Date")
    vat_certificate_expiry = fields.Date("VAT Certificate Expiry")
    mulkiya_issue_date = fields.Date("Mulkiya Issue Date")
    mulkiya_expiry = fields.Date("Mulkiya Expiry")
    po_box_expiry = fields.Date("P O Box  Expiry")
    sponsor_passport_no = fields.Char(string='Sponsor Passport No')
    sponsor_passport_copy_issue_date = fields.Date("Sponsor Passport Copy Issue Date")
    sponsor_passport_copy_expiry_date = fields.Date("Sponsor Passport Copy Expiry Date")
    sponsor_emirate_id_issue_date = fields.Date("Sponsor Emirates ID Issue Date")
    sponsor_emirate_id_expiry = fields.Date("Sponsor Emirates ID Expiry")
    status_of_license = fields.Selection([('active', 'Active'), ('inactive', 'Inactive'),
                                          ], string='Status Of License')


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
            # 'context': "{'default_customer_ref': '%s'}" % self.id
        }

    document_count = fields.Integer(compute='_document_count', string='# Documents')


class CustomerAttachment(models.Model):
    _inherit = 'ir.attachment'

    cust_attach_rel = fields.Many2many('customer.document', 'cust_attachment_id', 'cust_id3', 'attchc_id3',
                                      string="Attachment", invisible=1)
