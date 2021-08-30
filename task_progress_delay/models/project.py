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

class Project(models.Model):
    _inherit = "project.project"

    prefix_code = fields.Char(string='Prefix Code', required=True)
    category = fields.Selection(
        [('employee', 'Employee'), ('clients', 'Clients'), ('admin', 'Admin'), ('employees', 'Employees'), ],
        string='Category')
    sla_in_hours = fields.Float(string='SLA(in hours)')
    turnaround_time_days = fields.Float(string='TurnAround Time(in days)')
    turnaround_time_hours = fields.Float(string='TurnAround Time(in hours)', compute='_get_turnaround_hours')

    def _get_turnaround_hours(self):
        self.turnaround_time_hours = 0
        company_id = self.env.company.id
        resource = self.env['resource.calendar'].search(
            [('company_id', '=', company_id), ('company_calendar', '=', True)])
        for project in self:
            # for i in resource:
            if resource:
                project.turnaround_time_hours = project.turnaround_time_days * resource.hours_per_day


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    stage_name = fields.Many2one('project.task.type', string="Stage Name", domain="[('project_ids', '=', project_id)]")
    cost_stage = fields.Float(string='Task Cost')
    gov_fee = fields.Float(string='Government Fee')

    @api.model
    def create(self, vals):
        # assigning the sequence for the record
        # if vals.get('code', _('New')) == _('New'):
        res = super(AccountAnalyticLine, self).create(vals)
        for j in self:
            # if j.stage_name.name != self.stage_id.name:
            # 	raise Warning(_('"Please Fill the Stage Name"'))
            if not j.cost_stage and j.unit_amount:
                raise Warning(_('"Please Fill the Cost and Duration"'))
        return res


# stage_name = fields.Many2one(string="Stage Name", related='task_id.stage_id.name',readonly=True)
# task_name = fields.Many2one('project.task.type')


class projectTaskType(models.Model):
    _inherit = 'project.task.type'

    lead_time = fields.Float('Turnaround Time')
    allocation = fields.Float('Allocation in project')


