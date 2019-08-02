import numpy as np
import pandas as pd

# This file contains all the functions necessary to 
# calculate the different components of the cash flow tab

# Production Matrix
def Production(UseLife, ProdYr1, ProjDeg):
	prod = np.zeros((2,UseLife))
	for i in range(UseLife):
		if i == 0:
			prod[0,i] = 1
			prod[1,i] = ProdYr1
		else:
			prod[0,i] = prod[0,i-1]*(1-ProjDeg)
			prod[1,i] = prod[0,i]*ProdYr1

	return prod

def TariffRate(UseLife, Yr1TariffRateEsc, CostBasedTEscR, Yr1COE):
	# Row 0: Tarrif Rate Escalator (if applicable)
	# Row 1: Federal PBI Escalator (if applicable), 1 if no PBI
	# Row 2: State PBI Escalator (if applicable), 1 if no PBI
	# Row 3: Tariff Rate (Fixed Portion)
	# Row 4: Tariff Rate (Escalating Portion)
	# Row 5: Tariff Rate (Total)

	tariff = np.zeros((6,UseLife))
	tariffrate = 1- Yr1TariffRateEsc

	for i in range(UseLife):
			if i == 0:
				tariff[0,i] = 1
				tariff[1,i] = 1
				tariff[2,i] = 1
				tariff[3,i] = (1-Yr1TariffRateEsc)*Yr1COE
				tariff[4,i] = (Yr1TariffRateEsc)*Yr1COE
			else:
				tariff[0,i] = tariff[0,i-1]*(1+(Yr1TariffRateEsc*CostBasedTEscR))
				tariff[1,i] = 1 
				tariff[2,i] = 1
				tariff[3,i] = tariff[3,i-1]
				tariff[4,i] = tariff[4,i-1]*(1+CostBasedTEscR)

	tariff[5,:] = tariff[3,:] + tariff[4,:]

	return tariff


def ProjectRevenue(UseLife, PayDur, RevfromTar, PTMarValue, FedCashIncRate, \
	StateCashIncRate, InterestEarned, production):
	#Output: Project Revenue, All sources

	marketRev = np.zeros((1,UseLife))
	for i in range(UseLife):
		if i <= PayDur:
			marketRev[0,i] = 0
		else:
			marketRev[0,i] = (PTMarValue*production[1,i])/100


	fedCashInc = (FedCashIncRate*production[1,:])/100
	stateCashInc = StateCashIncRate


	projectRev = RevfromTar+marketRev+fedCashInc+stateCashInc+InterestEarned

	return projectRev

def Royalties(UseLife, Royal, PayDur, RevfromTar, PTMarValue, \
	FedCashIncRate, StateCashIncRate, production):
	#Output: Royalties

	marketRev = np.zeros((1,UseLife))
	for i in range(UseLife):
		if i <= PayDur:
			marketRev[0,i] = 0
		else:
			marketRev[0,i] = (PTMarValue*production[1,i])/100


	fedCashInc = (FedCashIncRate*production[1,:])/100
	stateCashInc = StateCashIncRate

	royalties = -Royal*(RevfromTar+marketRev+fedCashInc+stateCashInc)

	return royalties

