# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.http import request
import htmlmin
import copy
import re
from lxml.html import fromstring, Element
from lxml.etree import tostring as htmlstring


def hex2rgb(hexcode, alfa = 1):
	rgb = tuple(int(hexcode[1:][i:i + 2], 16) for i in (0, 2, 4))
	rgb = rgb + (alfa,)
	return rgb


class IrUiView(models.Model):
	_inherit = 'ir.ui.view'

	@api.model
	def render_template(self, template, values = None, engine = 'ir.qweb'):
		res = super(IrUiView, self).render_template(template, values, engine)
		res_copy = res

		try:
			website = request.website
		except:
			website = False

		optimiser = website and self.env['optimiser.optimiser'].sudo().search([('website_id', '=', website.id)])

		try:
			res = res.decode("utf-8", "ignore").encode("ascii", "xmlcharrefreplace")
		except:
			pass

		if values and values.get('request', False) and optimiser:
			res = fromstring(res)
			head = res.find('.//head')
			body = res.find('.//body')
			no_head_body = False

			if not body or not head:
				no_head_body = True

			if not no_head_body:
				if not request.httprequest.is_xhr:

					if optimiser.load_css_async or optimiser.css_bottom:
						styles = res.cssselect('link[rel="stylesheet"]')
						ie_styles = ""

						for style in styles:
							ie_styles += htmlstring(style, method = "html").decode("utf-8").strip().strip("\n").rstrip(
								'>') + "/>"

							if optimiser.css_bottom:
								body.insert(len(body), style)

							if optimiser.load_css_async:
								noscript_tag = Element('noscript')
								tmp_style = copy.copy(style)
								noscript_tag.insert(0, tmp_style)

								parent = style.getparent()
								parent.insert(parent.index(style) + 1, noscript_tag)

								style.attrib['rel'] = 'preload'
								style.attrib['as'] = 'style'
								style.attrib['onload'] = "this.onload=null;this.rel='stylesheet'"

						script_tag_for_converting_styles = Element("script")
						script_tag_for_converting_styles.attrib['data-not-touchable'] = 'true'
						script_tag_for_converting_styles.text = "function supportsToken(token){return function(relList){if(relList && relList.supports && token){return relList.supports(token)} return false}}; window.onload = function(){if(!supportsToken('preload')(document.createElement('link').relList)){var links=document.querySelectorAll('link[as=\"style\"][rel=\"preload\"]'); if(links.length){for(var i in links){links[i].rel='stylesheet'}}}}"
						body.insert(len(body), script_tag_for_converting_styles)

						script_tag_for_checking_ie = Element('script')
						script_tag_for_checking_ie.attrib['data-not-touchable'] = 'true'
						script_tag_for_checking_ie.text = "function isIE(){var myNav=navigator.userAgent.toLowerCase(); return (myNav.indexOf('msie') != -1 || myNav.indexOf('trident') != -1) ? true : false;}; if(isIE()){var div=document.createElement('div');div.innerHTML='%s';document.head.appendChild(div);}" % ie_styles
						head.insert(len(head), script_tag_for_checking_ie)

					if optimiser.js_bottom:
						scripts = res.cssselect('script:not([data-not-touchable])')

						for script in scripts:
							body.insert(len(body), script)

					if optimiser.load_js_async:
						scripts = res.cssselect('script[src]')

						for script in scripts:
							script.attrib['defer'] = 'defer'

					if optimiser.page_loading:
						page_loader_script_tag = Element("script")
						page_loader_script_tag.text = "window.addEventListener('" + optimiser.show_page_loading_until + \
						                              "', function(){document.querySelector('div.optimiser-page-loader').remove();});"
						page_loader_image_width = optimiser.page_loading_image_width if optimiser.page_loading_image_width else "100px"
						page_loader_image_height = optimiser.page_loading_image_height if optimiser.page_loading_image_height else "100px"
						page_loader_image_position_top = optimiser.page_loading_image_pos_top if optimiser.page_loading_image_pos_top else "50%"
						page_loader_image_position_left = optimiser.page_loading_image_pos_left if optimiser.page_loading_image_pos_left else "50%"
						page_loader_bg = optimiser.page_loading_bg_color if optimiser.page_loading_bg_color else "#FFFFFF"
						page_loader_bg_transparency = optimiser.page_loading_bg_transparency if optimiser.page_loading_bg_transparency else 1
						page_loader_bg_image = (optimiser.show_default_page_loading_image or optimiser.page_loading_image) \
						                       and "background-image: url(/optimiser-page-loader-image);" or ""

						page_loader_div = Element("div", **{
							'class': "optimiser-page-loader",
							'style': "position: fixed;"
							         "left: 0;"
							         "top: 0;"
							         "width: 100%%;"
							         "height: 100%%;"
							         "z-index: 9999999999;"
							         "%s"
							         "background-repeat: no-repeat;"
							         "background-size: %s %s;"
							         "background-color: rgba%s;"
							         "background-position: %s %s;"
							         "background-attachment: fixed;" % (str(page_loader_bg_image),
							                                            str(page_loader_image_width),
							                                            str(page_loader_image_height),
							                                            str(hex2rgb(page_loader_bg,
							                                                        page_loader_bg_transparency)),
							                                            str(page_loader_image_position_top),
							                                            str(page_loader_image_position_left))
						})

						body.insert(len(body), page_loader_script_tag)
						body.insert(0, page_loader_div)

					if len(optimiser.custom_content_ids) > 0:

						contents = optimiser.custom_content_ids

						for content in contents:
							if content.content:
								try:
									tmp = fromstring(content.content)
								except:
									continue

								if content.position.startswith('head'):
									html = head
								else:
									html = body

								position = len(html) if content.position.endswith("end") else 0
								head_content = tmp.find('.//head')

								if head_content:
									for tmp_content in head_content:
										html.insert(position, tmp_content)
										position += 1
								else:
									html.insert(position, tmp)

				if optimiser.enable_lazy_load_front:
					images = res.cssselect('img:not(.og_not_lazy)')
					bg_images = res.cssselect('[style*="background-image"]:not(.optimiser-page-loader):not(.og_not_lazy)')
					loading_image = ((optimiser.show_default_image_loading_image or optimiser.loading_image)
					                 and "/optimiser-loading") \
					                or "/optimiser/static/src/img/empty.png"
					check_class_regex = re.compile(r"^.*\s*optimiser_lazy(\s+|$)")

					if not request.httprequest.is_xhr:
						lazy_loader_style = Element('style')
						lazy_loader_style.text = 'img[src="/optimiser-loading"]{width:40px!important;height:40px!important;text-align:center;margin:auto;-o-object-fit:contain!important;object-fit:contain!important}'
						head.insert(len(head), lazy_loader_style)

					for bg_img in bg_images:
						bg_style = bg_img.attrib['style']
						find_bg_image = "background-image:"

						try:
							bg_image_index = bg_style.index(find_bg_image)
						except:
							continue

						index_of_bg_image_start = bg_image_index + len(find_bg_image)

						try:
							bg_style.index('url', index_of_bg_image_start)
						except:
							continue

						try:
							index_of_bg_image_end = bg_style.index(';', index_of_bg_image_start)
						except:
							try:
								bg_style += ';'
								index_of_bg_image_end = bg_style.index(';', index_of_bg_image_start)
							except:
								continue

						important_exists = ''

						try:
							important_exists = bg_style[index_of_bg_image_start:index_of_bg_image_end].index('!important')
						except:
							pass

						start_of_string = bg_style[:bg_style.index(find_bg_image)]
						end_of_string = bg_style[index_of_bg_image_end + 1:]

						if important_exists != '':
							url_with_important_exist = bg_style[
							                           index_of_bg_image_start:index_of_bg_image_end].strip().rstrip(
									'!important').strip()
							important_exists = '!important'
							main_image_url = url_with_important_exist.strip().lstrip('url(').rstrip(')').strip("'").strip(
								'"')
						else:
							main_image_url = bg_style[
							                 bg_style.index('url', index_of_bg_image_start) + 3:index_of_bg_image_end] \
								.strip().lstrip('(').rstrip(')').strip("'").strip('"')

						bg_img.attrib['data-src'] = main_image_url if not 'data-src' in bg_img.attrib else bg_img.attrib[
							'data-src']
						bg_img.attrib['class'] = bg_img.attrib.get('class', '') if check_class_regex.match(
								bg_img.attrib.get('class', '')) else bg_img.attrib.get('class', '') + ' optimiser_lazy'
						bg_img.attrib['style'] = "background-image: url('" + \
						                         loading_image + "')" + important_exists + ";" + \
						                         start_of_string + \
						                         end_of_string

					for img in images:
						img.attrib['data-src'] = img.attrib['src'] if not 'data-src' in img.attrib else img.attrib[
							'data-src']
						img.attrib['src'] = loading_image
						img.attrib['class'] = img.attrib.get('class', '') if check_class_regex.match(
								img.attrib.get('class', '')) else img.attrib.get('class', '') + ' optimiser_lazy'

				if optimiser.enable_recaptcha:
					if optimiser.captcha_selectors:
						selectors = res.cssselect(','.join(optimiser.captcha_selectors.mapped('name')))

						if selectors:
							captcha_element_parent = Element('div')
							captcha_element_parent.attrib['class'] = 'form-group field-recaptcha'

							captcha_element = Element('div')
							captcha_element.attrib['class'] = 'g-recaptcha'
							captcha_element.attrib['data-sitekey'] = optimiser.captcha_site_key

							captcha_element_parent.insert(0, captcha_element)

							for element in selectors:
								insert_element = None

								for i in reversed(element.getchildren()):
									if i.tag == 'div':
										insert_element = i
										break

								element.insert(element.index(insert_element), captcha_element_parent)

							if not request.httprequest.is_xhr:
								script_tag_for_recaptcha = Element("script")
								script_tag_for_recaptcha.attrib['src'] = 'https://www.google.com/recaptcha/api.js'
								script_tag_for_recaptcha.attrib['async'] = 'async'
								script_tag_for_recaptcha.attrib['defer'] = 'defer'
								body.insert(len(body), script_tag_for_recaptcha)

				doctype = None if '/slides/embed' in request.httprequest.url else '<!DOCTYPE html>'

				res = htmlstring(res, method = "html", doctype = doctype)
			else:
				res = res_copy

			if optimiser.compress_html:
				res = htmlmin.minify(res.decode("utf-8"),
				                     remove_empty_space = True, remove_comments = True)

			try:
				res = res.decode("utf-8")
			except:
				pass

		return res

	@api.multi
	def save(self, value, xpath = None):
		value = re.sub(r"optimiser_lazy_loaded", "", value, 0)
		value = re.sub(r"data-was-processed=[\"'][^\"']+[\"']", "", value, 0)
		super(IrUiView, self).save(value, xpath)

	@api.multi
	def write(self, vals):
		arch = vals.get('arch', False)

		if arch:
			arch = re.sub(r"optimiser_lazy_loaded", "", arch, 0)
			arch = re.sub(r"data-was-processed=[\"'][^\"']+[\"']", "", arch, 0)
			vals['arch'] = arch

		super(IrUiView, self).write(vals)
