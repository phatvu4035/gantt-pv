from datetime import datetime
from odoo.tools import relativedelta

from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged('-at_install', 'post_install')
class TestProjectTaskPlannedEndDate(TransactionCase):
    
    def setUp(self):
        super(TestProjectTaskPlannedEndDate, self).setUp()
        # create demo user
        self.u1 = self.env['res.users'].create(
            {"name": 'User Employee 1', "login": "uem1@example.com"}
        )

        self.u2 = self.env['res.users'].create(
            {"name": 'User Employee 2', "login": "uem2@example.com"}
        )

        self.u3 = self.env['res.users'].create(
            {"name": 'User Employee 3', "login": "uem3@example.com"}
        )

        # Create demo employee
        self.employee1 = self.env['hr.employee'].create(
            {
                "name": 'Employee 1', "company_id": 1, "resource_calendar_id": self.env.ref('resource.resource_calendar_std').id, "user_id": self.u1.id
            }
        )

        self.employee2 = self.env['hr.employee'].create(
            {
                "name": 'Employee 1', "company_id": 1, "resource_calendar_id": self.env.ref('resource.resource_calendar_std').id, "user_id": self.u2.id
            }
        )

        self.employee3 = self.env['hr.employee'].create(
            {
                "name": 'Employee 1', "company_id": 1, "resource_calendar_id": self.env.ref('resource.resource_calendar_std_35h').id, "user_id": self.u3.id
            }
        )

        # Create project
        self.project1 = self.env["project.project"].create(
            {"name": "Project One", }
        )

        # Create task
        self.task1 = self.env["project.task"].create(
            {"name": "Task 1", "project_id": self.project1.id, "planned_hours": 38, "resource_allocation": 100.0, "user_id": self.u1.id}
        )

    def test_change_assignee(self):
        current_planned_end_date = self.task1.planned_date_end
        # Change assignee
        self.task1.write({"user_id": self.u2.id})
        planned_end_date = self.task1.planned_date_end
        
        self.assertEqual(current_planned_end_date, planned_end_date)
        
    def test_change_date_end_and_then_change_assignee(self):
        now = datetime.now()
        # set new date end
        new_date = now + relativedelta(days=15)
        dt_string = new_date.strftime("%Y-%m-%d %H:%M:%S")
        self.task1.write({"planned_date_end": dt_string})
        current_planned_end_date = self.task1.planned_date_end
        
        # Change assignee
        self.task1.write({"user_id": self.u2.id})
        planned_end_date = self.task1.planned_date_end
        
        self.assertEqual(current_planned_end_date, planned_end_date)
    
    def test_change_planned_date_start(self):
        now = datetime.now()
        current_planned_end_date = self.task1.planned_date_end

        # set change date start
        new_date_start = now + relativedelta(days=5)
        dt_string = new_date_start.strftime("%Y-%m-%d %H:%M:%S")
        self.task1.write({"planned_date_start": dt_string})
        
        planned_end_date = self.task1.planned_date_end
        self.assertNotEqual(current_planned_end_date, planned_end_date)

    def test_change_planned_hours(self):
        current_planned_end_date = self.task1.planned_date_end
        # Change assignee with different resource calendar id
        self.task1.write({"planned_hours": 46})
        
        planned_end_date = self.task1.planned_date_end
        self.assertNotEqual(current_planned_end_date, planned_end_date)

    def test_change_resource_allocation(self):
        current_planned_end_date = self.task1.planned_date_end
        
        self.task1.write({"resource_allocation": 75.0})
        planned_end_date = self.task1.planned_date_end
        
        self.assertNotEqual(current_planned_end_date, planned_end_date)
