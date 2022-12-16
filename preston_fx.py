import pyodbc
import pandas as pd

def preston_fx_rate():
    conn_str = (
        r'DRIVER = {ODBC Driver 17 for SQL Server};'
        r'SERVER = preston;'
        r'DATABASE = RiskRaw;'
        r'Trusted_Connection = yes'
    )
    with pyodbc.connect(conn_str) as conn:
        cursor = conn.cursor()
        sql = '''
        SELECT DISTINCT
            CONVERT(date, EFFECTIVE_DATE) AS EFFECTIVE_DATE,
            FROM_CURRENCY_CODE,
            TO_CURRENCY_CODE,
            MID AS FX_RATE
        FROM rpt_SCD.Master_FN_FX_RATE
        WHERE 
            TENOR = 'SPOT' 
            AND TO_CURRENCY_CODE = 'CAD'
            AND [TYPE] = 'CAD_QUOTE_IPS'
            AND EFFECTIVE_DATE = DATEADD(d, -1, DATEADD(q, DATEDIFF(q, 0, EFFECTIVE_DATE) + 1, 0)) -- quarter end
            --AND EFFECTIVE_DATE = EOMONTH(EFFECTIVE_DATE) -- month end

        UNION ALL

        SELECT 
            CONVERT(date, EFFECTIVE_DATE) AS EFFECTIVE_DATE,
            CURRENCY_CODE AS FROM_CURRENCY_CODE,
            'CAD' AS TO_CURRENCY_CODE,
            IPS_CAD_QUOTE_MID AS FX_RATE
        FROM RPT_INFO_SERVICE.VW_MASTER_FX_RATE
        WHERE EFFECTIVE_DATE = '2019-03-31'

        ORDER BY EFFECTIVE_DATE DESC, FROM_CURRENCY_CODE
        '''
        fx_rates = pd.read_sql(sql, conn)

    return fx_rates
