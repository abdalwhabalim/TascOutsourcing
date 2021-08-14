# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta

from odoo import models, fields, api, _
from ast import literal_eval


class DocumentThreshhold(models.Model):
    _name = 'document.threshhold'
    _description = 'Document Threshhold'
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = 'document_name'

    document_type = fields.Many2one('ir.model.fields', string='Document Type', help="Choose the field",
                                  domain="[('model_id', 'in',('res.partner','hr.employee'))]",
                                  required=True, ondelete='cascade')
    document_name = fields.Char(string='Document Name', related='document_type.field_description',readonly=True)
    reminder_threshold = fields.Char(string='Reminder Threshold (in Days)')
    form_type = fields.Selection([('customer', "Customer"), ('employee', "Employee")], string="Form Type")

