from faker import Faker
import pandas as pd
import math
import datetime
from datetime import timedelta
import random
import os
from tqdm import tqdm
import gc

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

        # recovery_capacity would not appear on the dataset, as this is the target variable and needs to be 
        # deduced manually, its requirement is to generate variables correlated to the target variable
        self.recovery_capacity = fake.random.uniform(0.1, 0.95)

        self.collateral_value = fake.random.uniform(0.0, 0.3) * self.loan_amount
        self.collateral_value = round(self.collateral_value, 2)

        # Colateral value is part of the recovered amount, therefore recovery through payments will be:
        self.rec_by_payments = (self.loan_amount * self.recovery_capacity) - self.collateral_value

        #Disbursal date of the loan    
        self.disbursal_date = fake.date_between(start_date=datetime.date(2012,1,1), 
                                                end_date=datetime.date(2022,1,1))

        self.tenure_years = fake.random_int(min=1, max=8)

        self.interest = round(fake.random.uniform(8.0,15.0), 1)


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


    @property
    def credit_score(self):
        mean = self.recovery_capacity * 500 + 200
        std = 100
        return int(random.normalvariate(mean,std))

    @property
    def cheque_bounces(self):
        mean = (1 - self.recovery_capacity) * 4 #Inversey related
        std = 2
        return max(0, int(random.normalvariate(mean,std)))

    @property
    def number_of_loans(self):
        mean = (1 - self.recovery_capacity) * 4
        std = 1
        return max(0, int(random.normalvariate(mean, std)))

    @property
    def average_monthly_balance(self):
        mean = self.recovery_capacity * (self.loan_amount / (self.tenure_years * 12))
        std = mean * 0.4
        return random.normalvariate(mean, std)

    @property
    def missed_repayments(self):
        mean = (1 - self.recovery_capacity) * (self.tenure_years*12) * 0.6 #Inversey related
        std = 2
        return max(0, int(random.normalvariate(mean,std)))



loan_base = pd.DataFrame(columns=['loan_acc_num','customer_name','customer_address','loan_type','loan_amount',
                                  'collateral_value','credit_score', 'cheque_bounces', 'number_of_loans', 
                                  'average_monthly_balance', 'missed_repayments','tenure_years','interest',
                                  'monthly_emi','disbursal_date','default_date'])
loan_list_of_dicts = []

for _ in tqdm(range(N), desc= 'Generating the loan base...'):
    loan = Loan()
    loan_list_of_dicts.append({'loan_acc_num':loan.loan_acc_num,'customer_name':loan.customer_name,
                                  'customer_address':loan.customer_address,'loan_type':loan.loan_type,
                                  'loan_amount':loan.loan_amount,'collateral_value':loan.collateral_value,
                                  'cheque_bounces': loan.cheque_bounces, 'number_of_loans': loan.number_of_loans, 
                                  'average_monthly_balance': loan.average_monthly_balance, 
                                  'missed_repayments': loan.missed_repayments,
                                  'tenure_years':loan.tenure_years,'interest':loan.interest,
                                  'monthly_emi':loan.monthly_emi,'disbursal_date':loan.disbursal_date,
                                  'default_date':loan.default_date, 
                                  'recovery_capacity': loan.recovery_capacity, 
                                  'rec_by_payments': loan.rec_by_payments})

loan_base = pd.DataFrame(loan_list_of_dicts)
loan_base.drop(columns = ['recovery_capacity', 'rec_by_payments'], inplace = True)
loan_base.reset_index(drop=True)


#Generating the Dataset which has the repayment information

# Create an empty DataFrame for storing the repayment data
repayment_base = pd.DataFrame(columns=['loan_acc_num', 'repayment_date', 'repayment_amount'])

# Iterate through the rows of the loan_base DataFrame
for loan in tqdm(loan_list_of_dicts, desc= 'Generating repayment base..'):
    # Get the loan account number, start date, and default date
    loan_acc_num = loan['loan_acc_num']
    start_date = loan['disbursal_date'] 
    emi = loan['monthly_emi']
    rec_by_payments = loan['rec_by_payments']


    repayment_amounts = []
    repayment_dates = []

    date_counter = start_date # Initialised the date to be increased inside the loop below

    while rec_by_payments > 0:
        
        # Decide if the repayment is less than emi with 15% probability
        if random.random() < 0.15:
            # If repayment is less than emi, use faker to generate a random float between 0 and emi
            amount = fake.random.uniform(0, emi)
        else:
            # Else use full emi
            amount = emi
        
        repayment_amounts.append(amount)
        rec_by_payments -=  amount

        # Repayment dates
        date_counter += timedelta(days= 30 + fake.random_int(-6,8))
        # The timedelta adds some randomness to the repayment dates

        repayment_dates.append(date_counter)


    # Append the repayment data to the second DataFrame
    for date, amount in zip(repayment_dates, repayment_amounts):
        repayment_base = repayment_base.append({'loan_acc_num': loan_acc_num,
                                                'repayment_amount': amount,
                                                'repayment_date': date}, ignore_index=True)

repayment_base.reset_index(drop=True)


# Saving the bases as csv files
os.makedirs('output', exist_ok=True)

loan_base_path = os.path.join('output', 'main_loan_base1.csv') 
repayment_base_path = os.path.join('output', 'repayment_base1.csv')

loan_base.to_csv(loan_base_path, index = False)
repayment_base.to_csv(repayment_base_path, index = False)