class ProjectTask(models.Model):
    _inherit = 'project.task'

    task_code = fields.Char(string="Task Number")
    task_stage = fields.Char(string="Stage Name", related='stage_id.name')
    type = fields.Selection(
        [('monthlyretainer', 'Monthly Retainer'), ('payasyougo', 'Pay as you go'), ('hybrid', 'Hybrid'), ],
        string='Type', related='partner_id.customer_def_type')
    task_progress = fields.Float(string="Task Progress", default=0.0, compute='calculate_progress')
    progress_histogry_ids = fields.One2many('task.progress.history', 'task_id')
    prefix_code = fields.Char(string='Prefix Code')
    planned_hours = fields.Float(related='project_id.turnaround_time_days',
                                 help='Time planned to achieve this task (including its sub-tasks).', readonly="0",
                                 tracking=True)
    planned_days_project = fields.Float(related='project_id.turnaround_time_days', string='Turnaround Time (in Days)')
    delay_notify = fields.Char(string='Delay Color', compute='calculate_time_delay')
    total_cost = fields.Float(string="Total Cost", default=0.0, compute='calculate_task_cost')
    total_task_cost = fields.Float(string="Total Task Cost", default=0.0, compute='calculate_task_cost')
    total_govt_fee = fields.Float(string="Total Government Fee", default=0.0, compute='calculate_task_cost')
    # date_deadline = fields.Datetime(string="Date Deadline", compute='get_date_deadline')
    planned_date_begin = fields.Datetime("Start date")
    planned_date_end = fields.Datetime("End date", store=True)

    # @api.onchange('planned_date_end')
    # def _change_deadline(self):
    # 	for i in self:
    # 		i.date_deadline = i.planned_date_end

    def open_task_report(self):
        timesheet = self.env['account.analytic.line'].search([])
        domains = []
        for rec in timesheet:
            if rec.task_id.delay_notify == self.delay_notify:
                domains.append(rec.id)
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'account.analytic.line',
                    'target': 'current',
                    'view_id': self.env.ref('hr_timesheet.hr_timesheet_line_tree').id,
                    'view_mode': 'tree',
                    'context': {'group_by': 'task_id'},
                    'domain': [('task_id', '=', self.id)],
                    'res_id': rec.id,
                }

    @api.onchange('planned_date_begin')
    @api.depends('planned_date_begin')
    def get_date_deadline(self):
        # self.date_deadline = False
        self.planned_date_end = False
        for self in self:
            if self.planned_date_begin != False or self.planned_date_end != False:
                # datetime_str = '09/19/18 13:55:26'
                string_start = str(self.planned_date_begin)
                datetime_object = datetime.strptime(string_start, '%Y-%m-%d %H:%M:%S')
                date_deadline = timedelta(days=int(self.planned_days_project))
                date_deadline_final = datetime_object + date_deadline
                if date_deadline_final.isoweekday() == 5:
                    self.date_deadline = date_deadline_final + timedelta(days=2)
                    self.planned_date_end = date_deadline_final + timedelta(days=2)
                elif date_deadline_final.isoweekday() == 6:
                    self.date_deadline = date_deadline_final + timedelta(days=1)
                    self.planned_date_end = date_deadline_final + timedelta(days=1)
                else:
                    self.date_deadline = date_deadline_final
                    self.planned_date_end = date_deadline_final

    #  aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',self.stage_id.id)
    # if j.stage_name.name != self.task_stage:
    # 	raise Warning(_('"Please Fill the Stage Name"'))
    # 	# if not j.cost_stage:
    # 	# 	raise Warning(_('"Please Fill the Cost"'))

    def calculate_task_cost(self):
        self.total_task_cost = 0
        self.total_govt_fee = 0
        self.total_cost = 0
        for rec in self:
            tasks = self.env['account.analytic.line'].search([('task_id', '=', rec.id)])
            if tasks:
                for task in tasks:
                    rec.total_task_cost += task.cost_stage
                    rec.total_govt_fee += task.gov_fee
                    rec.total_cost = rec.total_task_cost + rec.total_govt_fee

    def calculate_time_delay(self):
        self.delay_notify = 0
        for rec in self:
            if rec.effective_hours > rec.planned_hours:
                rec.delay_notify = 'True'
        return True

    @api.model
    def create(self, vals):
        # assigning the sequence for the record
        # if vals.get('code', _('New')) == _('New'):
        res = super(ProjectTask, self).create(vals)
        for j in self.timesheet_ids:
            if not j.cost_stage or j.unit_amount:
                raise Warning(_('"Please Fill the Cost and Duration"'))
        project = self.env['project.project'].search([('name', '=', res.project_id.name)])
        if project:
            res.write({'prefix_code': project.prefix_code,
                       })
            vals['task_code'] = self.env['ir.sequence'].next_by_code('project.task')
            seq = vals['task_code'].replace('TASK', res.prefix_code)
            res.write({
                'task_code': seq,
            })
        return res

    @api.depends('stage_id')
    def calculate_progress(self):
        self.task_progress = 0
        for rec in self:
            if rec.stage_id and rec.stage_id.sequence == 0:
                rec.task_progress = 0.0
            else:
                stages = self.env['project.task.type'].search([])
                prev_stages = []
                for stage in stages:
                    if rec.project_id in stage.project_ids and stage.sequence < rec.stage_id.sequence:
                        prev_stages.append(stage)
                for prev_stage in prev_stages:
                    rec.task_progress = rec.task_progress + prev_stage.allocation
        return True

    def write(self, vals):
        if vals.get('stage_id', False):
            total_time = 0
            if len(self.timesheet_ids) == 0:
                raise Warning(_('"Please Fill the task cost or Government fee"'))
            for j in self.timesheet_ids:
                if j.cost_stage + j.gov_fee == 0:
                    raise Warning(_('"Please Fill the task cost or Government fee"'))
                if not j.cost_stage:
                    raise Warning(_('"Please Fill the Cost"'))
                if self.stage_id.name == j.stage_name.name:
                    total_time += j.unit_amount
                    history_vals = {
                        'stage_from_id': self.stage_id.id,
                        'stage_to_id': vals['stage_id'],
                        'task_id': self.id,
                        'date': fields.Date.today(),
                        'time_taken': total_time,
                    }
                vals['progress_histogry_ids'] = [(0, 0, history_vals)]
        return super(ProjectTask, self).write(vals)

    # def write(self, vals):
    #     if vals.get('stage_id', False):
    #         total_time = 0
    #         for j in self.timesheet_ids:
    #             if not j.cost_stage:
    #                 raise Warning(_('"Please Fill the Cost"'))
    #             if self.stage_id.name == j.stage_name.name:
    #                 total_time += j.unit_amount
    #             history_vals = {
    #                 'stage_from_id': self.stage_id.id,
    #                 'stage_to_id': vals['stage_id'],
    #                 'task_id': self.id,
    #                 'date': fields.Date.today(),
    #                 'time_taken': total_time,
    #             }
    #             vals['progress_histogry_ids'] = [(0, 0, history_vals)]
    #     return super(ProjectTask, self).write(vals)


class taskProgressHistory(models.Model):
    _name = 'task.progress.history'
    _description = 'Task Progress History'

    task_id = fields.Many2one('project.task')
    stage_from_id = fields.Many2one('project.task.type', string='From Stage')
    stage_to_id = fields.Many2one('project.task.type', string='To Stage')
    date = fields.Date('Date Completed')
    delay = fields.Integer(string='Delay', compute='calculate_time_delay')
    time_taken = fields.Float(string='Time Elapsed')
    delay_color = fields.Char(string='Delay Color', compute='calculate_time_taken')

    def calculate_time_delay(self):
        self.delay = 0
        for rec in self:
            rec.delay = rec.stage_from_id.lead_time - rec.time_taken
        return True

    def calculate_time_taken(self):
        self.delay_color = 0
        for rec in self:
            if rec.delay < 0:
                rec.delay_color = 'True'
        return True


class Worked_schedule(models.Model):
    _inherit = "resource.calendar"

    company_calendar = fields.Boolean(string='Company Calendar')
