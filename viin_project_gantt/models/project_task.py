# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, float_is_zero


class ProjectTask(models.Model):
    _name = 'project.task'
    _inherit = ['project.task', 'gantt.mixin']
    
    _sql_constraints = [
        ('resource_allocation', 'CHECK(resource_allocation > 0.0)', 'The Resource Allocation must not be greater than zero (0).')
    ]
        
    planned_date_start = fields.Datetime(string='Planned Start Date', default=fields.Datetime.now)
    planned_date_end = fields.Datetime(string='Planned End Date', compute='_compute_planned_date_end', store=True, readonly=False)
    depends_count = fields.Integer(string='Depends', compute='_compute_depends_count')
    depend_ids = fields.Many2many('project.task', 'project_task_dependency_rel', 'task_id', 'depend_task_id', string='Depend Tasks',
                               help="The tasks on which this task depends directly.")
    recursive_depend_ids = fields.Many2many('project.task', string='Recursive Depend Tasks',
                                                compute='_compute_recursive_depend_ids', search='_search_task_and_its_dependency',
                                                store=False, compute_sudo=True,
                                                help="The tasks on which the current task recursively depends on (incl. direct and indirect dependencies).")
    depending_task_ids = fields.Many2many('project.task', 'project_task_dependency_rel', 'depend_task_id', 'task_id',
                                          string='Depending Tasks', readonly=True,
                                          help="The tasks that directly depend on this task.")
    recursive_depending_ids = fields.Many2many('project.task', string='Recursive Depending Tasks',
                                               compute='_compute_recursive_depending_ids', search='_search_task_and_its_depending',
                                               store=False, compute_sudo=True)
    resource_allocation = fields.Float(string='Resource Allocation', default=100.0, required=True,
                                       help="The working time percentage that the resources assigned to this task could allocate for the task."
                                       " This helps calculate Planned End Date more realistic.\n"
                                       "For example, 50% resource allocation will result the task to take 2 times against the planned hours for completion.")

    dependency_level = fields.Integer(string='Dependency Level', compute='_compute_dependency_level', store=True, recursive=True,
                                      help="The level of this task in dependency tree (e.g. if it depends on nothing, its dependency"
                                      " level will be zero (0)")
    
    bad_resource_allocation_task_ids = fields.Many2many('project.task', string='Bad Resource Allocation Tasks',
                                                        compute='_compute_bad_resource_allocation_task_ids',
                                                        help="The tasks of the same assignment with time range overlapping")
    
    bad_resource_allocation_task_alert = fields.Char(string='Bad Resource Allocation Alert', default=False,
                                                     translate=True, compute='_compute_bad_resource_allocation_task_alert')
    
              
    @api.depends('planned_date_start', 'planned_hours', 'resource_allocation')
    def _compute_planned_date_end(self):
        for r in self:
            r.planned_date_end = r._get_planned_date_end(compute_leaves=True)

    @api.depends('depend_ids', 'depend_ids.dependency_level')
    def _compute_dependency_level(self):
        for r in self:
            # do not compute on view's onchange as it may get into circular recursion as the a
            # constrain `_check_circular_dependency` does its job after create/write only
            if isinstance(r.id, models.NewId):
                r.dependency_level = 0
                continue
            r.dependency_level = r._get_dependency_level()

    def _compute_depends_count(self):
        if not self.ids:
            return
        self.flush()
        self.env.cr.execute(
            """
            SELECT task_id, count(depend_task_id) as depend_count
            FROM project_task_dependency_rel AS dep_rel 
            WHERE dep_rel.task_id IN %s GROUP BY dep_rel.task_id
            """, (tuple(self.ids),)
            )
        data = self.env.cr.fetchall()
        mapped_data = dict(data)
        for r in self:
            r.depends_count = mapped_data.get(r.id, 0)

    def _compute_bad_resource_allocation_task_ids(self):
        if not self.ids:
            return
        self.env.cr.execute("""
            WITH overlap_map AS (
                SELECT t.id, overlap.id AS overlap_id
                FROM project_task AS t
                    LEFT JOIN project_task AS overlap ON overlap.user_id = t.user_id
                        AND t.id != overlap.id
                        AND (overlap.planned_date_start, overlap.planned_date_end) OVERLAPS (t.planned_date_start, t.planned_date_end)
                WHERE t.id IN %s AND t.user_id IS NOT NULL AND overlap.user_id IS NOT NULL
                GROUP BY t.id, overlap.id
            )
            SELECT
                overlap_map.id,
                array_agg(overlap_map.overlap_id) AS bad_resource_allocation_task_ids
            FROM overlap_map
            WHERE overlap_map.overlap_id IS NOT NULL
            GROUP BY overlap_map.id
            """, (tuple(self.ids),))

        res = self.env.cr.fetchall()
        overlapping_map = dict(res)

        for r in self:
            # need to filter out the task that don't have permission to read
            readable_ids = self.env['project.task'].search([('id', 'in', overlapping_map.get(r.id, []))]).ids
            r.bad_resource_allocation_task_ids = [(6, 0, readable_ids)]
            r.bad_resource_allocation_task_count = len(overlapping_map.get(r.id, []))

    def _compute_recursive_depend_ids(self):
        self.flush()
        mapped_data = self._get_recursive_dependency_map()
        for r in self:
            r.recursive_depend_ids = [(6, 0, mapped_data.get(r.id, []))]
    
    def _compute_recursive_depending_ids(self):
        self.flush()
        mapped_data = self._get_recursive_depending_map()
        for r in self:
            r.recursive_depending_ids = [(6, 0, mapped_data.get(r.id, []))]

    @api.constrains('planned_date_start', 'planned_date_end')
    def _check_planned_date_start_planned_date_end(self):
        for r in self:
            if r.planned_date_start and r.planned_date_end and r.planned_date_start > r.planned_date_end:
                raise UserError(_("The Planned Start Date must be earlier or equal to the Planned End Date"))

    @api.constrains('depend_ids')
    def _check_circular_dependency(self):
        if not self._check_m2m_recursion('depend_ids'):
            raise ValidationError(
                _("You cannot create recursive dependencies between tasks.")
            )
            
    def write(self, vals):
        no_date_assign = self.env['project.task']
        if vals.get('user_id'):
            no_date_assign = self.filtered(lambda rec: not rec.date_assign)
            new_vals = vals.copy()
            new_vals.update({
                'planned_date_start': vals.get('date_assign', fields.Datetime.now())
                })
            super(ProjectTask, no_date_assign).write(new_vals)
        return super(ProjectTask, self - no_date_assign).write(vals)

    def _get_planned_date_end(self, start_dt=None, compute_leaves=False, domain=None, resource=None):
        """
        Method to calculate end date after having planned hours and start date based on the task
        :param start_dt: the planned date start. If not given, the planned start date of the create date of the task will be used
        :param compute_leaves: controls whether or not this method is taking into account the global leaves.
        :param domain: controls the way leaves are recognized. None means default value ('time_type', '=', 'leave')
        :param resource: where or not bind a resource for its own leaves to take into account

        :return: planned end date after having planned hours and start date
        :rtype: datetime
        """
        self.ensure_one()
        start_dt = start_dt or self.planned_date_start or self.create_date or fields.Datetime.now()
        calendar = self.project_id.resource_calendar_id or self.company_id.resource_calendar_id
        realistic_hours = self.planned_hours or 0.0
        if not float_is_zero(self.resource_allocation, 2):
            realistic_hours = float_round((self.planned_hours or 0.0) * 100 / self.resource_allocation, precision_digits=2, rounding_method='UP')
        if not calendar:
            raise ValidationError(_("There is no working calendar specified for either the related project or the company."
                                    " Please specify one before scheduling your tasks."))
        
        return calendar.plan_hours(
            realistic_hours,
            start_dt,
            compute_leaves,
            domain,
            resource
            )

    @api.model
    def get_stages(self):
        read_field = ['id', 'name', 'display_name', 'color', 'sequence', 'project_ids']
        return self.env['project.task.type'].search([]).sudo().read(read_field)
            
    def _search_task_and_its_dependency(self, operator, value):
        if operator in ('like', 'ilike'):
            # search task with name like value
            tasks = self.search([['name', 'ilike', '%' + value + '%']])
            recursive_dependency_tasks = tasks.recursive_depend_ids
            recursive_dependency_tasks |= tasks
            return [('id', 'in', recursive_dependency_tasks.ids)]
        return []
    
    def _search_task_and_its_depending(self, operator, value):
        if operator in ('like', 'ilike'):
            # search task with name like value
            tasks = self.search([['name', 'ilike', '%' + value + '%']])
            recursive_depending_tasks = tasks.recursive_depending_ids
            recursive_depending_tasks |= tasks
            return [('id', 'in', recursive_depending_tasks.ids)]
        return []

    def _get_dependency_level(self):
        if not self.depend_ids:
            return 0
        # find the max level of the dependency
        max_level = 0
        for dependency in self.depend_ids:
            l = dependency._get_dependency_level()
            if l > max_level:
                max_level = l
        return max_level + 1

    def _get_recursive_dependency_map(self):
        res = {}
        if not self.ids:
            return res
        self.env.cr.execute(
            """
            WITH RECURSIVE dependencies AS (
                SELECT task_id, depend_task_id
                FROM project_task_dependency_rel
                
                UNION ALL
                
                SELECT
                    rel.task_id,
                    dep.depend_task_id
                FROM project_task_dependency_rel AS rel
                INNER JOIN dependencies AS dep ON dep.task_id = rel.depend_task_id
            )
            SELECT depend.task_id AS id, array_agg(depend.depend_task_id) AS recursive_depend_ids
            FROM dependencies AS depend
            WHERE depend.task_id IN %s
            GROUP BY depend.task_id
            """, (tuple(self.ids),)
            )
        data = self.env.cr.fetchall()
        return dict(data)
    
    def _get_recursive_depending_map(self):
        res = {}
        if not self.ids:
            return res
        self.env.cr.execute(
            """
            WITH RECURSIVE dependencies AS (
                SELECT task_id, depend_task_id
                FROM project_task_dependency_rel
                
                UNION ALL
                
                SELECT
                    rel.task_id,
                    dep.depend_task_id
                FROM project_task_dependency_rel AS rel
                INNER JOIN dependencies AS dep ON dep.task_id = rel.depend_task_id
            )
            SELECT depend.depend_task_id AS id, array_agg(depend.task_id) AS recursive_depending_ids
            FROM dependencies AS depend
            WHERE depend.depend_task_id IN %s
            GROUP BY depend.depend_task_id
            """, (tuple(self.ids),)
            )
        data = self.env.cr.fetchall()
        return dict(data)
