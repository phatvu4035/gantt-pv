# -*- coding: utf-8 -*-
{
    'name': "Project Scheduling",
    'name_vi_VN': "Lập kế hoạch dự án",
    'summary': """Schedule project tasks with Gantt chart""",
    'summary_vi_VN': """Ấn định lịch thực hiện cho từng nhiệm vụ dự án""",
    'description': """
Integrate Project app with Gannt view to allow users to schedule project tasks using gantt chart

Key Features
============

1. Schedule tasks and assign resources using the gantt chart
2. Automatic planned end date calculation based on the planned start date and planned hours that also respect resource's working schedule
3. Integrate Critical Path Method to identify the longest stretch of dependent tasks and measuring the time required to complete them from start to finish

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

""",
    'description_vi_VN': """
Tích hợp ứng dụng Dự án với giao diện Gantt cho phép người dùng ấn định và lập kế hoạch cho các nhiệm vụ dự án

Tính năng chính
===============

1. Lập kế hoạch và phân phối nguồn lực sử dụng sơ đồ gantt
2. Tự động tính toán ngày kết thúc dự kiến dựa trên số giờ dự kiến và ngày khởi động dự kiến và lịch làm việc của nguồn lực
3. Tích hợp Phương pháp Đường găng để xác định các nhiệm vụ phụ thuộc xuyên suốt dự án và thời gian cần thiết để hoàn thành chúng

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",
    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.erponline.vn",
    'support': "apps.support@viindoo.com",

    'category': 'Operations/Project',
    'version': '0.1.3',
    'depends': ['project', 'hr_timesheet', 'viin_web_gantt', 'to_project_stages'],
    'data': [
        'views/project_task_view.xml',
        'data/project_data.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'application': False,
    'auto_install': ['project'],
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
