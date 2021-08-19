# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta

from odoo import models, fields, api, _
from ast import literal_eval
from odoo.exceptions import UserError, ValidationError
from odoo.exceptions import Warning


class DocumentThreshhold(models.Model):
    _name = 'document.threshhold'
    _description = 'Document Threshhold'
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = 'name'

    document_part = fields.Many2one('ir.model.fields', string='Document Type', help="Choose the field",
                                  domain="[('model_id', '=','res.partner')]",
                                  ondelete='cascade')
    document_emp = fields.Many2one('ir.model.fields', string='Document Type', help="Choose the field",
                                  domain="[('model_id', '=','hr.employee')]",
                                  ondelete='cascade')
    name = fields.Char(string='Document Name',compute='_set_name_emp_part',readonly=True)
    first_reminder_threshold = fields.Char(string='First Reminder Threshold (in Days)')
    second_reminder_threshold = fields.Char(string='Second Reminder Threshold (in Days)')
    third_reminder_threshold = fields.Char(string='Third Reminder Threshold (in Days)')
    form_type = fields.Selection([('customer', "Customer"), ('employee', "Employee")], string="Form Type")

    # @api.onchange('form_type')
    def _set_name_emp_part(self):
        for self in self:
            if self.form_type == 'customer':
                print('fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff',self.document_part.field_description)
                self.name = self.document_part.field_description
            elif self.form_type == 'employee':
                self.name = self.document_emp.field_description

    @api.model
    def create(self, vals):
        doc_count = self.env['document.threshhold'].search([('document_part', '=', vals['document_part']),('document_emp', '=', vals['document_emp'])])
        if doc_count:
            raise ValidationError(_("Threshold is already entered for the selected document"))
        res = super(DocumentThreshhold, self).create(vals)
        return res