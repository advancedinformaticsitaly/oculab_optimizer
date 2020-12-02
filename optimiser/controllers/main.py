# -*- coding: utf-8 -*-

import base64
import odoo
from odoo import http
from odoo.http import Controller, request, route
from werkzeug.utils import redirect
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.web.controllers.main import Home, ensure_db, Session
from odoo.tools.translate import _
import requests
import json

DEFAULT_IMAGE = '/optimiser/static/src/img/loading.gif'


class Loading(Controller):
	@route(['/optimiser-loading'], type = 'http', auth = 'none', website = True)
	def image_loading(self, **post):
		website = request.website
		optimiser = website and request.env['optimiser.optimiser'].sudo().search([('website_id', '=', website.id)])

		if optimiser and optimiser.loading_image:
			image = base64.b64decode(optimiser.loading_image)
		else:
			return redirect(DEFAULT_IMAGE)

		return request.make_response(
				image, [('Content-Type', 'image')])

	@route(['/optimiser-page-loader-image'], type = 'http', auth = 'none', website = True)
	def page_loading(self, **post):
		website = request.website
		optimiser = website and request.env['optimiser.optimiser'].sudo().search([('website_id', '=', website.id)])

		if optimiser and optimiser.page_loading and optimiser.page_loading_image:
			image = base64.b64decode(optimiser.page_loading_image)
		else:
			return redirect(DEFAULT_IMAGE)

		return request.make_response(
				image, [('Content-Type', 'image')])


class AuthSignupHome(AuthSignupHome):
	def get_auth_signup_qcontext(self):
		""" Shared helper returning the rendering context for signup and reset password """
		qcontext = request.params.copy()
		qcontext.update(self.get_auth_signup_config())
		if qcontext.get('token'):
			try:
				# retrieve the user info (name, login or email) corresponding to a signup token
				token_infos = request.env['res.partner'].sudo().signup_retrieve_info(qcontext.get('token'))
				for k, v in token_infos.items():
					qcontext.setdefault(k, v)
			except:
				qcontext['error'] = _("Invalid signup token")
				qcontext['invalid_token'] = True

		try:
			website = request.website
		except:
			website = False

		optimiser = website and request.env['optimiser.optimiser'].sudo().search([('website_id', '=', website.id)])

		if request.httprequest.method == 'POST':
			if optimiser.enable_recaptcha and str(request.httprequest.path).startswith('/web/signup'):
				url = "https://www.google.com/recaptcha/api/siteverify"

				response = requests.get(url,
				                        params = {
					                        'secret'  : optimiser.captcha_secret_key,
					                        'response': str(qcontext.get('g-recaptcha-response')),
					                        'remoteip': str(request.httprequest.remote_addr)
				                        }).text

				data = json.loads(response)

				if (data.get('success') == False):
					qcontext['error'] = _("ReCaptcha can’t be blank.")

		oauth_module = request.env['ir.module.module'].sudo().search([('name', '=', 'auth_oauth')])

		if oauth_module and oauth_module.state != 'uninstalled':
			qcontext["providers"] = self.list_providers()

		return qcontext


class Home(Home):
	@route()
	def web_login(self, redirect = None, **kw):
		ensure_db()
		request.params['login_success'] = False
		if request.httprequest.method == 'GET' and redirect and request.session.uid:
			return http.redirect_with_hash(redirect)

		if not request.uid:
			request.uid = odoo.SUPERUSER_ID

		values = request.params.copy()
		try:
			values['databases'] = http.db_list()
		except odoo.exceptions.AccessDenied:
			values['databases'] = None

		try:
			website = request.website
		except:
			website = False

		optimiser = website and request.env['optimiser.optimiser'].sudo().search([('website_id', '=', website.id)])

		if request.httprequest.method == 'POST':
			if optimiser.enable_recaptcha:

				url = "https://www.google.com/recaptcha/api/siteverify"

				response = requests.get(url,
				                        params = {
					                        'secret'  : optimiser.captcha_secret_key,
					                        'response': str(values.get('g-recaptcha-response')),
					                        'remoteip': str(request.httprequest.remote_addr)
				                        }).text

				data = json.loads(response)

				if (data.get('success') == False):
					values['error'] = _("ReCaptcha can’t be blank.")
					request.params['password'] = ''

					res = super(Home, self).web_login(redirect, **kw)

					res.qcontext.update({
						'error': _("ReCaptcha can’t be blank.")
					})

					return res

		return super(Home, self).web_login(redirect, **kw)
