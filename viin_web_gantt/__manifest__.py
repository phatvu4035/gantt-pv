# -*- coding: utf-8 -*-
{
    'name': "Web Gantt",
    'summary': """
        Gantt Chart
        """,
    'description': """
Web Gantt chart for Odoo, based on Twproject
============================================

License: 
------------------------------------------------------
- This module is base on open source at Open Lab, Florence, Italy - https://gantt.twproject.com
- This library is released under MIT license

Support: 
------------------------------------------------------
- Model with fields: start date, end date, progress, state or stage

Note:
------------------------------------------------------
- With stage: stage must be defined color: color = fields.Char('Color')
    
Example:
------------------------------------------------------
- Stage: <viin_gantt 
        manager="manager_id" 
        members="user_id" 
        date_start="date_start"
        date_stop="date_end" 
        progress="progress" 
        stage_domain="[('project_ids', '=', project_id)]" 
        stage_by="project_id"
        depends="depend_ids"
        status="stage"
        status_readonly="0" 
        holiday="0" 
        string="Tasks" 
        default_group_by="project_id"
        filter_stage_condition="['project_id', 'IN', 'project_ids']" />
- State: <viin_gantt 
        manager="manager_id" 
        members="user_id" 
        date_start="date_start" 
        date_stop="date_end" 
        progress="progress" 
        status_readonly="0" 
        depends="depend_ids"
        holiday="0" 
        status="state"
        colors="['#ffffff', '#3BBF67', '#0099FF', '#fbb11e']"
        string="Tasks" 
        default_group_by="project_id"
        fetch_color="get_stages"/>  
      
Options: 
------------------------------------------------------
- status: state or stage
- status_readonly: 0 or 1, Can't change state or stage in gantt view, default: 0
- holiday: 0 or 1, can't assign start or end date at holiday, default: 0
- colors: list colors of state
- stage_domain & stage_by: Apply with stage as Project of Odoo 12
- depends: m2m fields, dependences of task
- index_color_field: field to calculate color of status
- get_stages: function to get all status
- field_status: field to use to update the status of task
- System will detect fields if missing attributes: status, depends, manager, members
- default_closed: [ 'done', 'cancel', 'cancelled', 'close', 'closed' ], with less view, skip records in list states
- fetch_color: function to fetch stage
- filter_stage_condition: condition to filter stage for data (left side is name of field in data, middle is operator
  right side is name of field in stage)
    """,
    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.erponline.vn",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.1.1',
    'depends': ['web'],
    'data': [
        'views/assets.xml',
    ],
    'qweb':[
        'static/src/xml/viin_web_gantt.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 299.7,
    'currency': 'EUR',
    'license': 'OPL-1',
}