def TotalOpExpenses(LastDay, UseLife, OMcostinfl, OMcostinflafter, \
	FixedOandM, genNPC, VarOandM, Insuryr1, ProjMan, PILOT, PropTaxAd, \
	LandLease, royalties, production):
	# Total Operating Expenses
	# Row 0: Operating Expense Inflation Factor
	# Row 1: Fixed O&M Expense
	# Row 2: Variable O&M Expense
	# Row 3: Insurance
	# Row 4: Project Administration
	# Row 5: Property Tax or Payment in Lieu of Taxes (PILOT)
	# Row 6: Land Lease
	# Row 7: Total Operating Expenses $
	# Row 8: Total Operating Expenses cents/kWh
	OpExp = np.zeros((9,UseLife))

	for i in range(UseLife):
		if i == 0:
			OpExp[0,i] = 1
			OpExp[5,i] = -PILOT

		else:
			if i <= LastDay: #If before inflation period
				OpExp[0,i] = OpExp[0,i-1]*(1+OMcostinfl)
			else: #If after inflation period
				OpExp[0,i] = OpExp[0,i-1]*(1+OMcostinflafter)
			OpExp[5,i] = OpExp[5,i-1]*(1+PropTaxAd)

		OpExp[1,i] = -FixedOandM*genNPC*OpExp[0,i]
		OpExp[2,i] = -VarOandM/100*production[1,i]*OpExp[0,i]
		OpExp[3,i] = -Insuryr1*OpExp[0,i]
		OpExp[4,i] = -ProjMan*OpExp[0,i]
		OpExp[6,i] = -LandLease*OpExp[0,i]
		OpExp[7,i] = OpExp[1,i] + OpExp[2,i] + OpExp[3,i]+ \
		OpExp[4,i] + OpExp[5,i] + OpExp[6,i] + royalties[0,i]
		OpExp[8,i] = OpExp[7,i]*100/production[1,i]

	return OpExp

def DebtLoan(GenEqCost, BOPCost, InterconCost, DevCFCost, TotValGrants, \
	PercDebt, UseLife,  DebtTerm, IntRateDebt):
	InstallCost = GenEqCost + BOPCost + InterconCost + DevCFCost - TotValGrants
	DebttoTotCap = PercDebt
	SizeDebt = InstallCost*DebttoTotCap

	LoanRep = np.zeros((5,UseLife))
	# Row 0: Loan Repayment: Principal (PPMT)
	# Row 1: Loan Repayment: Interest (IPMT) Interest portion of the payment
	# Row 2: Loan Repayment: Stuctured Debt Service Payment (PPMT+ IMPT)
	# Row 3: Loan Amortiziation: Beginning Balanace
	# Row 4: Loan Amortiziation: Ending Balance (beginning + Principal)

	for i in range(UseLife):
		if i < DebtTerm:
			LoanRep[0,i] = np.ppmt(IntRateDebt, i+1, DebtTerm, SizeDebt)
			LoanRep[1,i] = np.ipmt(IntRateDebt, i+1, DebtTerm, SizeDebt)
			if i == 0:
				LoanRep[3,i] = SizeDebt
				LoanRep[4,i] = LoanRep[3,i] + LoanRep[0,i]
			else:
				LoanRep[3,i] = LoanRep[4,i-1]
				LoanRep[4,i] = LoanRep[3,i] + LoanRep[0,i]
		else:
			LoanRep[0,i] = 0
			LoanRep[1,i] = 0
			LoanRep[3,i] = 0
			LoanRep[4,i] = 0
		
		LoanRep[2,i] = LoanRep[0,i] + LoanRep[1,i]
		
	LoanRep[4,DebtTerm-1] = 0 #correct for numerical error E-9

	return LoanRep, SizeDebt

def EBITDA(TotalOpExp7, projRev, UseLife):
	EBITDA = TotalOpExp7 +projRev
	return EBITDA

def PreDepreciation(macrs, macrs_halfyear, GenEqCost, BOPCost, InterconCost,\
	DevCFCost, ResFinCost):
	# This function is not super cool - it just calculates the value for depsch[0,0] 
	# (see function Depreciation below) The only reason we need this function is because
	# We need this first value for the calculation of the ITC before calculating Depreciation!
	# Yes, this is a redundant function...but it was easier than messing up the arrays
	# in the Depreciation function.

	# Inputs needed
	macrsValues = macrs.values
	macrshalfyearValues = macrs_halfyear.values
	capcost = np.array([GenEqCost, BOPCost, InterconCost, DevCFCost, ResFinCost])

	preDepValue = np.sum(np.multiply(capcost, macrsValues[:,0]))

	return preDepValue

