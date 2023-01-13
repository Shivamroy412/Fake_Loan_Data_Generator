from faker import Faker
import pandas as pd
import math
import datetime
from datetime import timedelta

fake = Faker('en_IN')


class Loan:
    def __init__(self):
        self.loan_acc_num = fake.random_int(min=10000000, max=99999999)
        self.customer_name = fake.name()
        self.customer_address = fake.address()
        self.loan_type = fake.random_element(["Personal","Car","Two-Wheeler","Consumer-Durable"])

        loan_type_range_dict = {"Personal": (5000, 5_00_000),
                                "Car": (2_00_000, 20_00_000),
                                "Two-Wheeler": (20_000, 3_00_000),
                                "Consumer-Durable": (2_000, 25_000)}


        self.loan_amount = fake.random_int(*loan_type_range_dict[self.loan_type])

        self.collateral_value = fake.random.uniform(0.0, 100.0) * self.loan_amount
        self.collateral_value = round(self.collateral_value, 2)

        self.tenure_years = fake.random_int(min=1, max=5)

        self.interest = round(fake.random.uniform(8.0,15.0), 1)

        self.disbursal_date = fake.date_between(start_date=datetime.date(2012,1,1), 
                                                end_date=datetime.date(2022,1,1))


        #A borrower defaults if he/she misses the repayment for 90 days
        self.default_date = fake.date_between(start_date=self.disbursal_date + timedelta(days=90), 
                                              end_date=self.disbursal_date + timedelta(days=self.tenure_years*12*30) - timedelta(days=90))

    @property
    def monthly_emi(self):
        monthly_interest = self.interest / 12 / 100
        num_payments = self.tenure_years * 12
        emi = (self.loan_amount * monthly_interest * math.pow((1 + monthly_interest), num_payments)) / \
                        (math.pow((1 + monthly_interest), num_payments) - 1)
        return round(emi,2)

loans = []

for _ in range(100):
    loan = Loan()
    loans.append(loan)

df = pd.DataFrame(columns=['loan_acc_num','customer_name','customer_address','loan_type','loan_amount','collateral_value','tenure_years','interest','monthly_emi','disbursal_date','default_date'])
for loan in loans:
    df = df.append({'loan_acc_num':loan.loan_acc_num,'customer_name':loan.customer_name,'customer_address':loan.customer_address,'loan_type':loan.loan_type,'loan_amount':loan.loan_amount,'collateral_value':loan.collateral_value,'tenure_years':loan.tenure_years,'interest':loan.interest,'monthly_emi':loan.monthly_emi,'disbursal_date':loan.disbursal_date,'default_date':loan.default_date}, ignore_index=True)

print(loans_df)








        # self.repayment_frequency = fake.random_element(elements=("Monthly", "Quarterly", "Semi-Annually", "Annually"))
        # self.repayment_amount = round((self.loan_amount/fake.random_int(min=12, max=60)), 2)
        # # Calculate loan repayment dates based on disbursement date and frequency 
        # if self.repayment_frequency == "Monthly":
        #     self.loan_repayment_dates = [self.loan_date + pd.DateOffset(months=i) for i in range(1,fake.random_int(min=12, max=60))]
        # elif self.repayment_frequency == "Quarterly":
        #     self.loan_repayment_dates = [self.loan_date + pd.DateOffset(months=i*3) for i in range(1,fake.random_int(min=4, max=20))]
        # elif self.repayment_frequency == "Semi-Annually":
        #     self.loan_repayment_dates = [self.loan_date + pd.DateOffset(months=i*6) for i in range(1,fake.random_int(min=2, max=10))]
        # else:
        #     self.loan_repayment_dates = [self.loan_date + pd.DateOffset(years=i) for i in range(1,fake.random_int(min=2, max=5))]
