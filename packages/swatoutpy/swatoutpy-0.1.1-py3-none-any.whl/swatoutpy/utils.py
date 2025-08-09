def get_column_names():
    return {
        "rch": [
            'REACH', 'RCH', 'GIS', 'MON', 'AREAkm2', 'FLOW_INcms', 'FLOW_OUTcms',
            'EVAPcms', 'TLOSScms', 'SED_INtons', 'SED_OUTtons', 'SEDCONCmg/L',
            'ORGN_INkg', 'ORGN_OUTkg', 'ORGP_INkg', 'ORGP_OUTkg', 'NO3_INkg',
            'NO3_OUTkg', 'NH4_INkg', 'NH4_OUTkg', 'NO2_INkg', 'NO2_OUTkg',
            'MINP_INkg', 'MINP_OUTkg', 'CHLA_INkg', 'CHLA_OUTkg', 'CBOD_INkg',
            'CBOD_OUTkg', 'DISOX_INkg', 'DISOX_OUTkg', 'SOLPST_INmg', 'SOLPST_OUTmg',
            'SORPST_INmg', 'SORPST_OUTmg', 'REACTPSTmg', 'VOLPSTmg', 'SETTLPSTmg',
            'RESUSP_PSTmg', 'DIFFUSEPSTmg', 'REACBEDPSTmg', 'BURYPSTmg',
            'BED_PSTmg', 'BACTP_OUTct', 'BACTLP_OUTct', 'CMETAL#1kg', 'CMETAL#2kg',
            'CMETAL#3kg', 'TOTNkg', 'TOTPkg', 'NO3ConcMg/l', 'WTMPdegc'
        ],
       "sub": [
            "BIGSUB", "SUB", "GIS", "MON", "AREA_km2", "PRECIP_mm", "SNOMELT_mm", "PET_mm", "ET_mm",
            "SW_mm", "PERC_mm", "SURQ_mm", "GW_Q_mm", "WYLD_mm", "SYLD_t_ha", "ORGN_kg_ha", "ORGP_kg_ha",
            "NSURQ_kg_ha", "SOLP_kg_ha", "SEDP_kg_ha", "LATQ_mm", "LATNO3_kg_ha", "GWNO3_kg_ha",
            "CHLA_mg_L", "CBODU_mg_L", "DOXQ_mg_L", "TNO3_kg_ha", "QTILE_mm", "TVAP_kg_ha"
],
        "hru": [
            'LULC', 'HRU', 'GIS', 'SUB', 'MGT', 'MON', 'AREAkm2', 'PRECIPmm', 'SNOFALLmm', 'SNOMELTmm',
            'IRRmm', 'PETmm', 'ETmm', 'SW_INITmm', 'SW_ENDmm', 'PERCmm', 'GW_RCHGmm', 'DA_RCHGmm',
            'REVAPmm', 'SA_IRRmm', 'DA_IRRmm', 'SA_STmm', 'DA_STmm', 'SURQ_GENmm', 'SURQ_CNTmm',
            'TLOSSmm', 'LATQGENmm', 'GW_Qmm', 'WYLDmm', 'DAILYCN', 'TMP_AVdgC', 'TMP_MXdgC',
            'TMP_MNdgC', 'SOL_TMPdgC', 'SOLARMJ/m2', 'SYLDt/ha', 'USLEt/ha', 'N_APPkg/ha', 'P_APPkg/ha',
            'NAUTOkg/ha', 'PAUTOkg/ha', 'NGRZkg/ha', 'PGRZkg/ha', 'NCFRTkg/ha', 'PCFRTkg/ha',
            'NRAINkg/ha', 'NFIXkg/ha', 'F-MNkg/ha', 'A-MNkg/ha', 'A-SNkg/ha', 'F-MPkg/ha', 'AO-LPkg/ha',
            'L-APkg/ha', 'A-SPkg/ha', 'DNITkg/ha', 'NUPkg/ha', 'PUPkg/ha', 'ORGNkg/ha', 'ORGPkg/ha',
            'SEDPkg/ha', 'NSURQkg/ha', 'NLATQkg/ha', 'NO3Lkg/ha', 'NO3GWkg/ha', 'SOLPkg/ha',
            'P_GWkg/ha', 'W_STRS', 'TMP_STRS', 'N_STRS', 'P_STRS', 'BIOMt/ha', 'LAI', 'YLDt/ha',
            'BACTPct', 'BACTLPct', 'WTABCLIm', 'WTABSOLm', 'SNOmm', 'CMUPkg/ha', 'CMTOTkg/ha',
            'QTILEmm', 'TNO3kg/ha', 'LNO3kg/ha', 'GW_Q_Dmm', 'LATQCNTmm'
        ]

    }

def get_column_widths():
    return {
        "sub": [6, 5, 9, 5] + [10] * 25,
        "hru": [4, 5, 10, 5, 5, 5] + [10] * 66 + [11,11,10,10,10,10,10,10,10,10,10,10,10]
    }
