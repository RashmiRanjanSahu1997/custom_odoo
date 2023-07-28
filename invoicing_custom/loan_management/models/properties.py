# -*- coding: utf-8 -*-
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _


class PropertiesProduct(models.Model):
    _name = 'loan.product'
    _description = 'In loan mangement the properties of product'
    _rec_name = 'product'

    image = fields.Binary(string="Image")
    product = fields.Char(string="Product", required=False, )
    price = fields.Float(string="Price", required=False, )
    princie_id = fields.Many2one(comodel_name="account.loan.line", string="Loan Princical ", required=False, )

    # princee = fields.Float(string="Principal", required=False, related="princie_id.principal_amount",
    #                       readonly=True, limit=1)


class PropertiesPrincipal(models.Model):
    _name = 'loan.principal'
    _description = 'In loan mangement the product  of principal'



