# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def _fix_task_planned_dates(env):
    env['project.task'].with_context(active_test=False).search([])._compute_planned_date_end()


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _fix_task_planned_dates(env)

