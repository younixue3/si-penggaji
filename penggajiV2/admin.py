from django.contrib import admin
from .models import PayrollTemplate, PayrollVariable, PayrollCalculationStep, PayrollAssignment, PayrollCalculationResult

admin.site.register(PayrollTemplate)
admin.site.register(PayrollVariable)
admin.site.register(PayrollCalculationStep)
admin.site.register(PayrollAssignment)
admin.site.register(PayrollCalculationResult)