def Depreciation(macrs, macrs_halfyear, GenEqCost, BOPCost, InterconCost,\
	DevCFCost, ResFinCost, depY1, UseLife, ITCAmt, genNPC, OneEqRepl, \
	OneReplCost, TwoEqRepll, TwoReplCost, EffIncomeTaxRate, firstRep, secondRep):
	# Assumption: Bonus Depreciation = "yes"

	#Need macrs values and calculate the sum of capital costs
	macrsValues = macrs.values
	macrshalfyearValues = macrs_halfyear.values
	capcost = np.array([GenEqCost, BOPCost, InterconCost, DevCFCost, ResFinCost])

	# Output #1: Depreciation Schedules, Half Year Convention
	# Row 0: 5 Year MACRS        Column 0: Before Adjustments
	# Row 1: 7 Year MACRS        Column 1: % Allocation
	# Row 2: 15 Year MACRS       Column 2: After Adjustments
	# Row 3: 20 Year MACRS
	# Row 4: 5 Year SL
	# Row 5: 15 Year SL
	# Row 6: 20 Year SL
	# Row 7: 39 Year SL
	# Row 8: Non-Depreciable
	# Row 9: Bonus Depreciation (Note: not in order)
	# Row 10: Project Cost Basis
	# Row 11: Adustments for ITC, ITC Grant, 
	depsch = np.zeros((12,3))

	for i in range(9):
		depsch[i,0] = np.sum(np.multiply(capcost, macrsValues[:,i]))

	depsch[10,0] = sum(depsch[0:9,0])
	depsch[11,0] = 0.5*ITCAmt + 0 + 0

	for i in range(9):
		depsch[i,1] = depsch[i,0]/depsch[10,0]
		depsch[i,2] = (depsch[10,0]-depsch[11,0])*(1-depY1)*depsch[i,1]

	depsch[10,1] = sum(depsch[0:9,1])
	#Take care of bonus depreciation
	depsch[9,2] = (depsch[10,0]-depsch[11,0]) * depY1
	depsch[10,2] = sum(depsch[0:10,2])

	# Output #2: Annual Depreciation Expense, Initial Installation
	# Output #2: Annual Depreciation Expense, Initial Installation
	# Row 0: 5 Year MACRS
	# Row 1: 7 Year MACRS
	# Row 2: 15 Year MACRS
	# Row 3: 20 Year MACRS
	# Row 4: 5 Year SL
	# Row 5: 15 Year SL
	# Row 6: 20 Year SL
	# Row 7: 39 Year SL
	# Row 8: Bonus Depreciation
	annualDepExp = np.zeros((9,UseLife))
	for i in range(8):
		for j in range(UseLife):
			annualDepExp[i,j] = depsch[i,2] * macrshalfyearValues[i,j]

	annualDepExp[8,:] = depsch[9,2] * macrshalfyearValues[8,0:UseLife]

	# Output #3: Annual Depreciation Expense, Repairs, & Replacements
	# Row 0: 1st Replacement
	# Row 1: Depreciation Timing
	# Row 2: Depreciation Expense
	# Row 3: 2nd Replacement
	# Row 4: Depreciation Timing
	# Row 5: Depreciation Expense
	# Row 6: Annual Depreciation Expense
	# Row 7: Annual Depreciation Benefit
	DepReplRepairs = np.zeros((8,UseLife))

	DepReplRepairs[0, (OneEqRepl - 1)] = firstRep
	DepReplRepairs[1, (OneEqRepl-1):UseLife] = np.arange(1,(UseLife-OneEqRepl)+2)
	DepReplRepairs[2, (OneEqRepl-1):UseLife] = firstRep * macrshalfyearValues[0,0:(UseLife-OneEqRepl)+1]
	DepReplRepairs[3, (TwoEqRepll - 1)] = secondRep
	DepReplRepairs[4, (TwoEqRepll-1):UseLife] = np.arange(1,(UseLife-TwoEqRepll)+2)
	DepReplRepairs[5, (TwoEqRepll-1):UseLife] = secondRep * macrshalfyearValues[0,0:(UseLife-TwoEqRepll)+1]

	DepReplRepairs[6,:] = np.sum(annualDepExp[0:9,:], axis=0) + DepReplRepairs[2,:] + DepReplRepairs[5,:]
	DepReplRepairs[7,:] = EffIncomeTaxRate*  DepReplRepairs[6,:]

	return depsch, annualDepExp, DepReplRepairs

