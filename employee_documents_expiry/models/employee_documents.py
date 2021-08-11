# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta

from odoo import models, fields, api, _
from ast import literal_eval

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    note = fields.Char(string='Default Note')
    expiry_notify_ids = fields.Many2many('res.users','expiry_emp_rel','emp_id3', 'emp_id', string='Notify People For Documents Expiry',
                                         help='In this field you can add the people who needs to notify')
    customer_notify_ids = fields.Many2many('res.users', 'expiry_cus_rel','cust_id3', 'cust_id' ,string='Notify People For Customer Documents Expiry',
                                           help='In this field you can add the people who needs to notify')

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('employee_documents_expiry.expiry_notify_ids', self.expiry_notify_ids.ids)
        self.env['ir.config_parameter'].sudo().set_param('employee_documents_expiry.customer_notify_ids', self.customer_notify_ids.ids)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        with_user = self.env['ir.config_parameter'].sudo()
        expiry_notify_ids = with_user.get_param('employee_documents_expiry.expiry_notify_ids')
        customer_notify_ids = with_user.get_param('employee_documents_expiry.customer_notify_ids')
        res.update(
            expiry_notify_ids=[(6, 0, literal_eval(expiry_notify_ids))] if expiry_notify_ids else False,
            customer_notify_ids=[(6, 0, literal_eval(customer_notify_ids))] if customer_notify_ids else False,
        )
        return res


class HrEmployeeDocument(models.Model):
    _name = 'hr.employee.document'
    _description = 'HR Employee Documents'
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = 'document_namee'

    def mail_reminder(self):
        list=[]
        now = datetime.now() + timedelta(days=1)
        today = fields.Date.today()
        date_now = now.date()
        match = self.search([])
        with_user = self.env['ir.config_parameter'].sudo()
        expiry_notify_ids = with_user.get_param('employee_documents_expiry.expiry_notify_ids')
        expiry_notify_ids=literal_eval(expiry_notify_ids) if expiry_notify_ids else False
        print('tesssssssssssssssssssssssssssssssssssssssssssssssssssss', expiry_notify_ids)
        move_res_model_id = self.env['ir.model'].search([('model', '=', 'hr.employee.document')], limit=1).id
        for employee in expiry_notify_ids:
            print('aaaaaaaaaaaaaaaaaaaaaa',employee)
            document_ids = self.env['res.users'].search([('id', '=', employee)])
            if document_ids:
                print('document_idsdocument_idsdocument_ids',document_ids.login)
                for i in match:
                    if i.reminder_date:
                        exp_date = i.reminder_date - timedelta(days=7)
                        # if date_now >= exp_date:
                        if i.reminder_date == today:
                            schedule_activity = self.env['mail.activity'].create({
                                'note': (('Reminder notification for the expiry of %s Document') % (i.employee_ref.name)),
                                'res_id': i.id,
                                'res_model_id': move_res_model_id,
                                'summary': (('Reminder notification for the expiry of %s Document') % (i.employee_ref.name)),
                                'date_deadline': i.reminder_date,
                                'user_id': document_ids.id,
                            })
                            schedule_activity.action_close_dialog()
                            mail_content = "  Hello  " + i.employee_ref.name + ",Document " + i.name + "is going to expire on " + \
                                           str(i.expiry_date) + ". Please renew it before expiry date"
                            main_content = {
                                'subject': _('Document-%s Expired On %s') % (i.name, i.expiry_date),
                                'author_id': self.env.user.partner_id.id,
                                'body_html': mail_content,
                                'email_to': document_ids.login,
                                # 'email_to': i.employee_ref.work_email,
                            }
                            self.env['mail.mail'].create(main_content).send()
        for a in match:
            if a.reminder_date:
                exp_date = a.reminder_date - timedelta(days=7)
                # if date_now >= exp_date:
                if a.reminder_date == today:
                    mail_content = "  Hello  " + a.employee_ref.name + ",Document " + a.name + "is going to expire on " + \
                                   str(a.expiry_date) + ". Please renew it before expiry date"
                    main_content = {
                        'subject': _('Document-%s Expired On %s') % (a.name, a.expiry_date),
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': a.employee_ref.work_email,
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

    name = fields.Char(string='Document Number',required=True)
    document_name = fields.Many2one('employee.checklist', string='Document Type')
    description = fields.Text(string='Description', copy=False)
    expiry_date = fields.Date(string='Expiry Date', copy=False)
    reminder_date = fields.Date(string='Reminder Date', compute='get_reminder_date')
    employee_ref = fields.Many2one('hr.employee', copy=False)
    doc_attachment_id = fields.Many2many('ir.attachment', 'doc_attach_rel', 'doc_id', 'attach_id3', string="Attachment",
                                         help='You can attach the copy of your document', copy=False)
    issue_date = fields.Date(string='Issue Date', default=fields.Date.context_today, copy=False)
    employee_name = fields.Char(related='employee_ref.name',string="Employee Name")
    model_name = fields.Many2one('ir.model', help="Choose the model name", string="Model",
                                 ondelete='cascade',domain="[('model', '=','res.partner')]")
    model_field = fields.Many2one('ir.model.fields', string='Document Type', help="Choose the field",
                                  domain="[('model_id', '=','hr.employee')]",
                                  required=True, ondelete='cascade')
    document_namee = fields.Char(string='Document Name', related='model_field.field_description',readonly=True)

    def get_reminder_date(self):
        for i in self:
            document_threshhold = self.env['document.threshhold'].search([('document_name', '=', i.document_namee)])
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


class HrEmployee(models.Model):
    _inherit = 'hr.employee'


    def _document_count(self):
        for each in self:
            document_ids = self.env['hr.employee.document'].search([('employee_ref', '=', each.id)])
            each.document_count = len(document_ids)


    def document_view(self):
        self.ensure_one()
        domain = [
            ('employee_ref', '=', self.id)]
        return {
            'name': _('Documents'),
            'domain': domain,
            'res_model': 'hr.employee.document',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click to Create for New Documents
                        </p>'''),
            'limit': 80,
            'context': "{'default_employee_ref': '%s'}" % self.id
        }

    document_count = fields.Integer(compute='_document_count', string='# Documents')


class HrEmployeeAttachment(models.Model):
    _inherit = 'ir.attachment'

    doc_attach_rel = fields.Many2many('hr.employee.document', 'doc_attachment_id', 'attach_id3', 'doc_id',
                                      string="Attachment", invisible=1)
