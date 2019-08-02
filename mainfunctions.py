import numpy as np
import pandas as pd
import cashflow

# This file contains all the calculations for the cashflow tab

def CashFlowFunction(Yr1COE, UseLife, Yr1TariffRateEsc, CostBasedTEscR, GenEqCost, BOPCost,\
	InterconCost, DevCFCost, PercDebt, DebtTerm, IntRateDebt, production, Royal, PayDur, LastDay,\
	OMcostinfl, OMcostinflafter, FixedOandM, genNPC, VarOandM, Insuryr1, ProjMan, PILOT, PropTaxAd,\
	LandLease, monthsDebt, monthsOM, firstRep, secondRep, OneEqRepl, TwoEqRepl, ReserveReq,\
	intReserve, LenderFee, IntConst, ClosingCosts, macrs, macrs_halfyear, depY1, OneReplCost,\
	TwoReplCost, EffIncomeTaxRate, StateTaxRate, FedTaxRate, AfterTaxEquity, ITC, ITCutilization):

	# Tariff Rate & Cash Incentives (assume no PBI)
	tariff = cashflow.TariffRate(UseLife, Yr1TariffRateEsc, CostBasedTEscR, Yr1COE)
	# print('Tariff Info')
	# print(tariff)

	# Simplified inputs for DebtLoan
	TotValGrants = 0 #SIMPLIFIED! Can calculate Total Value of Grants

	# Debt Service, Loan Repayment, and Loan Amortization
	loanRep, sizeDebt = cashflow.DebtLoan(GenEqCost, BOPCost, InterconCost, DevCFCost, \
		TotValGrants, PercDebt, UseLife,  DebtTerm, IntRateDebt)
	# print('Loan Information Matrix')
	# print(loanRep)
	# print('Size of Debt')
	# print(sizeDebt)

	# Inputs needed for Royalties
	TariffRate = tariff[5,:]
	RevfromTar = np.multiply(TariffRate,production[1,:])/100
	PTMarValue = np.zeros((1,UseLife)) # SIMPLIFIED,but doesn't matter
	FedCashIncRate = np.zeros((1,UseLife)) #SIMPLIFIED, but doesn't matter
	StateCashIncRate = np.zeros((1,UseLife)) #SIMPLIFIED, but doesn't matter

	# Royalties
	royalties = cashflow.Royalties(UseLife, Royal, PayDur, RevfromTar, PTMarValue, \
	FedCashIncRate, StateCashIncRate, production)

	# Project Expenses
	TotalOpExp = cashflow.TotalOpExpenses(LastDay, UseLife, OMcostinfl, \
		OMcostinflafter, FixedOandM, genNPC, VarOandM, Insuryr1, ProjMan, \
		PILOT, PropTaxAd, LandLease, royalties, production)
	# print('Total Operating Expenses Matrix')
	# print(TotalOpExp)


	#_________________INTERLUDE OF CALCULATIONS______________________
	#************Calculation: Initial Debt Service Reserve************
	# Units: $ 
	InitialDebtServRes = -loanRep[2,0]/12 * monthsDebt
	#******************************************
	#************Calculation: Initial Debt Service Reserve************
	# Units: $ 
	InitialDebtServRes = -loanRep[2,0]/12 * monthsDebt
	#******************************************

	#************Calculation: Initial O&M and WC Reserve************
	# Units: $
	InitialOMandWCRes = -(np.average(TotalOpExp[7,:]) / 12 * monthsOM)
	#******************************************
	#_________________________________________________________________


	# Reserve Accounts
	reserveAcc = cashflow.ReserveAccounts(UseLife, firstRep, secondRep,InitialDebtServRes, \
		InitialOMandWCRes,DebtTerm, OneEqRepl, TwoEqRepl, ReserveReq, PayDur,intReserve)
	# print(reserveAcc)
	
	# Inputs needed for Project Revenue
	InterestEarned = reserveAcc[6,:]
	# print(reserveAcc[6,:])

	# Project Revenue, All Sources
	projectRevenue = cashflow.ProjectRevenue(UseLife, PayDur, RevfromTar, \
		PTMarValue, FedCashIncRate, StateCashIncRate, InterestEarned, production)

	# EBITDA
	ebitda = cashflow.EBITDA(TotalOpExp[7,:], projectRevenue, UseLife)
	# print('EBITDA')
	# print(ebitda)


	#_________________INTERLUDE OF CALCULATIONS______________________

	#************Calculation: Reserves & Financing Costs************
	# Units: $
	ResFinCost = LenderFee * PercDebt * (GenEqCost + BOPCost + InterconCost + DevCFCost) + \
	IntConst+ ClosingCosts + InitialDebtServRes +InitialOMandWCRes
	#***********************************************************
	#************Calculation: Installed Costs (before rebates/grants)************
	# Units: $	Total Installed Cost
	TotalInstallCost = GenEqCost + BOPCost + InterconCost + DevCFCost + ResFinCost
	# Installed Costs in $/Wattdc
	Installperwatt = TotalInstallCost / genNPC / 1000
	#***********************************************************
	#_________________________________________________________________

	# Inputs required for Depreciation and Tax Calculations (assume Yes tax entity, ITC)
	FederalITC = cashflow.PreDepreciation(macrs, macrs_halfyear, GenEqCost, BOPCost, \
		InterconCost,DevCFCost, ResFinCost) * ITC * ITCutilization

	# Depreciation
	# depsch: Project Cost Allocation table
	# annualDepExp: Depreciation Expense, Initial Installation
	# depReplRepairs: Depreciation Expense, REpairs & Replacements
	# firstRep: Cost for 1st replacement
	# secondRep: Cost for 2nd replacement
	depsch, annualDepExp, depReplRepairs = cashflow.Depreciation(macrs, \
		macrs_halfyear, GenEqCost, BOPCost, InterconCost,DevCFCost, ResFinCost, depY1, \
		UseLife, FederalITC, genNPC, OneEqRepl, OneReplCost,TwoEqRepl, TwoReplCost, \
		EffIncomeTaxRate, firstRep, secondRep)
	# print('The table for Depreciation Schedules, Half Year Convention is: ')
	# print(depsch)
	# print('The table for Annual DepreciationExpense, Initial Installation is: ')
	# print(annualDepExp)
	# Check the values:
	# print(np.sum(annualDepExp, axis=1))
	# print('The table for Annual DepreciationExpense, Initial Installation is: ')
	# print(depReplRepairs)

	# Operating Income After Interest Expense
	OpIncAftIntExp = loanRep[1,:] + ebitda
	# print('Operating Income After Interest Expense')
	# print(OpIncAftIntExp)

	# Pre-Tax CashFlow to Equity
		# Repayment of Loan Principle: loanRep, row 0
		# (Contributions to), and Liquidation of, Reserve Accounts: -reserveacc, row 7
		# Adjustment(s) for Major Equipment Replacement(s): min of 0 and reserveacc, row 3
		# Also needs Operating Income after Interest Expense
	preTaxCashFlowEquity = loanRep[0,:] - reserveAcc[7,:] + np.minimum(reserveAcc[3,:], 0) \
	+ OpIncAftIntExp
	# print(preTaxCashFlowEquity)

	# Net Pre-Tax Cash Flow to Equity
	# Assume initial equity investment, then $0 for rest of time
	# Thus, "Net Pre-Tax Cash Flow to Equity" is the same as
	# "Pre-Tax Cash Flow to Equity" just with a year 0 as the initial
	# equity investment
	initialEquityInv = -(TotalInstallCost - TotValGrants - sizeDebt)
	NetPreTaxCashFlowEquity = np.append(initialEquityInv, preTaxCashFlowEquity)

	# Running IRR (Cash Only)
	runningIRRcashonly = cashflow.RunningIRR(NetPreTaxCashFlowEquity, UseLife)
	# print(runningIRR)

	# Taxes
	taxInfo = cashflow.Taxes(OpIncAftIntExp, depReplRepairs, UseLife, StateTaxRate, \
		FedTaxRate, FederalITC, NetPreTaxCashFlowEquity)
	# np.set_printoptions(formatter={'float_kind':'{:f}'.format})
	# print(taxInfo)

	# Add on initial equity investment before calculating IRR
	AfterTaxCashFlowEquity = np.append(initialEquityInv, taxInfo[4,:])

	# Running IRR (After Tax)
	runningIRRaftertax = cashflow.RunningIRR(AfterTaxCashFlowEquity, UseLife)

	#******************Calculations for IRR/NPV (blue box in spreadsheet)
	# Pre-Tax (Cash-only) Equity IRR (over defined Useful Life)
	PreTaxCashEquityIRR = runningIRRcashonly[0,UseLife-1]
	# print(PreTaxCashEquityIRR)
	# After Tax Equity IRR (over defined Useful Life)
	# AfterTaxEquityIRR = runningIRRaftertax[0,UseLife-1]
	# Net Present Value @ 12% (over defined Useful Life)
	# (needed to add zero to beginning because numpy NPV is calculated differently)
	AfterTaxCashFlowEquityMOD = np.append([[0]],AfterTaxCashFlowEquity)
	NPV = np.npv(AfterTaxEquity, AfterTaxCashFlowEquityMOD)

	return Yr1COE, NPV