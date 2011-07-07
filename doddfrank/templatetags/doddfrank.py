from django import template

register = template.Library()

@register.filter
def get_id(meeting):
    return str(meeting.get('_id'))

@register.filter
def get_cftc_rulemaking_link(rulemaking):
     links = ['http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_1_Registration/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_2_Definitions/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_3_BusConductStandardsCP/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_4_BusConductStandardsInternal/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_5_CapMargin/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_6_SegBankruptcy/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_7_DCORules/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_8_SwapReview/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_9_DCOGovernance/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_10_SystemicDCO/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_11_EndUser/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_12_DCMRules/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_13_SEFRules/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_14_FBOTRegistration/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_15_RuleApproval/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_16_SwapDataRepositories/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_17_Recordkeeping/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_18_RealTimeReporting/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_19_AgSwaps/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_20_FXSwaps/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_21_JointSEC/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_22_PortfolioMargining/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_23_DFManipulation/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_24_DisruptiveTrading/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_25_Whistleblowers/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_26_PosLimits/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_27_InvestAdviser/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_28_VolckerRule/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_29_CreditRatings/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_30_FCRA/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/XXXI.ConformingAmendments/index.htm',
          'http://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/XXXII.LargeSwapsTraderReporting/index.htm',
          ]

     roman_numerals = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X',
                       'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX',
                       'XX', 'XXI', 'XXII', 'XXIII', 'XXIV', 'XXV', 'XXVI', 'XXVII',
                       'XXVIII', 'XXIX', 'XXX', 'XXXI', 'XXXII', ]

     rulemaking_numeral = rulemaking.split('.')[0]
     rulemaking_number = roman_numerals.index(rulemaking_numeral)
     return links[rulemaking_number]

@register.filter
def length(i):
    print i
    return len(i)