def ReserveAccounts(UseLife, firstRep, secondRep,InitialDebtServRes, InitialOMandWCRes,\
	DebtTerm, OneEqRepl, TwoEqRepl, ReserveReq, PayDur,intReserve):
	# Reserve Accounts
	# Row 0: Beginning Balance
	# Row 1: Debt Service Reserve
	# Row 2: O&M Working Capital Reserve
	# Row 3: Major Equipment Replacement Reserves
	# Row 4: Decommissioning Reserves
	# Row 5: Ending Balance
	# Row 6: Interest on Reserves
	# Row 7: Annual Contributions to/(Liquidations of) Reserves

	reserveacc = np.zeros((8,UseLife))

	reserveacc[1,DebtTerm] = -InitialDebtServRes
	reserveacc[2,(UseLife-1)] = -InitialOMandWCRes

	reserveacc[3,0:OneEqRepl-1] = firstRep / (OneEqRepl-1)
	reserveacc[3,OneEqRepl-1] = -firstRep
	reserveacc[3,(OneEqRepl):(TwoEqRepl-1)] =  secondRep / (TwoEqRepl - OneEqRepl - 1)
	reserveacc[3,(TwoEqRepl-1)] = -secondRep
	reserveacc[4,:] = ReserveReq / PayDur

	for i in range(UseLife):
		if i == 0:
			reserveacc[0,i] = InitialDebtServRes + InitialOMandWCRes
		else:
			reserveacc[0,i] = reserveacc[5,i-1]

		reserveacc[5,i] = np.sum(reserveacc[0:5, i])
		reserveacc[6,i] = np.average([reserveacc[0,i],reserveacc[5,i]]) * intReserve

	reserveacc[7,:] = np.sum(reserveacc[1:5,:], axis=0)

	return reserveacc

def RunningIRR(Equity, UseLife):
	runningirr = np.zeros((1,UseLife))
	for i in range(UseLife):
		runningirr[0,i] = np.irr(Equity[0:i+2])

	return runningirr

def Taxes(OpIncAftIntExp, DepReplRepairs, UseLife, StateTaxRate, FedTaxRate,\
	FederalITC, NetPreTaxCashFlowEquity):
	# Row 0: Taxable Income (Operating loss used)
	# 	Note: This is Also Taxable Income (Federal) and (State) for "as generated"
	# Row 1: State Income Taxes Saved / (Paid) before ITC/PTC
	# 	Note: Assuming no state cash incentive
	# Row 2: Federal Income Taxes Saved / (Paid) before ITC/PTC
	# Row 3:  Cash Benefit of Federal ITC, Cash Grant, or PTC
	# 	Note: Not taking into account Cost Based + Cash Grant
	# Row 4: After-Tax Cash Flow to Equity

	# NOTE: Assuming Cash Benefit of State ITC and/or PTC is $0

	tax = np.zeros((5,UseLife))

	tax[0,:] = OpIncAftIntExp - DepReplRepairs[6,:]
	tax[1,:] = - tax[0,:] * StateTaxRate
	tax[2,:] = - (tax[0,:] + tax[1,:]) * FedTaxRate
	tax[3,0] = FederalITC
	tax[4,:] = NetPreTaxCashFlowEquity[1:UseLife+1] + np.sum(tax[1:4,:], axis=0)
	# print(np.sum(tax[1:4,:], axis=0).shape)
	# print(NetPreTaxCashFlowEquity[1:UseLife+1].shape)
	return tax
