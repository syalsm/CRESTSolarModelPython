import numpy as np
import pandas as pd
import cashflow
import mainfunctions

# Assumptions:
# Assume technology is "Photovoltaic"
# No State Rebates, Tax Credits, and/or REC Revenue
# Cost information is "Intermediate"
# Assume YES: Owner is a taxable entity
# Federal grants Treated as Taxable Income: YES (Inputs Q30)
# Assume no decommissioning reserves (Fund from Operations)
# Reserve Requirement = $0
# Assume Bonus Depreciation = YES


def main():

	#_______________________INPUTS________________________________________

	# Project Size and Performance__________________

	#************Input: Generatory Nameplate Capacity************
	# Units: kWdc
	genNPC = 2000
	#***********************************************************

	#************Input: Net Capacity Factor************
	# Units: percentage

	# 1. Choose state for Net Capacity Factor. If no state, just write the number
	# Number should be a percentage or a state abbreviation i.e. "CA"
	netCapFac = "CA"
	state = "yes"
	netcapfacstates = pd.read_csv('data.csv')

	# 2. Look up state
	netCapFac = 0 #Enter zero if state
	stateYorN = "yes" #Enter "yes" for state and "no" for not state
	state = "CA" #Enter state abbreviation (enter 0 if not specifying)
	netcapfacstates = pd.read_csv('data.csv')

	# 2. Look up state
	if stateYorN == "yes": #Look up the state
		indexState = netcapfacstates.index[netcapfacstates['State']==state].tolist()
		netCapFac = netcapfacstates.iloc[indexState[0],1]
	elif stateYorN == "no":
		print("Custom Net CapacityFactor")
	else:
		print("Not a valid state abbreviation")
	# print('The Net Capacity Factor for CA is ', netCapFac)
	
	#****************************************************

	#--------------Calculation: Production in Year 1---------
	# Units: kW
	ProdYr1 = genNPC*netCapFac*8760 #Question: Why 8760?
	# print('Year 1 production is ', ProdYr1)
	#--------------------------------------------------------

	#************Input: Project Degredation************
	# Units: percentage (between 0.05% and 1%)
	ProjDeg = 0.005
	#**************************************************

	#************Input: Useful Life*********************
	# Units: years
	UseLife = 25
	#***************************************************

	#________________________Capital Costs______________________
	# Assume "Intermediate" level

	#************Input: Generation Eqiupment Cost************
	# Units: $
	GenEqCost = 3500000 # Original Value: 3500000
	#***********************************************************

	#************Input: Balance of Plant************
	# Units: $
	BOPCost = 2000000 # Original Value: 2000000
	#***********************************************************

	#************Input: Interconnection************
	# Units: $
	InterconCost = 500000 # Original value: 500000

	#***********************************************************

	#************Input: Development Cost and Fees************
	# Units: $
	DevCFCost = 1000000 # Original Value: 1000000 
	#***********************************************************
	
	#________________________Operations and Maintenance______________________
	# Assume "Intermediate" level

	#************Input: Fixed O&M Expense Yr 1************
	# Units: $/kW-hr dc
	FixedOandM = 6.50
	#***********************************************************

	#************Input: Variable O&M Expense Yr 1************
	# Units: cents/kW-hr dc
	VarOandM = 0
	#***********************************************************

	#************Input: O&M Cost Inflation, initial period************
	# Units: %
	OMcostinfl = 0.016
	#***********************************************************

	#************Input: Initial Period ends last day of:************
	# Units: year
	LastDay = 10
	#***********************************************************

	#************Input: O&M Cost Inflation, thereafter************
	# Units: %
	OMcostinflafter = 0.016
	#***********************************************************

	#************Input: Insurance, Year 1 (% of total cost)************
	# Units: %
	Insuryr1perc = 0.004
	#***********************************************************

	#-----------------Calculation: Insurance Year 1 ($) -------
	# Units: $
	# If calculations are "intermediate" only need capital costs
	Insuryr1 = Insuryr1perc*(GenEqCost+BOPCost+InterconCost+DevCFCost)
	# ---------------------------------------------------------

	#************Input: Project Management************
	# Units: $/yr
	ProjMan = 0
	#**************************************************

	#************Input: Property Tax or PILOT, Yr1************
	# Units: $/yr
	PILOT = 50000
	#**************************************************
	
	#************Input: Annual Property Tax Adjustment Factor************
	# Units: %
	PropTaxAd = -0.1
	#**************************************************
	
	#************Input: Land Lease************
	# Units: $/yr
	LandLease = 5000 # Original value is: 5000
	
	#**************************************************

	#************Input: Royalties (% of revenue)************
	# Units: %
	Royal = 0.03
	#**************************************************

	#________________________Construction Financing______________________

	#************Input: Construction Period************
	# Units: months
	ConstPeriod = 6
	#***********************************************************

	#************Input: Interest Rate Annual************
	# Units: %
	IntRateAnnual = 0.05
	#***********************************************************
	
	#--------------Calculation: Interest during Construction---------
	# Units: $
	IntConst = (GenEqCost + BOPCost + InterconCost + DevCFCost)*(IntRateAnnual/12)*(ConstPeriod/2)
	# print(IntConst)
	#--------------------------------------------------------

	#________________________Permanent  Financing______________________
	#************Input: % Debt % of hard costs) Mortgage-style amort.************
	# Units: %
	PercDebt = 0.45
	#***********************************************************

	#************Input: Debt Term************
	# Units: yrs
	DebtTerm = 18
	#******************************************

	#************Input: Interest Rate on Term Debt************
	# Units: %
	IntRateDebt = 0.07
	#******************************************

	#************Input: Lender's Fee (% total borrowing)************
	# Units: %
	LenderFee = 0.03
	#******************************************

	#************Input: Required Minimum Annual DSCR************
	# Units: --
	MinAnnualDSCR = 1.2
	#******************************************

	#************Input: Required Average DSCR************
	# Units: --
	AvgAnnualDSCR = 1.45
	#******************************************

	#--------------Calculation: Equity---------
	# Units: $
	Equity = 1-PercDebt
	# print(Equity)
	#--------------------------------------------------------

	#************Input: Target After-Tax Equity IRR************
	# Units: %
	AfterTaxEquity = 0.12
	#******************************************

	#************Input: Other closing costs************
	# Units: $
	ClosingCosts = 0
	#******************************************

	#________________________Tax______________________
	# Assume owner is a taxable entity
	# Adssume Federal and Tax Benefits are used as generated

	#************Input: Federal Income Tax Rate************
	# Units: %
	FedTaxRate = 0.35
	#******************************************

	#************Input: State Income Tax Rate************
	# Units: %
	StateTaxRate = 0.085 #0.123 # Changed from 8.5% in the model to match CA https://www.bankrate.com/finance/taxes/state-taxes-california.aspx
	#******************************************

	#************Calculation: Effective Income Tax Rate************
	# Units: %
	EffIncomeTaxRate = FedTaxRate + (StateTaxRate*(1-FedTaxRate)) 
	#******************************************

	#________________________Cost-Based Tariff Rate Structure______________________
	
	#************Input: Payment Duration for Cost-Based Tariff************
	# Units: years
	PayDur = 25
	#******************************************

	#************Input: % of Year-One Tariff Rate Escalated************
	# Units: %
	Yr1TariffRateEsc = 0
	#******************************************

	#************Input: Cost-Based Tariff Escalation Rate************
	# Units: %
	CostBasedTEscR = 0
	#******************************************

	#________________________Federal Incentives______________________
	# Form of Federal Incentives: Cost-Based
	# Type of incentive: Investment Tax Credit (ITC)

	#************Input: ITC amount************
	# Units: %
	ITC = 0.3
	#******************************************

	#************Input: ITC utilization factor************
	# Units: %
	ITCutilization = 1
	#******************************************

	#************Input: ITC utilization factor************
	# Units: %
	ITCutilization = 1
	#******************************************

	## No additional Federal or State taxes.

	#________________________Capital Expenditures: Inverter Replacements______________________

	#************Inputs: Equiment replacement and costs************
	# Units: year
	OneEqRepl = 10
	# Units: $/Watt dc
	OneReplCost = 0.235
	# Units: year
	TwoEqRepl = 20
	# Units: $/Watt dc
	TwoReplCost = 0.235

	# Cost for each replacement (needed for cashflow calculations)
	firstRep = OneReplCost * genNPC * 1000
	secondRep = TwoReplCost * genNPC * 1000
	#******************************************

	#____________________Reserves Funded from Operations: Decommissioning Reserves______________________
	# Fund from Operations
	ReserveReq = 0

	#________________________Initial Funding of Reserve Accounts______________________
	#************Input: # of months of Debt Service************
	# Units: month
	monthsDebt = 6
	#******************************************
	#************Input: # of months of O&M expense************
	# Units: month
	monthsOM = 6
	#******************************************
	#************Input: Interest on All Reserves************
	# Units: %
	intReserve = 0.02
	#******************************************

	#________________________Depreciation Allocation______________________
	# Assume Bonus Depreciation = YES
	#************Input: % of bonus depreciation applied in Year 1************
	# Units: % (note, this is usually a federal number)
	depY1 = 0.5
	#******************************************

	# Table of Allocation of costs (MACRS)
	macrs = pd.read_csv('macrs.csv',index_col=0)
	# print(macrs)

	macrs_halfyear = pd.read_csv('macrs_halfyear.csv',index_col=0)
	# print(macrs_halfyear.values)


	#_______________________CASH FLOW TAB___________________________________
	# Production
	# Row 0: Production Degredation Factor
	# Row 1: Production
	production = cashflow.Production(UseLife, ProdYr1, ProjDeg)
	# print('Production Matrix')
	# print(production[1,:])

	# Range of COE values
	x = np.arange(0,101,0.1)

	for i in x:
		Yr1COE, NPV = mainfunctions.CashFlowFunction(i, UseLife, Yr1TariffRateEsc, CostBasedTEscR,\
			GenEqCost, BOPCost, InterconCost, DevCFCost, PercDebt, DebtTerm, IntRateDebt, production,\
			Royal, PayDur, LastDay, OMcostinfl, OMcostinflafter, FixedOandM, genNPC, VarOandM,\
			Insuryr1, ProjMan, PILOT, PropTaxAd, LandLease, monthsDebt, monthsOM, firstRep, secondRep,\
			OneEqRepl, TwoEqRepl, ReserveReq, intReserve, LenderFee, IntConst, ClosingCosts, macrs,\
			macrs_halfyear, depY1, OneReplCost, TwoReplCost, EffIncomeTaxRate, StateTaxRate, FedTaxRate,\
			AfterTaxEquity, ITC, ITCutilization)

		if i == 0:
			NPV_min = NPV
			COE_min = Yr1COE
		else:
			if NPV_min < 0 and NPV > 0:
				COE_final = np.average([COE_min, Yr1COE])
				break
			else:
				NPV_min = NPV
				COE_min = Yr1COE

	# NOTE: Net Year One COE = Net Nominal Levelized Cost of Energy if 
	# there is a 0% Escalator

	print('Final Net Nominal Levalized COE is ', "%.2f" % COE_final)
	print('COE bounds are ', "%.2f" % COE_min, "%.2f" % Yr1COE)
	print('NPV Bounds are ', "%.2f" % NPV_min, "%.2f" % NPV)



	# ___________________CALCULATIONS (FOR LATER)

	#***********************************************************
	#************Calculation: Royalties, Yr 1 ($) for reference************
	# Units: $
	# requires the cashflow part of the spreadsheet
	#***********************************************************

	#************Calculation: Actual Min DSCR occuirs************
	# Requires values in cash flow
	# Also check if min required DSCR <= actual min dscr (if not = FAIL)
	#******************************************

	#************Calculation: Actual Average DSCR occurs************
	# Requires values in cash flow
	# Also check if avg required DSCR <= actual avg dscr (if not = FAIL)
	#******************************************
	
	#************Calculation: Weighted Average Cost of Capital (WACC)************
	# Units %
	# Requires numbers from Sources of Funding an Tax section
	#******************************************

	#************Calculation: Summary of Sources of Funding for Total Installed Cost************
	# Requires numbers from Cash flow!
	# Both dollar amounts and percentages
	#******************************************

	#--------------Calculation: ITC Grant---------
	# Units: $,assuming ITC, taxable entity, intermediate inputs
	# GrantAmt = Requires 'Cash Flow'!$C$99 * Inputs!$Q$21 * Inputs!$Q$22
	# =IF ( $G$73="Yes" # If taxable entitiy
	# 	, IF ( $Q$20="ITC" ,# credit is ITC
	# 		Value if it is true: IF ($G$18="Complex",'Complex Inputs'!$D$121,'Cash Flow'!$C$99) *Inputs!$Q$21 * Inputs!$Q$22 ,
	# 		Value if it is false:  IF($Q$20="Cash Grant",
	# 				If cash grant is true: IF($G$18="Complex",'Complex Inputs'!$D$121,'Cash Flow'!$C$99)*Inputs!$Q$21,
	# 				If cash grant is false: 0))
	# 	If not a taxable entity: ,0
	#--------------------------------------------------------


if __name__ == '__main__':
	main()







