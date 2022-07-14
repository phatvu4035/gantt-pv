# -*- coding: utf-8 -*-

from odoo import models, api

    
class IrActionsActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'

    @api.model
    def _get_project_actions_for_gantt(self):
        return [
            'project.project_task_action_sub_task',
            'project.action_view_all_task',
            'project.act_project_project_2_project_task_all',
            'project.dblc_proj',
            'project.act_res_users_2_project_task_opened',
            'project.action_view_task_overpassed_draft',
            ]
        
    @api.model
    def _add_project_gantt_view(self):
        self._add_gantt_view(self._get_project_actions_for_gantt())
