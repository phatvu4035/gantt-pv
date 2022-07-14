from datetime import timedelta
from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase
from odoo.tests import tagged
from datetime import datetime


@tagged('-at_install', 'post_install')
class TestBadResourceAllocationTasks(SavepointCase):
    @classmethod
    def setUpClass(self):
        super(TestBadResourceAllocationTasks, self).setUpClass()
        
        self.task_user_1 = self.env['res.users'].with_context(no_reset_password=True, tracking_disable=True).create({
            'name': 'Task User 1',
            'login': 'task_user1@example.com',
            'groups_id': [(6, 0, [self.env.ref('project.group_project_manager').id])]
        })
        
        self.task_user_2 = self.env['res.users'].with_context(no_reset_password=True, tracking_disable=True).create({
            'name': 'Task User 2',
            'login': 'task_user2@example.com',
            'groups_id': [(6, 0, [self.env.ref('project.group_project_manager').id])]
        })

        self.project1 = self.env["project.project"].with_context(tracking_disable=True).create(
            {"name": "Project One"}
        )
        self.project2 = self.env["project.project"].with_context(tracking_disable=True).create(
            {"name": "Project Two"}
        )
        self.task1 = self.env["project.task"].with_context(tracking_disable=True).create(
            {
                "name": "Task 1", 
                "project_id": self.project1.id,
                "planned_date_start": fields.Datetime.now() + timedelta(days=-2),
                "planned_date_end": (fields.Datetime.now() + timedelta(days=5)),
                "user_id": self.task_user_1.id
            }
        )
        self.task2 = self.env["project.task"].with_context(tracking_disable=True).create(
            {
                "name": "Task 2",
                "project_id": self.project1.id,
                "planned_date_start": fields.Datetime.now() + timedelta(days=-1),
                "planned_date_end": fields.Datetime.now() + timedelta(days=4),
                "user_id": self.task_user_1.id
            }
        )
        self.task3 = self.env["project.task"].with_context(tracking_disable=True).create(
            {
                "name": "Task 3",
                "project_id": self.project1.id,
                "planned_date_start": fields.Datetime.now(),
                "planned_date_end": fields.Datetime.now() + timedelta(days=3),
                "user_id": self.task_user_1.id
            }
        )
        self.task4 = self.env["project.task"].with_context(tracking_disable=True).create(
            {
                "name": "Task 4",
                "project_id": self.project1.id,
                "planned_date_start": fields.Datetime.now() + timedelta(days=1),
                "planned_date_end": fields.Datetime.now() + timedelta(days=3),
                "user_id": self.task_user_1.id
            }
        )
        
        self.task5 = self.env["project.task"].with_context(tracking_disable=True).create(
            {
                "name": "Task 5",
                "project_id": self.project1.id,
                "planned_date_start": fields.Datetime.now() + timedelta(days=1),
                "planned_date_end": fields.Datetime.now() + timedelta(days=3),
                "user_id": self.task_user_2.id
            }
        )
    def test_01_total_resource_allowcation_is_100(self):
        """
        when there are more than one task doing at the same time
        """
        self.task1.with_context(tracking_disable=True).write({
            'resource_allocation': 25.0, 
            'planned_hours': 36,
            "planned_date_start": datetime(2015, 1, 3, 8, 59, 59),
            "planned_date_end": datetime(2015, 1, 9, 8, 59, 59),
            })
        self.task2.with_context(tracking_disable=True).write({
            'resource_allocation': 25.0, 
            'planned_hours': 36,
            "planned_date_start": datetime(2015, 1, 2, 8, 59, 59),
            "planned_date_end": datetime(2015, 1, 8, 8, 59, 59),
            })
        self.task3.with_context(tracking_disable=True).write({
            'resource_allocation': 25.0, 
            'planned_hours': 36,
            "planned_date_start": datetime(2015, 1, 7, 8, 59, 59),
            "planned_date_end": datetime(2015, 1, 8, 8, 59, 59),
            })
        self.task4.with_context(tracking_disable=True).write({
            'resource_allocation': 25.0, 
            'planned_hours': 36,
            "planned_date_start": datetime(2015, 1, 6, 8, 59, 59),
            "planned_date_end": datetime(2015, 1, 11, 8, 59, 59),
            })
        self.task5.with_context(tracking_disable=True).write({
            'resource_allocation': 25.0, 
            'planned_hours': 36,
            "planned_date_start": datetime(2015, 1, 12, 8, 59, 59),
            "planned_date_end": datetime(2015, 1, 13, 8, 59, 59),
            })
        
        self.assertEqual(self.task1.bad_resource_allocation_task_count, 3)
    
    def test_02_total_resource_allowcation_greater_100(self):
        """
        when effort for some task of user is really time consumption at the mean time of doing 'Task 1'
        """
        self.task1.with_context(tracking_disable=True).write({
            'resource_allocation': 25.0,
            'planned_hours': 36,
            "planned_date_start": datetime(2015, 1, 4, 8, 59, 59),
            "planned_date_end": datetime(2015, 1, 11, 8, 59, 59),
        })
        self.task2.with_context(tracking_disable=True).write({
            'planned_hours': 36,
            "planned_date_start": datetime(2015, 1, 4, 8, 59, 59),
            "planned_date_end": datetime(2015, 1, 5, 8, 59, 59),
        })
        self.task3.with_context(tracking_disable=True).write({
            'planned_hours': 36,
            "planned_date_start": datetime(2015, 1, 7, 8, 59, 59),
            "planned_date_end": datetime(2015, 1, 8, 8, 59, 59),
        })
        self.task4.with_context(tracking_disable=True).write({
            'planned_hours': 36,
            "planned_date_start": datetime(2015, 1, 9, 8, 59, 59),
            "planned_date_end": datetime(2015, 1, 11, 8, 59, 59),
        })
        self.task5.with_context(tracking_disable=True).write({
            'planned_hours': 36,
            "planned_date_start": datetime(2015, 1, 12, 8, 59, 59),
            "planned_date_end": datetime(2015, 1, 13, 8, 59, 59),
        })
        self.task5.flush()

        self.task5._compute_bad_resource_allocation_task_ids()
        self.assertEqual(self.task5.bad_resource_allocation_task_count, 0)
