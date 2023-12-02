from odoo import models,fields,api
#from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
#from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
class Saleorder (models.Model):
	
	_inherit="sale.order"

	discount_on_order = fields.Char('Discount')

	quotation_date = fields.Datetime(string="Quotation Date",readonly='True', default=fields.Datetime.now, copy=False)

	@api.model
	def get_contacts(self):
		val3 = []
		sp=""
		if self.contact:
			x=0
			for el in self.contact:
				x+=1
				val3.append(el.name)
				val3.append(" ")
				val3.append(el.phone)
				if x < (len(self.contact)):
					val3.append(" / ")
		for i in val3:
			sp=sp+str(i)
		return sp
