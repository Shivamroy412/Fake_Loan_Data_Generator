from faker import Faker
import pandas as pd
import math
import datetime
from datetime import timedelta
import random
import os
from tqdm import tqdm

fake = Faker('en_IN')
N = 20000 #Number of entries

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

        self.tenure_years = fake.random_int(min=1, max=8)

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


loan_base = pd.DataFrame(columns=['loan_acc_num','customer_name','customer_address','loan_type','loan_amount','collateral_value','tenure_years','interest','monthly_emi','disbursal_date','default_date'])

for _ in tqdm(range(N), desc= 'Generating the loan base...'):
    loan = Loan()
    loan_base = loan_base.append({'loan_acc_num':loan.loan_acc_num,'customer_name':loan.customer_name,'customer_address':loan.customer_address,'loan_type':loan.loan_type,'loan_amount':loan.loan_amount,'collateral_value':loan.collateral_value,'tenure_years':loan.tenure_years,'interest':loan.interest,'monthly_emi':loan.monthly_emi,'disbursal_date':loan.disbursal_date,'default_date':loan.default_date}, ignore_index=True)

loan_base.reset_index(drop=True)



#Generating the Dataset which has the repayment information

# Create an empty DataFrame for storing the repayment data
repayment_base = pd.DataFrame(columns=['loan_acc_num', 'repayment_date', 'repayment_amount'])

# Iterate through the rows of the loan_base DataFrame
for i, row in tqdm(loan_base.iterrows(), desc= 'Generating repayment base..'):
    # Get the loan account number, start date, and default date
    loan_acc_num = row['loan_acc_num']
    start_date = row['disbursal_date']
    default_date = row['default_date']
    emi = row['monthly_emi']
    # Calculate the number of months between the start date and the default date
    num_months = (default_date.year - start_date.year) * 12 + default_date.month - start_date.month
    # Generate a list of repayment dates and amounts
    repayment_dates = [start_date + pd.DateOffset(months=i) + timedelta(days=fake.random_int(-6,8)) 
                        for i in range(num_months)]
                        # The timedelta adds some randomness to the repayment dates
    repayment_amounts = []
    # for each month
    for i in range(num_months):
        #decide if the repayment is less than emi with 15% probability
        if random.random() < 0.15:
            # if repayment is less than emi, use faker to generate a random float between 0 and emi
            repayment_amounts.append(fake.random.uniform(0, emi))
        else:
            # else use full emi
            repayment_amounts.append(emi)

    # Append the repayment data to the second DataFrame
    for date, amount in zip(repayment_dates, repayment_amounts):
        repayment_base = repayment_base.append({'loan_acc_num': loan_acc_num,
                                            'repayment_amount': amount,
                                            'repayment_date': date}, ignore_index=True)

repayment_base.reset_index(drop=True)


# Saving the bases as csv files
os.makedirs('output', exist_ok=True)

loan_base_path = os.path.join('output', 'main_loan_base.csv') 
repayment_base_path = os.path.join('output', 'repayment_base.csv')

loan_base.to_csv(loan_base_path, index = False)
repayment_base.to_csv(repayment_base_path, index = False)
