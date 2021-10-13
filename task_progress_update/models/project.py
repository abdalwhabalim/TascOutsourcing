# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, date
from datetime import time
from odoo.tools.translate import _
from odoo.exceptions import Warning
from dateutil.relativedelta import relativedelta
from datetime import datetime
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import datetime as dt
from odoo.exceptions import ValidationError, UserError


class projectTaskType(models.Model):
    _inherit = 'project.task.type'

    is_start_stage = fields.Boolean('Start Stage', default=False)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    check_entered = fields.Boolean(related='stage_name.is_closed', string='Is Close Stage')
    end_date_boolean = fields.Boolean('End Stage', default=False)
    is_start_stages = fields.Boolean(related='stage_name.is_start_stage', string='Is Start Stage')
    red_boolean = fields.Boolean(string='Red Boolean', compute='compute_red_boolean')
    green_boolean = fields.Boolean(string='green Boolean', compute='compute_green_boolean')
    amber_boolean = fields.Boolean(string='amber Boolean', compute='compute_amber_boolean')

    @api.onchange('end_date_boolean', )
    @api.constrains('end_date_boolean')
    def close_stage(self):
        if self.task_id:
            self.task_id.check_task_closed = True

    def compute_red_boolean(self):
        for rec in self:
            rec.red_boolean = False
            if rec.turn_time:
                if rec.unit_amount:
                    if rec.turn_time < rec.unit_amount:
                        rec.red_boolean = True
                    else:
                        rec.red_boolean = False

    def compute_green_boolean(self):
        for rec in self:
            rec.green_boolean = False
            if rec.start_dates and rec.end_dates:
                if rec.turn_time:
                    if rec.unit_amount:
                        if rec.unit_amount <= rec.turn_time:
                            rec.green_boolean = True
                        else:
                            rec.green_boolean = False

    def compute_amber_boolean(self):
        for rec in self:
            rec.amber_boolean = False
            if rec.start_dates and not rec.end_dates:
                rec.amber_boolean = True
            else:
                rec.amber_boolean = False


class ProjectTask(models.Model):
    _inherit = 'project.task'

    check_task_closed = fields.Boolean('Close SLA', default=False)
