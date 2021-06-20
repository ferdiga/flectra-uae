# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, models, _
from flectra.exceptions import UserError


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    def action_bom_cost(self):
        templates = self.filtered(lambda t: t.product_variant_count == 1 and t.bom_count > 0)
        if templates:
            return templates.mapped('product_variant_id').action_bom_cost()

    def button_bom_cost(self):
        templates = self.filtered(lambda t: t.product_variant_count == 1 and t.bom_count > 0)
        if templates:
            return templates.mapped('product_variant_id').button_bom_cost()


class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = 'product.product'
    _description = 'Product'

    def button_bom_cost(self):
        self.ensure_one()
        self._set_price_from_bom()

    def action_bom_cost(self):
        boms_to_recompute = self.env['mrp.bom'].search(['|', ('product_id', 'in', self.ids), '&', ('product_id', '=', False), ('product_tmpl_id', 'in', self.mapped('product_tmpl_id').ids)])
        for product in self:
            product._set_price_from_bom(boms_to_recompute)

    def _set_price_from_bom(self, boms_to_recompute=False):
        self.ensure_one()
        bom = self.env['mrp.bom']._bom_find(product=self)
        if bom:
            self.standard_price = self._compute_bom_price(bom, boms_to_recompute=boms_to_recompute)

    def _compute_average_price(self, qty_invoiced, qty_to_invoice, stock_moves):
        self.ensure_one()
        if stock_moves.product_id == self:
            return super()._compute_average_price(qty_invoiced, qty_to_invoice, stock_moves)
        bom = self.env['mrp.bom']._bom_find(product=self, company_id=stock_moves.company_id.id, bom_type='phantom')
        if not bom:
            return super()._compute_average_price(qty_invoiced, qty_to_invoice, stock_moves)
        dummy, bom_lines = bom.explode(self, 1)
        bom_lines = {line: data for line, data in bom_lines}
        value = 0
        for move in stock_moves:
            bom_line = move.bom_line_id
            bom_line_data = bom_lines[bom_line]
            bom_line_qty = bom_line_data['qty']
            value += bom_line_qty * move.product_id._compute_average_price(qty_invoiced * bom_line_qty, qty_to_invoice * bom_line_qty, move)
        return value

    def _compute_bom_price(self, bom, boms_to_recompute=False):
        self.ensure_one()
        if not bom:
            return 0
        if not boms_to_recompute:
            boms_to_recompute = []
        total = 0
        for opt in bom.operation_ids:
            duration_expected = (
                opt.workcenter_id.time_start +
                opt.workcenter_id.time_stop +
                opt.time_cycle)
            total += (duration_expected / 60) * opt.workcenter_id.costs_hour
        for line in bom.bom_line_ids:
            if line._skip_bom_line(self):
                continue

            # Compute recursive if line has `child_line_ids`
            if line.child_bom_id and line.child_bom_id in boms_to_recompute:
                child_total = line.product_id._compute_bom_price(line.child_bom_id, boms_to_recompute=boms_to_recompute)
                total += line.product_id.uom_id._compute_price(child_total, line.product_uom_id) * line.product_qty
            else:
                total += line.product_id.uom_id._compute_price(line.product_id.standard_price, line.product_uom_id) * line.product_qty
        return bom.product_uom_id._compute_price(total / bom.product_qty, self.uom_id)
