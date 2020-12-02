# -*- coding: utf-8 -*-
{
	'name'                 : "Optimiser / Compressor / Lazy Load / Google Speed / Google reCaptcha",
	'summary'              : """
		Speed up your website.
	""",
	'description'          : """
		This module allows you to
			1. Speed up your website
			2. Add Lazy Loading for images and pages
			3. Compress html
			4. Asynchronous load javascript and/or css files
			5. Restrict access for users who can use this module
		
		This module can be used on multi domain websites too.
		
		 To Install The external Dependencies, run these commands in terminal
		 
	            pip3 install cssselect\n
	            pip3 install htmlmin
            
	""",
	'author'               : "OdooGuys Pvt. Ltd.",
	'website'              : "http://odooguys.com/",
	'category'             : 'optimise',
	'version'              : '12.0.3.2.9',
	'license'              : 'OPL-1',
	'depends'              : ['base', 'web', 'website', 'auth_signup'],
	"qweb"                 : [
		'static/src/xml/colorpicker.xml',
	],
	'data'                 : [
		'data/defaults.xml',
		'data/rules.xml',
		'views/assets.xml',
		'views/widget_colorpicker_view.xml',
		'views/view.xml',
		'views/menu.xml',
		'views/payment.xml',
	],
	'images'               : ['static/description/banner.jpg'],
	'installable'          : True,
	'auto_install'         : False,
	'application'          : True,
	"external_dependencies": {
		"python": [
			"htmlmin",
			"cssselect",
			"lxml"
		],
		'bin'   : [],
	},
	"web_preload"          : True,
	"support"              : "support@odooguys.com",
	"price"                : 125,
	"currency"             : "EUR",
}
