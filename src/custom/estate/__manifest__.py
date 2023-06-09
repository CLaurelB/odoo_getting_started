{
    'name': 'estate',
    'description': 'Learning module',
    'license': 'LGPL-3' ,
    'depends': [
        'base_setup',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_menus.xml',
        'views/res_users_views.xml',
        ],
    'installable': True,
    'application': True,
    'auto_install': False
    
}
