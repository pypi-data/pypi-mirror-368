import logging
from collections import defaultdict
from decimal import Decimal
from typing import Optional, List, Dict

import numpy as np
import pandas as pd

from defeatbeta_api.client.duckdb_client import get_duckdb_client
from defeatbeta_api.client.duckdb_conf import Configuration
from defeatbeta_api.client.hugging_face_client import HuggingFaceClient
from defeatbeta_api.data.balance_sheet import BalanceSheet
from defeatbeta_api.data.finance_item import FinanceItem
from defeatbeta_api.data.finance_value import FinanceValue
from defeatbeta_api.data.income_statement import IncomeStatement
from defeatbeta_api.data.news import News
from defeatbeta_api.data.print_visitor import PrintVisitor
from defeatbeta_api.data.statement import Statement
from defeatbeta_api.data.stock_statement import StockStatement
from defeatbeta_api.data.transcripts import Transcripts
from defeatbeta_api.utils.case_insensitive_dict import CaseInsensitiveDict
from defeatbeta_api.utils.const import stock_profile, stock_earning_calendar, stock_historical_eps, stock_officers, \
    stock_split_events, \
    stock_dividend_events, stock_revenue_estimates, stock_earning_estimates, stock_summary, stock_tailing_eps, \
    stock_prices, stock_statement, income_statement, balance_sheet, cash_flow, quarterly, annual, \
    stock_earning_call_transcripts, stock_news, stock_revenue_breakdown
from defeatbeta_api.utils.util import load_finance_template, parse_all_title_keys, income_statement_template_type, \
    balance_sheet_template_type, cash_flow_template_type


