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



class WorkflowConfiguration(models.Model):
    _name = 'workflow.config'
    _inherit =['mail.thread','mail.activity.mixin']
    _description = 'Workflow Configuration'
    _rec_name = 'project_id'

    project_id = fields.Many2one('project.project',string='Project',required=True,)
    line_ids = fields.One2many('workflow.line','workflow_id',string='SLA Workflow',)


class WorkflowLine(models.Model):
    _name = 'workflow.line'

    workflow_id = fields.Many2one('workflow.config',string='Workflow')
    stage_id = fields.Many2one('project.task.type',string="Stages")

