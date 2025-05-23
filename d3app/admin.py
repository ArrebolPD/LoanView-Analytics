from django.contrib import admin

# Refrom django.contrib import admin
from .models import LoanApplication
@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'application_date', 'age', 'annual_income', 'credit_score',
        'employment_status', 'education_level', 'loan_amount', 'loan_duration',
        'loan_approved', 'risk_score'
    )
    list_filter = (
        'employment_status', 'education_level', 'marital_status',
        'loan_approved',
    )
    search_fields = (
        'application_date', 'employment_status', 'education_level', 'loan_purpose'
    )
    ordering = ('-application_date',)

