# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class Partner(models.Model):

	_inherit = 'res.partner'

	dob = fields.Date(string='Date of Birth', required=True)