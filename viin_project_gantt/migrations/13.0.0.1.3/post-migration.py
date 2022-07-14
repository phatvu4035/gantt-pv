# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID

    
def _remove_gantt_from_report_project_task_user(env):
    action = env['ir.actions.act_window.view']
    action._remove_gantt_view(['project.action_project_task_user_tree'])


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _remove_gantt_from_report_project_task_user(env)

