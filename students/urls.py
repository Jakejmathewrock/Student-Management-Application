from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('parent-dashboard/', views.parent_dashboard, name='parent_dashboard'),
    path('parent/child/<int:pk>/', views.parent_child_detail, name='parent_child_detail'),

    # Students
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.student_add, name='student_add'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
    path('students/export/', views.student_export, name='student_export'),

    # Departments
    path('departments/', views.department_list, name='department_list'),
    path('departments/add/', views.department_add, name='department_add'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),

    # Courses
    path('courses/', views.course_list, name='course_list'),
    path('courses/add/', views.course_add, name='course_add'),
    path('courses/<int:pk>/edit/', views.course_edit, name='course_edit'),
    path('courses/<int:pk>/delete/', views.course_delete, name='course_delete'),

    # Attendance
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/add/', views.attendance_add, name='attendance_add'),
    path('attendance/pending-fees/', views.pending_fees_list, name='pending_fees_list'),
    path('attendance/gpa-distribution/', views.gpa_distribution, name='gpa_distribution'),

    # Results
    path('results/', views.result_list, name='result_list'),
    path('results/add/', views.result_add, name='result_add'),
    path('results/<int:pk>/delete/', views.result_delete, name='result_delete'),

    # Teacher Module
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/add/', views.teacher_add, name='teacher_add'),
    path('teachers/<int:pk>/edit/', views.teacher_edit, name='teacher_edit'),
    path('teachers/<int:pk>/delete/', views.teacher_delete, name='teacher_delete'),

    # Timetable Module
    path('timetable/', views.timetable_list, name='timetable_list'),
    path('timetable/add/', views.timetable_add, name='timetable_add'),
    path('timetable/<int:pk>/edit/', views.timetable_edit, name='timetable_edit'),
    path('timetable/<int:pk>/delete/', views.timetable_delete, name='timetable_delete'),

    # Assignments
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/add/', views.assignment_add, name='assignment_add'),
    path('assignments/submit/', views.assignment_submit, name='assignment_submit'),

    # Notice Board
    path('notices/', views.notice_list, name='notice_list'),
    path('notices/add/', views.notice_add, name='notice_add'),

    # Fee Management
    path('fees/', views.fee_list, name='fee_list'),
    path('fees/add/', views.fee_add, name='fee_add'),
    path('fees/<int:pk>/pay/', views.fee_payment, name='fee_payment'),

    # Export
    path('attendance/export/', views.attendance_export, name='attendance_export'),
    path('results/export/', views.result_export, name='result_export'),
    path('students/export/excel/', views.student_export_excel, name='student_export_excel'),
    path('students/export/pdf/', views.student_export_pdf, name='student_export_pdf'),

    # ID Card
    path('students/<int:pk>/id-card/', views.student_id_card, name='student_id_card'),

    # ── EXAM MODULE ──────────────────────────────────────────────
    # Admin
    path('exams/',                              views.exam_list,                name='exam_list'),
    path('exams/create/',                       views.exam_create,              name='exam_create'),
    path('exams/<int:pk>/',                     views.exam_detail,              name='exam_detail'),
    path('exams/<int:pk>/edit/',                views.exam_edit,                name='exam_edit'),
    path('exams/<int:pk>/delete/',              views.exam_delete,              name='exam_delete'),
    path('exams/applications/<int:pk>/approve/',views.application_approve,      name='application_approve'),
    path('exams/applications/<int:pk>/reject/', views.application_reject,       name='application_reject'),

    # Student Portal
    path('exam-portal/',                        views.exam_portal,              name='exam_portal'),
    path('exam-portal/apply/<int:pk>/',         views.exam_apply,               name='exam_apply'),
    path('exam-portal/application/<int:pk>/',   views.exam_application_status,  name='exam_application_status'),
    path('exam-portal/hall-ticket/<int:pk>/',   views.hall_ticket,              name='hall_ticket'),

    # Food Court — Student
    path('food-court/',                         views.food_court,                 name='food_court'),
    path('food-court/checkout/',                views.food_checkout,            name='food_checkout'),
    path('food-court/orders/',                  views.food_my_orders,           name='food_my_orders'),
    path('food-court/order/<int:pk>/',          views.food_order_detail,        name='food_order_detail'),

    # Food Court — Admin
    path('food-court/manage/',                  views.food_menu_admin,          name='food_menu_admin'),
    path('food-court/manage/add/',              views.food_item_add,            name='food_item_add'),
    path('food-court/manage/<int:pk>/edit/',    views.food_item_edit,           name='food_item_edit'),
    path('food-court/orders-admin/',            views.food_orders_admin,        name='food_orders_admin'),

    # ── LIBRARY MODULE ───────────────────────────────────────────
    # Admin
    path('library/books/',                      views.book_list,                name='book_list'),
    path('library/books/add/',                  views.book_add,                 name='book_add'),
    path('library/books/<int:pk>/edit/',        views.book_edit,                name='book_edit'),
    path('library/books/<int:pk>/delete/',      views.book_delete,              name='book_delete'),
    path('library/issues/',                     views.issue_list,               name='issue_list'),
    path('library/issues/add/',                 views.issue_add,                name='issue_add'),
    path('library/issues/<int:pk>/return/',     views.issue_return,             name='issue_return'),
    path('library/issues/<int:pk>/settle/',     views.settle_fine,              name='settle_fine'),

    # Student Portal
    path('library-portal/',                     views.library_portal,           name='library_portal'),
    path('student-timetable/',                  views.student_timetable,        name='student_timetable'),
    path('hostel-portal/',                      views.hostel_portal,            name='hostel_portal'),

    # ── HOSTEL MODULE ────────────────────────────────────────────
    # Admin
    path('hostel/rooms/',                       views.room_list,                name='room_list'),
    path('hostel/rooms/add/',                   views.room_add,                 name='room_add'),
    path('hostel/rooms/<int:pk>/edit/',         views.room_edit,                name='room_edit'),
    path('hostel/rooms/<int:pk>/delete/',       views.room_delete,              name='room_delete'),
    path('hostel/allocations/',                 views.allocation_list,          name='allocation_list'),
    path('hostel/allocations/add/',             views.allocation_add,           name='allocation_add'),
    path('hostel/allocations/<int:pk>/checkout/',views.allocation_checkout,     name='allocation_checkout'),

    # ── NOTIFICATION CENTER ──────────────────────────────────────
    path('notifications/',                      views.notification_list,        name='notification_list'),
    path('notifications/<int:pk>/read/',        views.notification_mark_read,   name='notification_mark_read'),
    path('notifications/mark-all-read/',        views.notification_mark_all_read, name='notification_mark_all_read'),
    path('notifications/<int:pk>/delete/',      views.notification_delete,      name='notification_delete'),
    path('notifications/send/',                 views.notification_send,        name='notification_send'),
    path('fees/<int:pk>/remind/',               views.send_fee_reminder,        name='send_fee_reminder'),
    path('assignments/<int:pk>/remind/',        views.send_assignment_reminder, name='send_assignment_reminder'),

    # ── PAYMENT MANAGEMENT SYSTEM ─────────────────────────────
    path('payments/',                            views.payment_dashboard,         name='payment_dashboard'),
    path('payments/initiate/<int:fee_pk>/',      views.payment_initiate,          name='payment_initiate'),
    path('payments/upi-confirm/<int:fee_pk>/',   views.payment_upi_confirm,       name='payment_upi_confirm'),
    path('payments/razorpay-callback/',          views.payment_razorpay_callback, name='payment_razorpay_callback'),
    path('payments/success/<int:txn_pk>/',       views.payment_success,           name='payment_success'),
    path('payments/failure/<int:txn_pk>/',       views.payment_failure,           name='payment_failure'),
    path('payments/pending/<int:txn_pk>/',       views.payment_pending,           name='payment_pending'),
    path('payments/history/',                    views.payment_history,           name='payment_history'),
    path('payments/receipt/<int:txn_pk>/',       views.payment_receipt_pdf,       name='payment_receipt_pdf'),
    path('payments/admin/',                      views.payment_admin_list,        name='payment_admin_list'),
    path('payments/admin/approve/<int:txn_pk>/', views.payment_admin_approve,     name='payment_admin_approve'),

    # ── LAUNDRY MODULE ───────────────────────────────────────────
    path('laundry/',                            views.laundry_portal,           name='laundry_portal'),
    path('laundry/place-order/',                views.laundry_place_order,      name='laundry_place_order'),
    path('laundry/order/<int:pk>/',             views.laundry_order_detail,     name='laundry_order_detail'),
    path('laundry/order/<int:pk>/pdf/',         views.laundry_order_receipt_pdf,name='laundry_order_receipt_pdf'),
    path('laundry/my-orders/',                  views.laundry_my_orders,        name='laundry_my_orders'),
    path('laundry/admin/orders/',               views.laundry_admin_orders,     name='laundry_admin_orders'),
    path('laundry/admin/orders/pdf/',           views.laundry_orders_export_pdf,name='laundry_orders_export_pdf'),
    path('laundry/admin/services/',             views.laundry_services_admin,   name='laundry_services_admin'),
    path('laundry/admin/services/<int:pk>/toggle/', views.laundry_service_toggle, name='laundry_service_toggle'),

    # ── NEW REPORTS AND SEARCH EVERYWHERE ────────────────────────
    path('food-court/order/<int:pk>/pdf/',      views.food_order_invoice_pdf,   name='food_order_invoice_pdf'),
    path('food-court/orders/pdf/',              views.food_orders_export_pdf,   name='food_orders_export_pdf'),
    path('results/pdf/',                        views.result_export_pdf,        name='result_export_pdf'),
    path('attendance/pdf/',                     views.attendance_export_pdf,    name='attendance_export_pdf'),
    path('students/<int:pk>/id-card/pdf/',      views.student_id_card_pdf,      name='student_id_card_pdf'),
    path('students/<int:pk>/marksheet/pdf/',    views.student_marksheet_pdf,    name='student_marksheet_pdf'),
    path('students/<int:pk>/bonafide/pdf/',     views.student_bonafide_pdf,     name='student_bonafide_pdf'),
    path('exam-portal/hall-ticket/<int:pk>/pdf/', views.exam_hall_ticket_pdf,   name='exam_hall_ticket_pdf'),
    path('search/',                             views.search_everywhere,        name='search_everywhere'),
]
