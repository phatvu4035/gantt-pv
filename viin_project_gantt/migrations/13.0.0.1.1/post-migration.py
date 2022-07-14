# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def _populate_task_planned_dates(env):
    env['project.task'].with_context(active_test=False).search([('planned_date_start', '=', False)])._compute_planned_date_start()
    env['project.task'].with_context(active_test=False).search([('planned_date_end', '=', False)])._compute_planned_date_end()


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _populate_task_planned_dates(env)

