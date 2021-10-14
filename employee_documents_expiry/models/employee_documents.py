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
                    # if i.first_reminder_date:
                    #     exp_date = i.first_reminder_date - timedelta(days=7)
                    #     # if date_now >= exp_date:
                    if i.first_reminder_date == today:
                        schedule_activity = self.env['mail.activity'].create({
                            'note': (('First Reminder notification for the expiry of %s Document') % (i.employee_ref.name)),
                            'res_id': i.id,
                            'res_model_id': move_res_model_id,
                            'summary': (('First Reminder notification for the expiry of %s Document') % (i.employee_ref.name)),
                            'date_deadline': i.first_reminder_date,
                            'user_id': document_ids.id,
                        })
                        schedule_activity.action_close_dialog()
                        template_id = self.env['ir.model.data'].get_object_reference(
                            'employee_documents_expiry',
                            'email_template_employee')[1]
                        if template_id:
                            email_template_obj = self.env['mail.template'].browse(template_id)
                            values = email_template_obj.generate_email(i.id, ['subject', 'body_html', 'email_from',
                                                                              'email_to', 'partner_to', 'email_cc',
                                                                              'reply_to',
                                                                              'scheduled_date'])
                            i.aging_date = i.model_field.first_reminder_threshold
                            # mail_content = '<p> Greetings from TASC!! <br></br> <br></br>Please be informed that below employee is about to expiry in ' + i.first_reminder_threshhold + 'days' +\
                            #                '<br></br><b>Please review the below to take necessary action to renew the </b>'+ i.name + \
                            #                'Please write to projects@tascoutsourcing.com for any further assistance on renewal of the document."</p>'
                            values['email_from'] = self.env['res.users'].browse(self.env.uid).company_id.email
                            values['email_to'] = document_ids.login
                            # values['body_html'] = mail_content
                            # values['subject'] = _('Reshmi Document-%s Expired On %s') % (i.name, i.expiry_date),
                            msg_id = self.env['mail.mail'].create(values)
                            if msg_id:
                                msg_id._send()
                        # mail_content = "  Hello  " + i.employee_ref.name + ",Document " + i.name + "is going to expire on " + \
                        #                str(i.expiry_date) + ". Please renew it before expiry date"
                        # main_content = {
                        #     'subject': _('Document-%s Expired On %s') % (i.name, i.expiry_date),
                        #     'author_id': self.env.user.partner_id.id,
                        #     'body_html': mail_content,
                        #     'email_to': document_ids.login,
                        #     # 'email_to': i.employee_ref.work_email,
                        # }
                        # self.env['mail.mail'].create(main_content).send()
                    elif i.second_reminder_date == today:
                        schedule_activity = self.env['mail.activity'].create({
                            'note': (('Second Reminder notification for the expiry of %s Document') % (i.employee_ref.name)),
                            'res_id': i.id,
                            'res_model_id': move_res_model_id,
                            'summary': (('Second Reminder notification for the expiry of %s Document') % (i.employee_ref.name)),
                            'date_deadline': i.second_reminder_date,
                            'user_id': document_ids.id,
                        })
                        schedule_activity.action_close_dialog()
                        template_id = self.env['ir.model.data'].get_object_reference(
                            'employee_documents_expiry',
                            'email_template_employee')[1]
                        if template_id:
                            email_template_obj = self.env['mail.template'].browse(template_id)
                            values = email_template_obj.generate_email(i.id, ['subject', 'body_html', 'email_from',
                                                                              'email_to', 'partner_to', 'email_cc',
                                                                              'reply_to',
                                                                              'scheduled_date'])
                            i.aging_date = i.model_field.first_reminder_threshold
                            # mail_content = '<p> Greetings from TASC!! <br></br> <br></br>Please be informed that below employee is about to expiry in ' + i.first_reminder_threshhold + 'days' +\
                            #                '<br></br><b>Please review the below to take necessary action to renew the </b>'+ i.name + \
                            #                'Please write to projects@tascoutsourcing.com for any further assistance on renewal of the document."</p>'
                            values['email_from'] = self.env['res.users'].browse(self.env.uid).company_id.email
                            values['email_to'] = document_ids.login
                            # values['body_html'] = mail_content
                            # values['subject'] = _('Reshmi Document-%s Expired On %s') % (i.name, i.expiry_date),
                            msg_id = self.env['mail.mail'].create(values)
                            if msg_id:
                                msg_id._send()
                    elif i.third_reminder_date == today:
                        schedule_activity = self.env['mail.activity'].create({
                            'note': (('Third Reminder notification for the expiry of %s Document') % (i.employee_ref.name)),
                            'res_id': i.id,
                            'res_model_id': move_res_model_id,
                            'summary': (('Third Reminder notification for the expiry of %s Document') % (i.employee_ref.name)),
                            'date_deadline': i.third_reminder_date,
                            'user_id': document_ids.id,
                        })
                        schedule_activity.action_close_dialog()
                        template_id = self.env['ir.model.data'].get_object_reference(
                            'employee_documents_expiry',
                            'email_template_employee')[1]
                        if template_id:
                            email_template_obj = self.env['mail.template'].browse(template_id)
                            values = email_template_obj.generate_email(i.id, ['subject', 'body_html', 'email_from',
                                                                              'email_to', 'partner_to', 'email_cc',
                                                                              'reply_to',
                                                                              'scheduled_date'])
                            i.aging_date = i.model_field.first_reminder_threshold
                            # mail_content = '<p> Greetings from TASC!! <br></br> <br></br>Please be informed that below employee is about to expiry in ' + i.first_reminder_threshhold + 'days' +\
                            #                '<br></br><b>Please review the below to take necessary action to renew the </b>'+ i.name + \
                            #                'Please write to projects@tascoutsourcing.com for any further assistance on renewal of the document."</p>'
                            values['email_from'] = self.env['res.users'].browse(self.env.uid).company_id.email
                            values['email_to'] = document_ids.login
                            # values['body_html'] = mail_content
                            # values['subject'] = _('Reshmi Document-%s Expired On %s') % (i.name, i.expiry_date),
                            msg_id = self.env['mail.mail'].create(values)
                            if msg_id:
                                msg_id._send()
        for a in match:
            # if a.reminder_date:
            #     exp_date = a.reminder_date - timedelta(days=7)
            #     # if date_now >= exp_date:
            if a.first_reminder_date == today or a.second_reminder_date == today or a.third_reminder_date == today:
                if a.employee_ref.client_name.employee_expiry is True:
                    template_id = self.env['ir.model.data'].get_object_reference(
                        'employee_documents_expiry',
                        'email_template_employee')[1]
                    if template_id:
                        email_template_obj = self.env['mail.template'].browse(template_id)
                        values = email_template_obj.generate_email(a.id, ['subject', 'body_html', 'email_from',
                                                                          'email_to', 'partner_to', 'email_cc',
                                                                          'reply_to',
                                                                          'scheduled_date'])
                        values['email_from'] = self.env['res.users'].browse(self.env.uid).company_id.email
                        values['email_to'] = a.employee_ref.work_email
                        # values['body_html'] = mail_content
                        # values['subject'] = _('Reshmi Document-%s Expired On %s') % (i.name, i.expiry_date),
                        msg_id = self.env['mail.mail'].create(values)
                        if msg_id:
                            msg_id._send()
                    template_id = self.env['ir.model.data'].get_object_reference(
                        'employee_documents_expiry',
                        'email_template_employee')[1]
                    if template_id:
                        email_template_obj = self.env['mail.template'].browse(template_id)
                        values = email_template_obj.generate_email(i.id, ['subject', 'body_html', 'email_from',
                                                                          'email_to', 'partner_to', 'email_cc',
                                                                          'reply_to',
                                                                          'scheduled_date'])
                        i.aging_date = i.model_field.first_reminder_threshold
                        # mail_content = '<p> Greetings from TASC!! <br></br> <br></br>Please be informed that below employee is about to expiry in ' + i.first_reminder_threshhold + 'days' +\
                        #                '<br></br><b>Please review the below to take necessary action to renew the </b>'+ i.name + \
                        #                'Please write to projects@tascoutsourcing.com for any further assistance on renewal of the document."</p>'
                        values['email_from'] = self.env['res.users'].browse(self.env.uid).company_id.email
                        values['email_to'] = a.employee_ref.client_name.email
                        # values['body_html'] = mail_content
                        # values['subject'] = _('Reshmi Document-%s Expired On %s') % (i.name, i.expiry_date),
                        msg_id = self.env['mail.mail'].create(values)
                        if msg_id:
                            msg_id._send()
                    # mail_content = "  Hello  " + a.employee_ref.name + ",Document " + a.name + " is going to expire on " + \
                    #                str(a.expiry_date) + ". Please renew it before expiry date"
                    # main_content = {
                    #     'subject': _('Document-%s Expired On %s') % (a.name, a.expiry_date),
                    #     'author_id': self.env.user.partner_id.id,
                    #     'body_html': mail_content,
                    #     'email_to': a.employee_ref.work_email,
                    #     # 'email_to': i.employee_ref.work_email,
                    # }
                    # self.env['mail.mail'].create(main_content).send()
                    # cust_content = "  Hello  " + a.employee_ref.client_name.name + ",Document " + a.name + " for the corresponding Employee " + a.employee_ref.name + " is going to expire on " + \
                    #                str(a.expiry_date) + ". Please renew it before expiry date"
                    # cust_content = {
                    #     'subject': _('Document-%s Expired On %s') % (a.name, a.expiry_date),
                    #     'author_id': self.env.user.partner_id.id,
                    #     'body_html': cust_content,
                    #     'email_to': a.employee_ref.client_name.email,
                    #     # 'email_to': i.employee_ref.work_email,
                    # }
                    # self.env['mail.mail'].create(cust_content).send()

 #    + ",for the corresponding Employee " + \
 #    a.employee_ref.name + " is going to expire on " + \


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

    name = fields.Char(string='Document Number',)
    document_name = fields.Many2one('employee.checklist', string='Document Type')
    description = fields.Text(string='Description', copy=False)
    expiry_date = fields.Date(string='Expiry Date', copy=False)
    first_reminder_date = fields.Date(string='First Reminder Date', compute='get_reminder_date')
    second_reminder_date = fields.Date(string='Second Reminder Date', compute='get_reminder_date')
    third_reminder_date = fields.Date(string='Third Reminder Date', compute='get_reminder_date')
    employee_ref = fields.Many2one('hr.employee', copy=False)
    employee_id = fields.Char(related='employee_ref.emp_id', string='Employee ID')
    google_attachment_id = fields.Char(string="Google drive Attachment")
    doc_attachment_id = fields.Many2many('ir.attachment', 'doc_attach_rel', 'doc_id', 'attach_id3', string="Attachment",
                                         help='You can attach the copy of your document', copy=False)
    issue_date = fields.Date(string='Issue Date', default=fields.Date.context_today, copy=False)
    employee_name = fields.Char(related='employee_ref.name',string="Employee Name")
    model_name = fields.Many2one('ir.model', help="Choose the model name", string="Model",
                                 ondelete='cascade',domain="[('model', '=','res.partner')]")
    # model_field_name = fields.Many2one('ir.model.fields', string='Field Name', help="Choose the field",
    #                               domain="[('model_id', '=','hr.employee')]",
    #                               required=True, ondelete='cascade')
    model_field = fields.Many2one('document.threshhold',string='Document Type',domain="[('form_type', '=','employee')]")
    document_namee = fields.Char(string='Document Name', related='model_field.name',readonly=True)
    aging_date = fields.Char(string='First Reminder Date',compute='get_ageing_date')

    # @api.onchange('document_namee')
    # def _get_expiry_date(self):
    #     # employee_master = self.env['hr.employee'].search([('field_description', '=', self.document_namee)])
    #     for i in self.model_field_name:
    #         if i.field_description == self.document_namee:
    #             print('eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',i.name)
    #     # if employee_master:
    #     #     self.expiry_date = employee_master.


    def get_ageing_date(self):
        self.aging_date = 0
        today = fields.Date.today()
        for i in self:
            if i.first_reminder_date == today:
                i.aging_date = i.model_field.first_reminder_threshold
            elif i.second_reminder_date == today:
                i.aging_date = i.model_field.second_reminder_threshold
            elif i.third_reminder_date == today:
                i.aging_date = i.model_field.third_reminder_threshold


    def get_reminder_date(self):
        self.first_reminder_date = 0
        self.second_reminder_date = 0
        self.third_reminder_date = 0
        for i in self:
            document_threshhold = self.env['document.threshhold'].search([('name', '=', i.document_namee),
                                                                          ('form_type', '=','employee')])
            for document in document_threshhold:
                if document_threshhold:
                    if i.expiry_date != False:
                        date_format = '%Y-%m-%d'
                        orig_date = str(i.expiry_date)
                        dtObj = datetime.strptime(orig_date, date_format)
                        first_reminder = timedelta(days=int(document.first_reminder_threshold))
                        second_reminder = timedelta(days=int(document.second_reminder_threshold))
                        third_reminder = timedelta(days=int(document.third_reminder_threshold))
                        first_reminder_date = dtObj - first_reminder
                        second_reminder_date = dtObj - second_reminder
                        third_reminder_date = dtObj - third_reminder
                        print('Expiry dateeee',i.expiry_date)
                        print('days',first_reminder)
                        print('reminder date',first_reminder_date)
                        i.first_reminder_date = first_reminder_date
                        i.second_reminder_date = second_reminder_date
                        i.third_reminder_date = third_reminder_date


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    client_name = fields.Many2one('res.partner', string='Client Name')
    date_of_joining = fields.Date("Date of Joining")
    passport_expiry = fields.Date("Passport Expiry Date")
    visa_valid_from = fields.Date("Visa Valid From")
    probation_term_months = fields.Char(string='Probation Term Months')
    visa_type = fields.Selection([('residencevisa', 'Residence Visa'), ('tecom', 'Residence Visa TECOM'),('labourcard', 'Labour Card'), ('missionvisa', 'Mission Visa')
                                  , ('nonsponsored', 'Non Sponsored ID Card'), ('parttime', 'Part Time Labour Card'),
                                  ('temporary', 'Temporary Labour Card')], string='Visa Type')
    ctc = fields.Monetary('CTC', currency_field='currency_id', default=0.0,compute="_calculate_ctc")
    allowance = fields.Monetary('Allowances', currency_field='currency_id', default=0.0)
    base_salary = fields.Monetary('Base Salary', currency_field='currency_id', default=0.0)
    basic = fields.Monetary('Basic', currency_field='currency_id', default=0.0)
    hra = fields.Monetary('HRA', currency_field='currency_id', default=0.0)
    transport = fields.Monetary('Transport', currency_field='currency_id', default=0.0)
    other = fields.Monetary('Other', currency_field='currency_id', default=0.0)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    iban_number = fields.Char(string='IBAN Number')
    emp_id = fields.Char(string='Employee ID')
    coverage_category = fields.Selection([('familyfloater', 'Family Floater'), ('na', 'Not Applicable'), ('self', 'Self'),], string='Coverage Category')
    coverage_level = fields.Selection([('age0-15', 'Age 0-15'),('age16-20', 'Age 16-20'),('age19-34', 'Age 19-34'),
                                       ('age21-25', 'Age 21-25'),
                                       ('age26-30', 'Age 26-30'),
                                           ('age31-35', 'Age 31-35'),('age35-41', 'Age 35-41'),('age36-40', 'Age 36-40'),
                                       ('age41-45', 'Age 41-45'),('age42-49', 'Age 42-49'),('age 51-55', 'Age  51-55'),
                                       ('na', 'Not Applicable'),('self', 'Self'),('selfone', 'Self + 1'),('selfto', 'Self + 2'),
                                       ('self3', 'Self + 3'),
                                       ('self4', 'Self + 4'),

                                       ], string='Coverage Level')
    insurance_category = fields.Selection([('blue', 'Blue'), ('gold', 'Gold'), ('silver', 'Silver'),('platinum', 'Platinum'),],
                                          string='Insurance Category')
    employee_status = fields.Selection([('active', 'Active'), ('inactive', 'Inactive'), ('applicant', 'Applicant'),],
                                       string='Employee Status')
    ministry_of_labor = fields.Char(string='Ministry Of Labour')
    mol_expiry = fields.Date("MOL Expiry Date")
    labor_card = fields.Char(string='Labour Card NO')
    lc_expiry = fields.Date("LC Expiry Date")
    insurance_card_expiry = fields.Date("Insurance Card Expiry")
    insurance_card_number = fields.Date("Insurance Card Number")
    emirates_id = fields.Char(string='Emirates ID')
    eid_expiry = fields.Date("EID Expiry Date")
    ohc_expiry = fields.Date("OHC Expiry Date")
    dl_expiry = fields.Date("DL Expiry Date")
    access_card_expiry = fields.Date("Access Card Expiry Date")


    def _calculate_ctc(self):
        self.ctc = 0
        for salary in self:
            salary.ctc = salary.allowance + salary.base_salary + salary.basic + salary.hra + salary.transport + salary.other
        return True

    def _document_count(self):
        for each in self:
            document_ids = self.env['hr.employee.document'].search([('employee_ref', '=', each.id)])
            each.document_count = len(document_ids)


    def document_view(self):
        self.ensure_one()
        domain = [
            ('employee_ref', '=', self.id)]
        emp_obj = self.env['hr.employee.document']
        reference = emp_obj.search([('employee_ref', '=', self.id)])
        # if reference:
        #     emmp_id = emp_obj[0].id
        # else:
        #     reference = emp_obj.create({
        #         "employee_ref": self.id,
        #     })
        #     emmp_id = reference.id
        return {
            'name': _('Documents'),
            'domain': domain,
            'res_model': 'hr.employee.document',
            # 'res_id': emmp_id,
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click to Create for New Documents
                        </p>'''),
            'limit': 80,
            'context': {'default_employee_ref': self.id}
        }

    document_count = fields.Integer(compute='_document_count', string='# Documents')


class HrEmployeeAttachment(models.Model):
    _inherit = 'ir.attachment'

    doc_attach_rel = fields.Many2many('hr.employee.document', 'doc_attachment_id', 'attach_id3', 'doc_id',
                                      string="Attachment", invisible=1)
