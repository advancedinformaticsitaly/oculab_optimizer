# -*- coding: utf-8 -*-

from odoo import api, fields, models

class Selectors(models.Model):
	_name = 'optimiser.selectors'
	_description = 'Optimiser Form Selectors'

	name = fields.Char(string = 'Selector')


class Optimiser(models.Model):
	_name = 'optimiser.optimiser'
	_description = 'Optimiser'

	website_id = fields.Many2one(comodel_name = "website", string = "Website", help = "Website id field.",
	                             domain = lambda self: [('id', 'not in', self.get_added_websites())], required = True)
	enable_lazy_load_front = fields.Boolean(string = 'Lazy Load', help = 'Enable lazy load in frontend.',
	                                        default = False)
	loading_image = fields.Binary(string = 'Loading Image',
	                              help = 'Loading Image will be shown until the real image will be loaded.')
	compress_html = fields.Boolean(string = 'Compress Html', help = 'Compress HTML of frontend.',
	                               default = False)
	js_bottom = fields.Boolean(string = 'JS Scripts Bottom', help = 'Load javascript files in the bottom of the page.',
	                           default = False)
	css_bottom = fields.Boolean(string = 'CSS Bottom',
	                            help = 'Load css files in the bottom of the page.',
	                            default = False)
	page_loading = fields.Boolean(string = 'Page Loading',
	                              help = 'If you enable this the loading will be added for all pages.The loading will be displayed until the page is ready.',
	                              default = False)
	page_loading_bg_color = fields.Char(string = 'Background Color',
	                                    help = 'Background color of page loading.',
	                                    default = "#FFFFFF")
	page_loading_bg_transparency = fields.Float(string = 'Background Transparency',
	                                            help = 'Transparency of page loading background.Values can be from 0 to 1.',
	                                            default = 1, digits = (1, 1))
	page_loading_image = fields.Binary(string = 'Image',
	                                   help = 'Page Loading Image.')
	page_loading_image_width = fields.Char(string = 'Image Width', help = 'Width of page loading image.',
	                                       default = '100px')
	page_loading_image_height = fields.Char(string = 'Image Height', help = 'Height of page loading image.',
	                                        default = '100px')
	page_loading_image_pos_top = fields.Char(string = 'Image Position Top',
	                                         help = 'Position of page loading image from top.(Values can be in px/%/string.Ex.` 10px or 10% or top or bottom or center)',
	                                         default = '50%')
	page_loading_image_pos_left = fields.Char(string = 'Image Position Left',
	                                          help = 'Position of page loading image from top.(Values can be in px/%/string.Ex.` 10px or 10% or left or right or center)',
	                                          default = '50%')
	show_page_loading_until = fields.Selection(
			[('DOMContentLoaded', 'Html Content is loaded'), ('load', 'Resources are loaded')],
			string = 'Show Loading Until',
			help = 'Select page loading show/hide condition.',
			default = 'DOMContentLoaded')
	show_default_image_loading_image = fields.Boolean(string = 'Show Default image',
	                                                  help = 'Show default loading image if lazy load option was enabled.',
	                                                  default = True)
	show_default_page_loading_image = fields.Boolean(string = 'Show Default image',
	                                                 help = 'Show default page loading image if page loading option was enabled.',
	                                                 default = True)
	load_js_async = fields.Boolean(string = "Load JS Async", help = "Load js scripts asynchronous.", default = False)
	load_css_async = fields.Boolean(string = "Load CSS Async", help = "Load styles asynchronous using javascript.",
	                                default = False)
	custom_content_ids = fields.One2many('optimiser.custom.content', 'optimiser_id', 'Contents')

	enable_recaptcha = fields.Boolean(string = 'Enable ReCaptcha')
	captcha_site_key = fields.Char(string = 'Site Key', help = 'You can find this in google recaptcha site.')
	captcha_secret_key = fields.Char(string = 'Secret Key', help = 'You can find this in google recaptcha site.')
	captcha_selectors = fields.Many2many(comodel_name = "optimiser.selectors", string = 'Captcha Selectors',
	                                     help = 'You can select the css-selector of your form, which will contain recaptcha.')

	def _validate_page_loading_bg_transparency(self):
		if self.page_loading_bg_transparency < 0 or self.page_loading_bg_transparency > 1:
			return False
		return True

	_constraints = [(_validate_page_loading_bg_transparency,
	                 "Background Transparency field`s value should be from 0 to 1.", ['page_loading_bg_transparency'])]

	@api.multi
	def get_added_websites(self):
		return [int(optimise.website_id) for optimise in self.search([])]

	@api.onchange('website_id')
	def _onchange_website_id(self):
		return {
			"domain": {
				"website_id": [('id', 'not in', self.get_added_websites())]
				}
			}

	@api.onchange('loading_image')
	def _onchange_image_loading_image(self):
		if self.loading_image:
			self.show_default_image_loading_image = False

	@api.onchange('page_loading_image')
	def _onchange_page_loading_image(self):
		if self.page_loading_image:
			self.show_default_page_loading_image = False


class OptimiserCustomContent(models.Model):
	_name = 'optimiser.custom.content'
	_description = 'Optimiser Custom Content'

	optimiser_id = fields.Many2one('optimiser.optimiser', 'Optimiser', ondelete='cascade', required=True)
	position = fields.Selection([
        ('head_begin', 'Beginning of Head'),
        ('head_end', 'End of Head'),
        ('body_begin', 'Beginning of Body'),
        ('body_end', 'End of Body'),
    ], string='Position', default = "body_end", help = "The position where the content will be added.")
	content = fields.Text(string = "Content", help = "The content that will be added at the position you set.")