from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestProjectTaskDependency(TransactionCase):

    def setUp(self):
        super(TestProjectTaskDependency, self).setUp()

        self.project1 = self.env['project.project'].with_context(tracking_disable=True).create({
            'name': 'Project One',
            })
        self.project2 = self.env['project.project'].with_context(tracking_disable=True).create({
            'name': 'Project Two',
            })
        self.task1 = self.env['project.task'].with_context(tracking_disable=True).create({
            'name': '1',
            'project_id': self.project1.id
            })
        self.task2 = self.env['project.task'].with_context(tracking_disable=True).create({
            'name': '2',
            'depend_ids': [(6, 0, [self.task1.id])],
            'project_id': self.project1.id,
            })
        self.task3 = self.env['project.task'].with_context(tracking_disable=True).create({
            'name': '3',
            'depend_ids': [(6, 0, [self.task2.id])],
            'project_id': self.project1.id,
            })
        self.task4 = self.env['project.task'].with_context(tracking_disable=True).create({
            'name': '4',
            'depend_ids': [(6, 0, [self.task2.id])],
            'project_id': self.project2.id,
            })
        # compute non-stored fields for later tests
        tasks = self.task1 + self.task1 + self.task3 + self.task4
        tasks._compute_recursive_depend_ids()
        tasks._compute_recursive_depending_ids()

    def test_01_dependency_path(self):
        
        self.assertEqual(len(self.task3.depend_ids), 1)

        self.assertEqual(len(self.task1.recursive_depend_ids), 0)
        
        self.assertEqual(len(self.task3.recursive_depend_ids), 2)
        self.assertRecordValues(
            self.task3,
            [
                {
                    'recursive_depend_ids': [self.task2.id, self.task1.id]
                    }
                ]
            )

        self.assertEqual(len(self.task3.depending_task_ids), 0)
        self.assertEqual(len(self.task1.depending_task_ids), 1)
        self.assertRecordValues(
            self.task1,
            [
                {
                    'depending_task_ids': [self.task2.id]
                    }
                ]
            )

        self.assertEqual(len(self.task3.recursive_depending_ids), 0)
        self.assertEqual(len(self.task1.recursive_depending_ids), 3)
        self.assertRecordValues(
            self.task1,
            [
                {
                    'recursive_depending_ids': [self.task2.id, self.task4.id, self.task3.id]
                    }
                ]
            )

    def test_02_avoid_recursion(self):
        with self.assertRaises(ValidationError):
            self.task1.write({'depend_ids': [(6, 0, [self.task3.id])]})

    def test_03_dependency_level(self):
        self.assertEqual(self.task1.dependency_level, 0,
                         "The task 1's dependency level should be 0 as it depends on nothing")
        self.assertEqual(self.task2.dependency_level, 1,
                         "The task 2's dependency level should be 1 as it depends on the task 1")
        self.assertEqual(self.task3.dependency_level, 2,
                         "The task 3's dependency level should be 2 as it depends on the task 2 while the task 2 depends on the task 1.")
        self.assertEqual(self.task4.dependency_level, 2,
                         "The task 4's dependency level should be 2 as it depends on the task 2 while the task 2 depends on the task 1.")

    def test_04_dependency_level(self):
        self.task0 = self.env['project.task'].with_context(tracking_disable=True).create({
            'name': '0',
            'project_id': self.project1.id
            })
        self.task1.write({'depend_ids': [(4, self.task0.id)]})
        self.assertEqual(self.task1.dependency_level, 1,
                         "The task 1's dependency level should be 1 as it depends on the task 0")
        self.assertEqual(self.task2.dependency_level, 2,
                         "The task 2's dependency level should be 2 as it depends on the task 1 while the task 1 depends on the task 0")
        self.assertEqual(self.task3.dependency_level, 3,
                         "The task 3's dependency level should be 3 as it depends on the task 2 while the task 2 depends on the task 1 and the task 1 depends on the task 0.")
        self.assertEqual(self.task4.dependency_level, 3,
                         "The task 4's dependency level should be 3 as it depends on the task 2 while the task 2 depends on the task 1 and the task 1 depends on the task 0.")
