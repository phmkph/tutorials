
{
    'name': 'Estate',
    'version': '0.1',
    'summary': 'Managing real estate objects',
    'website': 'https://www.elmi.lv',
	'license':'LGPL-3',
	'category': 'Tutorials/estate',
    'data': [
		'views/estate_property_views.xml',
		'views/estate_menus.xml',
		'views/res_users_views.xml',
		'security/ir.model.access.csv',
		'report/estate_property_reports.xml',
		'report/estate_property_sub_template.xml',
		'report/estate_property_templates.xml'
		],
	'depends': [
        'base',
        'mail',
        'calendar',
        'web',
        'contacts',
		'web_editor',
    ],
    'installable': True,
    'application': True
}