class Ticker:
    def __init__(self, ticker, http_proxy: Optional[str] = None, log_level: Optional[str] = logging.INFO, config: Optional[Configuration] = None):
        self.ticker = ticker.upper()
        self.http_proxy = http_proxy
        self.duckdb_client = get_duckdb_client(http_proxy=self.http_proxy, log_level=log_level, config=config)
        self.huggingface_client = HuggingFaceClient()

    def info(self) -> pd.DataFrame:
        return self._query_data(stock_profile)

    def officers(self) -> pd.DataFrame:
        return self._query_data(stock_officers)

    def calendar(self) -> pd.DataFrame:
        return self._query_data(stock_earning_calendar)

    def earnings(self) -> pd.DataFrame:
        return self._query_data(stock_historical_eps)

    def splits(self) -> pd.DataFrame:
        return self._query_data(stock_split_events)

    def dividends(self) -> pd.DataFrame:
        return self._query_data(stock_dividend_events)

    def revenue_forecast(self) -> pd.DataFrame:
        return self._query_data(stock_revenue_estimates)

    def earnings_forecast(self) -> pd.DataFrame:
        return self._query_data(stock_earning_estimates)

    def summary(self) -> pd.DataFrame:
        return self._query_data(stock_summary)

    def ttm_eps(self) -> pd.DataFrame:
        return self._query_data(stock_tailing_eps)

    def price(self) -> pd.DataFrame:
        return self._query_data(stock_prices)

    def quarterly_income_statement(self) -> Statement:
        return self._statement(income_statement, quarterly)

    def annual_income_statement(self) -> Statement:
        return self._statement(income_statement, annual)

    def quarterly_balance_sheet(self) -> Statement:
        return self._statement(balance_sheet, quarterly)

    def annual_balance_sheet(self) -> Statement:
        return self._statement(balance_sheet, annual)

    def quarterly_cash_flow(self) -> Statement:
        return self._statement(cash_flow, quarterly)

    def annual_cash_flow(self) -> Statement:
        return self._statement(cash_flow, annual)

    def ttm_pe(self) -> pd.DataFrame:
        price_url = self.huggingface_client.get_url_path(stock_prices)
        price_sql = f"SELECT * FROM '{price_url}' WHERE symbol = '{self.ticker}'"
        price_df = self.duckdb_client.query(price_sql)
        eps_url = self.huggingface_client.get_url_path(stock_tailing_eps)
        eps_sql = f"SELECT * FROM '{eps_url}' WHERE symbol = '{self.ticker}'"
        eps_df = self.duckdb_client.query(eps_sql)

        price_df['report_date'] = pd.to_datetime(price_df['report_date'])
        eps_df['report_date'] = pd.to_datetime(eps_df['report_date'])
        latest_trade_date = price_df['report_date'].max()
        latest_price_data = price_df[price_df['report_date'] == latest_trade_date].iloc[0]
        pe_data = pd.merge_asof(
            eps_df.sort_values('report_date'),
            price_df.sort_values('report_date'),
            left_on='report_date',
            right_on='report_date',
            direction='forward'
        )
        pe_data['ttm_pe'] = round(pe_data['close'] / pe_data['tailing_eps'], 2)
        pe_data = pe_data[pe_data['ttm_pe'].notna() & np.isfinite(pe_data['ttm_pe'])]
        pe_data = pe_data.sort_values('report_date', ascending=False)
        latest_eps = pe_data.iloc[0]['tailing_eps']
        current_pe = round(latest_price_data['close'] / latest_eps, 2)
        result_data = {
            'report_date': [],
            'ttm_pe': [],
            'price': [],
            'ttm_eps': []
        }

        result_data['report_date'].append(latest_price_data['report_date'].strftime('%Y-%m-%d'))
        result_data['ttm_pe'].append(current_pe)
        result_data['price'].append(latest_price_data['close'])
        result_data['ttm_eps'].append(latest_eps)
        for row in pe_data.itertuples():
            result_data['report_date'].append(row.report_date.strftime('%Y-%m-%d'))
            result_data['ttm_pe'].append(row.ttm_pe)
            result_data['price'].append(row.close)
            result_data['ttm_eps'].append(row.tailing_eps)

        return pd.DataFrame(result_data)

    def quarterly_gross_margin(self) -> pd.DataFrame:
        return self._generate_margin_sql('gross', 'quarterly', 'gross_profit', 'gross_margin')

    def annual_gross_margin(self) -> pd.DataFrame:
        return self._generate_margin_sql('gross', 'annual', 'gross_profit', 'gross_margin')

    def quarterly_operating_margin(self) -> pd.DataFrame:
        return self._generate_margin_sql('operating', 'quarterly', 'operating_income', 'operating_margin')

    def annual_operating_margin(self) -> pd.DataFrame:
        return self._generate_margin_sql('operating', 'annual', 'operating_income', 'operating_margin')

    def quarterly_net_margin(self) -> pd.DataFrame:
        return self._generate_margin_sql('net', 'quarterly', 'net_income_common_stockholders', 'net_margin')

    def annual_net_margin(self) -> pd.DataFrame:
        return self._generate_margin_sql('net', 'annual', 'net_income_common_stockholders', 'net_margin')

    def quarterly_ebitda_margin(self) -> pd.DataFrame:
        return self._generate_margin_sql('ebitda', 'quarterly', 'ebitda', 'ebitda_margin')

    def annual_ebitda_margin(self) -> pd.DataFrame:
        return self._generate_margin_sql('ebitda', 'annual', 'ebitda', 'ebitda_margin')

    def quarterly_fcf_margin(self) -> pd.DataFrame:
        return self._generate_margin_sql('fcf', 'quarterly', 'free_cash_flow', 'fcf_margin')

    def annual_fcf_margin(self) -> pd.DataFrame:
        return self._generate_margin_sql('fcf', 'annual', 'free_cash_flow', 'fcf_margin')

    def earning_call_transcripts(self) -> Transcripts:
        return Transcripts(self._query_data(stock_earning_call_transcripts))

    def news(self) -> News:
        url = self.huggingface_client.get_url_path(stock_news)
        sql = f"SELECT * FROM '{url}' WHERE ARRAY_CONTAINS(related_symbols, '{self.ticker}') ORDER BY report_date ASC"
        return News(self.duckdb_client.query(sql))

    def revenue_by_segment(self) -> pd.DataFrame:
        return self._revenue_by_breakdown('segment')

    def revenue_by_geography(self) -> pd.DataFrame:
        return self._revenue_by_breakdown('geography')

    def revenue_by_product(self) -> pd.DataFrame:
        return self._revenue_by_breakdown('product')

    def quarterly_revenue_yoy_growth(self) -> pd.DataFrame:
        return self._calculate_yoy_growth(item_name='total_revenue', period_type='quarterly', finance_type='income_statement')

    def annual_revenue_yoy_growth(self) -> pd.DataFrame:
        return self._calculate_yoy_growth(item_name='total_revenue', period_type='annual', finance_type='income_statement')

    def quarterly_operating_income_yoy_growth(self) -> pd.DataFrame:
        return self._calculate_yoy_growth(item_name='operating_income', period_type='quarterly', finance_type='income_statement')

    def annual_operating_income_yoy_growth(self) -> pd.DataFrame:
        return self._calculate_yoy_growth(item_name='operating_income', period_type='annual', finance_type='income_statement')

    def quarterly_net_income_yoy_growth(self) -> pd.DataFrame:
        return self._calculate_yoy_growth(item_name='net_income_common_stockholders', period_type='quarterly', finance_type='income_statement')

    def annual_net_income_yoy_growth(self) -> pd.DataFrame:
        return self._calculate_yoy_growth(item_name='net_income_common_stockholders', period_type='annual', finance_type='income_statement')

    def quarterly_fcf_yoy_growth(self) -> pd.DataFrame:
        return self._calculate_yoy_growth(item_name='free_cash_flow', period_type='quarterly', finance_type='cash_flow')

    def annual_fcf_yoy_growth(self) -> pd.DataFrame:
        return self._calculate_yoy_growth(item_name='free_cash_flow', period_type='annual', finance_type='cash_flow')

    def quarterly_eps_yoy_growth(self) -> pd.DataFrame:
        return self._quarterly_eps_yoy_growth('eps', 'eps', 'prev_year_eps')

    def quarterly_ttm_eps_yoy_growth(self) -> pd.DataFrame:
        return self._quarterly_eps_yoy_growth('tailing_eps', 'ttm_eps', 'prev_year_ttm_eps')

    def _quarterly_eps_yoy_growth(self, eps_column: str, current_alias: str, prev_alias: str) -> pd.DataFrame:
        url = self.huggingface_client.get_url_path(stock_tailing_eps)
        as_current = f" as {current_alias}" if current_alias != eps_column else ""
        sql = f"""
            WITH quarterly_eps AS (
                SELECT 
                    symbol,
                    report_date,
                    {eps_column},
                    LAG({eps_column}, 4) OVER (PARTITION BY symbol ORDER BY report_date) as prev_year_eps
                FROM '{url}'
                WHERE symbol = '{self.ticker}'
                AND {eps_column} IS NOT NULL
            )
            SELECT 
                symbol,
                report_date,
                {eps_column}{as_current},
                prev_year_eps as {prev_alias},
                CASE 
                    WHEN prev_year_eps IS NOT NULL AND prev_year_eps != 0 
                    THEN ROUND((({eps_column} - prev_year_eps) / ABS(prev_year_eps)), 4)
                    WHEN prev_year_eps IS NOT NULL AND prev_year_eps = 0 AND {eps_column} > 0
                    THEN 1.00
                    WHEN prev_year_eps IS NOT NULL AND prev_year_eps = 0 AND {eps_column} < 0
                    THEN -1.00
                    ELSE NULL
                END as yoy_growth
            FROM quarterly_eps
            ORDER BY report_date;
        """
        return self.duckdb_client.query(sql)

    def _calculate_yoy_growth(self, item_name: str, period_type: str, finance_type: str) -> pd.DataFrame:
        url = self.huggingface_client.get_url_path(stock_statement)
        metric_name = item_name.replace('total_', '')  # For naming consistency in output
        lag_period = 4 if period_type == 'quarterly' else 1
        ttm_filter = "AND report_date != 'TTM'" if period_type == 'quarterly' else ''

        sql = f"""
            WITH metric_data AS (
                SELECT 
                    symbol,
                    report_date,
                    item_value as {metric_name},
                    LAG(item_value, {lag_period}) OVER (PARTITION BY symbol ORDER BY report_date) as prev_year_{metric_name}
                FROM '{url}' 
                WHERE symbol='{self.ticker}' 
                    AND finance_type = '{finance_type}' 
                    AND item_name='{item_name}' 
                    AND period_type='{period_type}'
                    {ttm_filter}
            )
            SELECT 
                symbol,
                report_date,
                {metric_name},
                prev_year_{metric_name},
                CASE 
                    WHEN prev_year_{metric_name} IS NOT NULL AND prev_year_{metric_name} != 0 
                    THEN ROUND(({metric_name} - prev_year_{metric_name}) / ABS(prev_year_{metric_name}), 4)
                    ELSE NULL
                END as yoy_growth
            FROM metric_data
            WHERE {metric_name} IS NOT NULL
            ORDER BY report_date;
        """
        return self.duckdb_client.query(sql)

    def _revenue_by_breakdown(self, breakdown_type: str) -> pd.DataFrame:
        url = self.huggingface_client.get_url_path(stock_revenue_breakdown)
        sql = f"SELECT * FROM '{url}' WHERE symbol = '{self.ticker}' AND breakdown_type = '{breakdown_type}' ORDER BY report_date ASC"
        data = self.duckdb_client.query(sql)
        df_wide = data.pivot(index=['report_date'], columns='item_name', values='item_value').reset_index()
        df_wide.columns.name = None
        df_wide = df_wide.fillna(0)
        return df_wide

    def _generate_margin_sql(self, margin_type: str, period_type: str, numerator_item: str,
                             margin_column: str) -> pd.DataFrame:
        ttm_filter = "AND report_date != 'TTM'" if period_type == 'quarterly' else ""
        finance_type_filter = \
            "AND finance_type = 'income_statement'" if margin_type in ['gross', 'operating', 'net', 'ebitda'] \
            else "AND finance_type in ('income_statement', 'cash_flow')" if margin_type == 'fcf' \
            else ""
        sql = f"""
            SELECT symbol,
                   report_date,
                   {numerator_item},
                   total_revenue,
                   round({numerator_item}/total_revenue, 4) as {margin_column}
            FROM (
                SELECT
                     symbol,
                     report_date,
                     MAX(CASE WHEN t1.item_name = '{numerator_item}' THEN t1.item_value END) AS {numerator_item},
                     MAX(CASE WHEN t1.item_name = 'total_revenue' THEN t1.item_value END) AS total_revenue
                  FROM '{self.huggingface_client.get_url_path('stock_statement')}' t1
                  WHERE symbol = '{self.ticker}'
                    {finance_type_filter}
                    {ttm_filter}
                    AND item_name IN ('{numerator_item}', 'total_revenue')
                    AND period_type = '{period_type}'
                  GROUP BY symbol, report_date
            ) t 
            ORDER BY report_date ASC
        """
        return self.duckdb_client.query(sql)

    def _query_data(self, table_name: str) -> pd.DataFrame:
        url = self.huggingface_client.get_url_path(table_name)
        sql = f"SELECT * FROM '{url}' WHERE symbol = '{self.ticker}'"
        return self.duckdb_client.query(sql)

    def _statement(self, finance_type: str, period_type: str) -> Statement:
        url = self.huggingface_client.get_url_path(stock_statement)
        sql = f"SELECT * FROM '{url}' WHERE symbol = '{self.ticker}' and finance_type = '{finance_type}' and period_type = '{period_type}'"
        df = self.duckdb_client.query(sql)
        stock_statements = self._dataframe_to_stock_statements(df=df)
        if finance_type == income_statement:
            template_type = income_statement_template_type(df)
            template = load_finance_template(income_statement, template_type)
            finance_values_map = self._get_finance_values_map(statements=stock_statements, finance_template=template)
            stmt = IncomeStatement(finance_template=template, income_finance_values=finance_values_map)
            printer = PrintVisitor()
            stmt.accept(printer)
            return printer.get_statement()
        elif finance_type == balance_sheet:
            template_type = balance_sheet_template_type(df)
            template = load_finance_template(balance_sheet, template_type)
            finance_values_map = self._get_finance_values_map(statements=stock_statements, finance_template=template)
            stmt = BalanceSheet(finance_template=template, income_finance_values=finance_values_map)
            printer = PrintVisitor()
            stmt.accept(printer)
            return printer.get_statement()
        elif finance_type == cash_flow:
            template_type = cash_flow_template_type(df)
            template = load_finance_template(cash_flow, template_type)
            finance_values_map = self._get_finance_values_map(statements=stock_statements, finance_template=template)
            stmt = BalanceSheet(finance_template=template, income_finance_values=finance_values_map)
            printer = PrintVisitor()
            stmt.accept(printer)
            return printer.get_statement()
        else:
            raise ValueError(f"unknown finance type: {finance_type}")

    @staticmethod
    def _dataframe_to_stock_statements(df: pd.DataFrame) -> List[StockStatement]:
        statements = []

        for _, row in df.iterrows():
            try:
                item_value = Decimal(str(row['item_value'])) if not pd.isna(row['item_value']) else None
                statement = StockStatement(
                    symbol=str(row['symbol']),
                    report_date=str(row['report_date']),
                    item_name=str(row['item_name']),
                    item_value=item_value,
                    finance_type=str(row['finance_type']),
                    period_type=str(row['period_type'])
                )
                statements.append(statement)
            except Exception as e:
                print(f"Error processing row {row}: {str(e)}")
                continue

        return statements

    @staticmethod
    def _get_finance_values_map(statements: List['StockStatement'],
                                finance_template: Dict[str, 'FinanceItem']) -> Dict[str, List['FinanceValue']]:
        finance_item_title_keys = CaseInsensitiveDict()
        parse_all_title_keys(list(finance_template.values()), finance_item_title_keys)

        finance_values = defaultdict(list)

        for statement in statements:
            period = "TTM" if statement.report_date == "TTM" else (
                "3M" if statement.period_type == "quarterly" else "12M")
            value = FinanceValue(
                finance_key=statement.item_name,
                report_date=statement.report_date,
                report_value=statement.item_value,
                period_type=period
            )
            finance_values[statement.item_name].append(value)

        final_map = CaseInsensitiveDict()

        for title, values in finance_values.items():
            key = finance_item_title_keys.get(title)
            if key is not None:
                final_map[key] = values

        return final_map

    def download_data_performance(self) -> str:
        res = f"-------------- Download Data Performance ---------------"
        res += f"\n"
        res += self.duckdb_client.query(
            "SELECT * FROM cache_httpfs_cache_access_info_query()"
        ).to_string()
        res += f"\n"
        res += f"--------------------------------------------------------"
        return res