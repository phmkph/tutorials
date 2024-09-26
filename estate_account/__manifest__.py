{
    'name': 'estate_account',
    'version': '0.1',
    'summary': 'Invoicing capabilities for Real Estate module',
    'website': 'https://www.elmi.lv',
	'license':'LGPL-3',
	'category': 'Tutorials/estate_account',
    'data': [
			'views/estate_account_views.xml',
			'views/estate_account_menus.xml',
			'security/ir.model.access.csv',
			],
	'depends': [
		'base',
		'web',
		'contacts',
		'web_editor',
		'estate',
		'account',
    ],
    'installable': True,
    'application': True
}
