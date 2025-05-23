from django.shortcuts import render
from django.http import HttpResponse
import csv
import os
from django.db.models import Avg
from .models import LoanApplication
from datetime import datetime
import json
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth



from django.core.serializers.json import DjangoJSONEncoder




def data_visualization(request):
    # Total applications
    total_applications = LoanApplication.objects.count()
    
    # Average Interest Rate
    avg_interest_rate = LoanApplication.objects.aggregate(avg_ir=Avg('interest_rate'))['avg_ir']
    
    # Avg DTI
    avg_dti = LoanApplication.objects.aggregate(avg_dti=Avg('debt_to_income_ratio'))['avg_dti']

    
    # Total approved loan amount
    approved_loan_amount = LoanApplication.objects.filter(loan_approved=True).aggregate(
        total_amt=Sum('loan_amount')
    )['total_amt'] or 0
    
    # Loan approval status counts
    approval_status_counts = LoanApplication.objects.values('loan_approved').annotate(
        count=Count('loan_approved')
    )
    approval_status_data = [
        {'status': 'Approved' if item['loan_approved'] else 'Rejected', 'count': item['count']}
        for item in approval_status_counts
    ]
    
    # Loan purpose counts
    loan_purpose_counts = LoanApplication.objects.values('loan_purpose').annotate(
        count=Count('loan_purpose')
    )
    loan_purpose_data = list(loan_purpose_counts)
    
    # Applications by month
    applications_by_month = LoanApplication.objects.annotate(
        month=TruncMonth('application_date')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    applications_by_month_data = [
        {'month': item['month'].strftime('%Y-%m'), 'count': item['count']}
        for item in applications_by_month
    ]
    
    # Applications by loan duration
    applications_by_duration = LoanApplication.objects.values('loan_duration').annotate(
        count=Count('loan_duration')
    ).order_by('loan_duration')
    applications_by_duration_data = [
        {'duration': item['loan_duration'], 'count': item['count']}
        for item in applications_by_duration
    ]

    # Tổng hợp dữ liệu cho dashboard Applicants Profile

    # 1. Age Distribution (Phân nhóm tuổi)
    age_data_raw = LoanApplication.objects.values('age')
    age_groups = [
        {"age_group": "Young Adults", "count": sum(1 for a in age_data_raw if 18 <= a['age'] <= 25)},
        {"age_group": "Adults", "count": sum(1 for a in age_data_raw if 26 <= a['age'] <= 40)},
        {"age_group": "Middle Aged", "count": sum(1 for a in age_data_raw if a['age'] > 40)},
    ]
    age_data = [group for group in age_groups if group["count"] > 0]

    # 2. Employment Status Distribution
    employment_status_counts = LoanApplication.objects.values('employment_status').annotate(
        count=Count('employment_status')
    )
    employment_data = [
        {'status': item['employment_status'], 'count': item['count']}
        for item in employment_status_counts
    ]

    # 3. Marital Status Distribution
    marital_status_counts = LoanApplication.objects.values('marital_status').annotate(
        count=Count('marital_status')
    )
    marital_data = [
        {'status': item['marital_status'], 'count': item['count']}
        for item in marital_status_counts
    ]

    # 4. Education Level Distribution
    education_level_counts = LoanApplication.objects.values('education_level').annotate(
        count=Count('education_level')
    )
    education_data = [
        {'level': item['education_level'], 'count': item['count']}
        for item in education_level_counts
    ]

    # 5. Annual Income Distribution
    annual_income_data = [
        {'income': item['annual_income']}
        for item in LoanApplication.objects.values('annual_income')
    ]

    # 6. Credit Score Distribution (Phân loại)
    credit_score_data_raw = LoanApplication.objects.values('credit_score')
    credit_score_ranges = [
        {"range": "Poor", "count": sum(1 for c in credit_score_data_raw if 300 <= c['credit_score'] <= 579)},
        {"range": "Fair", "count": sum(1 for c in credit_score_data_raw if 580 <= c['credit_score'] <= 669)},
        {"range": "Good", "count": sum(1 for c in credit_score_data_raw if 670 <= c['credit_score'] <= 739)},
        {"range": "Very Good", "count": sum(1 for c in credit_score_data_raw if 740 <= c['credit_score'] <= 799)},
        {"range": "Excellent", "count": sum(1 for c in credit_score_data_raw if 800 <= c['credit_score'] <= 850)},
    ]
    credit_score_data = [range_data for range_data in credit_score_ranges if range_data["count"] > 0]

    # 7. Monthly Income vs Education Level
    income_vs_education_data = list(
        LoanApplication.objects.values('education_level')
        .annotate(avg_income=Avg('monthly_income'))
        .order_by('education_level')
    )

    # 8. Monthly Income & Monthly Debt Payment
    income_vs_debt_data = [
        {'income': item['monthly_income'], 'debt': item['monthly_debt_payments']}
        for item in LoanApplication.objects.values('monthly_income', 'monthly_debt_payments')
    ]

    # 9. Total Loan Application by Home Ownership Status
    home_ownership_counts = LoanApplication.objects.values('home_ownership_status').annotate(
        count=Count('home_ownership_status')
    )
    home_ownership_data = [
        {'status': item['home_ownership_status'], 'count': item['count']}
        for item in home_ownership_counts
    ]

    # 10. Debt-to-Income Ratio by Employment
    dti_by_employment = LoanApplication.objects.values('employment_status').annotate(
        dti=Avg('debt_to_income_ratio')
    )
    dti_by_employment_data = [
        {'employment': item['employment_status'], 'dti': item['dti'] * 100}  # Convert to percentage
        for item in dti_by_employment
    ]
    # Tổng hợp dữ liệu cho dashboard Risk & Approval Analysis

    # 1. Approval Rate by Education Level
    approval_by_education = LoanApplication.objects.values('education_level', 'loan_approved').annotate(
        count=Count('id')
    )
    approval_by_education_dict = {}
    for item in approval_by_education:
        education = item['education_level']
        status = 'Approved' if item['loan_approved'] else 'Rejected'
        if education not in approval_by_education_dict:
            approval_by_education_dict[education] = {'education': education, 'Approved': 0, 'Rejected': 0}
        approval_by_education_dict[education][status] = item['count']
    approval_by_education_data = list(approval_by_education_dict.values())

    # 2. Approval Rate by Employment Status
    approval_by_employment = LoanApplication.objects.values('employment_status', 'loan_approved').annotate(
        count=Count('id')
    )
    approval_by_employment_dict = {}
    for item in approval_by_employment:
        employment = item['employment_status']
        status = 'Approved' if item['loan_approved'] else 'Rejected'
        if employment not in approval_by_employment_dict:
            approval_by_employment_dict[employment] = {'employment': employment, 'Approved': 0, 'Rejected': 0}
        approval_by_employment_dict[employment][status] = item['count']
    approval_by_employment_data = list(approval_by_employment_dict.values())

    # 3. Approval Rate by Marital Status
    approval_by_marital = LoanApplication.objects.values('marital_status', 'loan_approved').annotate(
        count=Count('id')
    )
    approval_by_marital_dict = {}
    for item in approval_by_marital:
        marital = item['marital_status']
        status = 'Approved' if item['loan_approved'] else 'Rejected'
        if marital not in approval_by_marital_dict:
            approval_by_marital_dict[marital] = {'marital': marital, 'Approved': 0, 'Rejected': 0}
        approval_by_marital_dict[marital][status] = item['count']
    approval_by_marital_data = list(approval_by_marital_dict.values())

    # 4. Average Risk Score by Loan Status
    avg_risk_by_status = LoanApplication.objects.values('loan_approved').annotate(
        avg_risk=Avg('risk_score')
    )
    avg_risk_score_data = [
        {
            'status': 'Approved' if item['loan_approved'] else 'Rejected',
            'avg_risk': round(item['avg_risk'] or 0, 2)
        }
        for item in avg_risk_by_status
    ]


    # 5. Total Assets vs Total Liabilities
    assets_vs_liabilities_data = [
        {'assets': item['total_assets'], 'liabilities': item['total_liabilities']}
        for item in LoanApplication.objects.values('total_assets', 'total_liabilities')
    ]
    
        # Avg Assets by Loan Status
    avg_assets_by_status = LoanApplication.objects.values('loan_approved').annotate(
        avg_assets=Avg('total_assets')
    )
    avg_assets_by_status_data = [
        {
            'status': 'Approved' if item['loan_approved'] else 'Rejected',
            'avg_assets': round(item['avg_assets'] or 0, 2)
        }
        for item in avg_assets_by_status
    ]

    # Avg Liabilities by Loan Status
    avg_liabilities_by_status = LoanApplication.objects.values('loan_approved').annotate(
        avg_liabilities=Avg('total_liabilities')
    )
    avg_liabilities_by_status_data = [
        {
            'status': 'Approved' if item['loan_approved'] else 'Rejected',
            'avg_liabilities': round(item['avg_liabilities'] or 0, 2)
        }
        for item in avg_liabilities_by_status
    ]

    # 6. Loan Approved Status by Number of Dependents
    approval_by_dependents = LoanApplication.objects.values('number_of_dependents', 'loan_approved').annotate(
        count=Count('id')
    )
    approval_by_dependents_dict = {}
    for item in approval_by_dependents:
        dependents = item['number_of_dependents']
        status = 'Approved' if item['loan_approved'] else 'Rejected'
        if dependents not in approval_by_dependents_dict:
            approval_by_dependents_dict[dependents] = {'dependents': dependents, 'Approved': 0, 'Rejected': 0}
        approval_by_dependents_dict[dependents][status] = item['count']
    approval_by_dependents_data = list(approval_by_dependents_dict.values())


    # 7. Loan Approves by Loan Purpose
    loan_approves_by_purpose = LoanApplication.objects.values('loan_purpose', 'loan_approved').annotate(
        count=Count('id')
    )
    loan_approves_by_purpose_dict = {}
    for item in loan_approves_by_purpose:
        purpose = item['loan_purpose']
        status = 'Approved' if item['loan_approved'] else 'Rejected'
        if purpose not in loan_approves_by_purpose_dict:
            loan_approves_by_purpose_dict[purpose] = {'purpose': purpose, 'Approved': 0, 'Rejected': 0}
        loan_approves_by_purpose_dict[purpose][status] = item['count']
    loan_approves_by_purpose_data = list(loan_approves_by_purpose_dict.values())

    # 8. Monthly Income by Loan Approved
    monthly_income_by_approved_data = [
        {'income': item['monthly_income'], 'loan_approved': item['loan_approved']}
        for item in LoanApplication.objects.values('monthly_income', 'loan_approved')
    ]

    # 9. Loan Amount vs Loan Duration by Loan Approved
    # Loan Approved Count by Duration (for Area Chart)
    approved_count_by_duration = LoanApplication.objects.filter(loan_approved=True).values('loan_duration').annotate(
        count=Count('id')
    ).order_by('loan_duration')

    approved_count_by_duration_data = [
        {'loan_duration': item['loan_duration'], 'count': item['count']}
        for item in approved_count_by_duration
    ]
    
# Add raw applicant data for client-side filtering
    raw_applicant_data = list(LoanApplication.objects.values(
        'age',
        'employment_status',
        'marital_status',
        'education_level',
        'annual_income',
        'credit_score',
        'monthly_income',
        'monthly_debt_payments',
        'home_ownership_status',
        'debt_to_income_ratio',
        'loan_approved',
        'risk_score',  # Added
        'total_assets',  # Added for next chart
        'total_liabilities',  # Added for next chart
        'number_of_dependents',  # Added for DTI chart
        'loan_purpose',  # Added for loan purpose chart
        'loan_amount',  # Added for loan amount chart
        'loan_duration'  # Added for loan amount chart
    ))
    
    context = {
        'total_applications': total_applications,
        'avg_interest_rate': round((avg_interest_rate or 0) * 100, 2),
        'avg_dti': round((avg_dti or 0) * 100, 2),
        'approved_loan_amount': round(approved_loan_amount / 1000000, 2),
        'approval_status_data': json.dumps(approval_status_data),
        'loan_purpose_data': json.dumps(loan_purpose_data),
        'applications_by_month_data': json.dumps(applications_by_month_data),
        'applications_by_duration_data': json.dumps(applications_by_duration_data),
        
       # Dữ liệu cho dashboard Applicants Profile
        'age_data': json.dumps(age_data),
        'employment_data': json.dumps(employment_data),
        'marital_data': json.dumps(marital_data),
        'education_data': json.dumps(education_data),
        'annual_income_data': json.dumps(annual_income_data),
        'credit_score_data': json.dumps(credit_score_data),
        'income_vs_education_data': json.dumps(income_vs_education_data),
        'income_vs_debt_data': json.dumps(income_vs_debt_data),
        'home_ownership_data': json.dumps(home_ownership_data),
        'dti_by_employment_data': json.dumps(dti_by_employment_data),

       # Risk & Approval Analysis Dashboard
        'approval_by_education_data': json.dumps(approval_by_education_data),
        'approval_by_employment_data': json.dumps(approval_by_employment_data),
        'approval_by_marital_data': json.dumps(approval_by_marital_data),
        'avg_risk_score_data' : json.dumps(avg_risk_score_data),
        'assets_vs_liabilities_data': json.dumps(assets_vs_liabilities_data),
        'approval_by_dependents_data': json.dumps(approval_by_dependents_data),
        'loan_approves_by_purpose_data': json.dumps(loan_approves_by_purpose_data),
        'monthly_income_by_approved_data': json.dumps(monthly_income_by_approved_data),
        'approved_count_by_duration_data': json.dumps(approved_count_by_duration_data),
        'raw_applicant_data': json.dumps(raw_applicant_data),
        'avg_assets_by_status_data': json.dumps(avg_assets_by_status_data),
        'avg_liabilities_by_status_data': json.dumps(avg_liabilities_by_status_data),# Add raw data
    }
    
    return render(request, 'd3app/visualization.html', context)


def import_csv_data(request):
    file_path = 'Loan_Data_Processed.csv'

    if not os.path.exists(file_path):
        return HttpResponse("Không tìm thấy file CSV.")

    imported_count = 0

    with open(file_path, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')  # Use semicolon as delimiter
        for row in reader:
            try:
                # Parse date with stripping to handle potential whitespace
                LoanApplication.objects.create(
                    application_date=datetime.strptime(row['ApplicationDate'].strip(), "%Y-%m-%d").date(),
                    age=int(row['Age']),
                    annual_income=int(row['AnnualIncome']),
                    credit_score=int(row['CreditScore']),
                    employment_status=row['EmploymentStatus'],
                    education_level=row['EducationLevel'],
                    experience=int(row['Experience']),
                    loan_amount=int(row['LoanAmount']),
                    loan_duration=int(row['LoanDuration']),
                    marital_status=row['MaritalStatus'],
                    number_of_dependents=int(row['NumberOfDependents']),
                    home_ownership_status=row['HomeOwnershipStatus'],
                    monthly_debt_payments=int(row['MonthlyDebtPayments']),
                    credit_card_utilization_rate=float(row['CreditCardUtilizationRate'].replace(',', '.')),
                    number_of_open_credit_lines=int(row['NumberOfOpenCreditLines']),
                    number_of_credit_inquiries=int(row['NumberOfCreditInquiries']),
                    debt_to_income_ratio=float(row['DebtToIncomeRatio'].replace(',', '.')),
                    bankruptcy_history=int(row['BankruptcyHistory']),
                    loan_purpose=row['LoanPurpose'],
                    previous_loan_defaults=int(row['PreviousLoanDefaults']),
                    payment_history=int(row['PaymentHistory']),
                    length_of_credit_history=int(row['LengthOfCreditHistory']),
                    savings_account_balance=int(row['SavingsAccountBalance']),
                    checking_account_balance=int(row['CheckingAccountBalance']),
                    total_assets=int(row['TotalAssets']),
                    total_liabilities=int(row['TotalLiabilities']),
                    monthly_income=int(float(row['MonthlyIncome'].replace(',', '.'))),
                    utility_bills_payment_history=float(row['UtilityBillsPaymentHistory'].replace(',', '.')),
                    job_tenure=int(row['JobTenure']),
                    net_worth=int(row['NetWorth']),
                    base_interest_rate=float(row['BaseInterestRate'].replace(',', '.')),
                    interest_rate=float(row['InterestRate'].replace(',', '.')),
                    monthly_loan_payment=int(float(row['MonthlyLoanPayment'].replace(',', '.'))),
                    total_debt_to_income_ratio=float(row['TotalDebtToIncomeRatio'].replace(',', '.')),
                    loan_approved=bool(int(row['LoanApproved'])),
                    risk_score=float(row['RiskScore'].replace(',', '.')) if row['RiskScore'] else None,
                )
                imported_count += 1
            except KeyError as e:
                return HttpResponse(f"Lỗi ở dòng {imported_count + 1}: Cột không tìm thấy - {e}")
            except ValueError as e:
                return HttpResponse(f"Lỗi ở dòng {imported_count + 1}: Giá trị không hợp lệ - {e}. Dữ liệu: {row}")
            except Exception as e:
                return HttpResponse(f"Lỗi ở dòng {imported_count + 1}: {e}. Dữ liệu: {row}")

    return HttpResponse(f"✅ Đã import thành công {imported_count} bản ghi từ CSV.")