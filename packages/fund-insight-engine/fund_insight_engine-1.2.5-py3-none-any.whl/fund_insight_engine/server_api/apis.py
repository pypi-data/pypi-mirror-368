from mongodb_controller import COLLECTION_2110
from fund_insight_engine.mongodb_retriever.general_utils import get_latest_date_in_collection
from fund_insight_engine.fund_data_retriever.fund_configuration.fund_info import fetch_data_fund_info
from fund_insight_engine.fund_data_retriever.fund_configuration.fund_numbers import fetch_data_fund_numbers
from .api_utils import set_default_benchmarks, transform_name_title, transform_name_review, transform_to_date_ref_text, transform_to_korean_unit, transform_to_usd_unit

def api__temp__title__fund_code__date_ref(fund_code, date_ref):
    info = fetch_data_fund_info(fund_code, date_ref)
    data = {
        'fund_code': fund_code,
        'name': info['펀드명'],
        'manager': info['매니저'],
        'inception_date': info['설정일'],
        'date_ref': date_ref,
        'name_title': transform_name_title(info['펀드명']),
        'name_review': transform_name_review(info['펀드명']),
        'name_index': 'Fund'
    }
    return data

def api__temp__review__fund_code__date_ref(fund_code, date_ref):
    numbers = fetch_data_fund_numbers(fund_code, date_ref)
    numbers['펀드명'], numbers['순자산'], numbers['수정기준가'], numbers['설정일']

    data = {
        '펀드명': numbers['펀드명'],
        '운용규모 (NAV)': transform_to_korean_unit(numbers['순자산']),
        '설정일': numbers['설정일'],
        '기준가': f"{numbers['수정기준가']:,} ({transform_to_date_ref_text(date_ref)} 수정기준가 기준)",
    }
    return data

def api__temp__fundinfo__fund_code__date_ref(fund_code, date_ref):
    info = fetch_data_fund_info(fund_code, date_ref)
    data = {
        'fund_code': fund_code,
        'date_ref': date_ref,
        'name': info['펀드명'],
        'name_raw': info['펀드명'],
        'name_title': transform_name_title(info['펀드명']),
        'name_review': transform_name_review(info['펀드명']),
        'name_index': 'Fund',
        'manager': info['매니저'],
        'inception_date': info['설정일'],
        'maturity_date': info['만기일'],
        'bm': info['BM1: 기준']
    }
    return data

def api__temp__latest_date():
    return get_latest_date_in_collection(COLLECTION_2110, 'date_ref')



def api__temp__total__fund_code__date_ref(fund_code, date_ref):
    info = fetch_data_fund_info(fund_code, date_ref)
    numbers = fetch_data_fund_numbers(fund_code, date_ref)
    data = {
        'name_review': transform_name_review(info['펀드명']),
        'name_title': transform_name_title(info['펀드명']),
        'manager': info['매니저'],
        'nav_num': numbers['순자산'],
        'nav_total': transform_to_korean_unit(numbers['순자산']),
        'nav_total_usd_en': transform_to_usd_unit(numbers['순자산'], date_ref),
        'price_ref': f"{numbers['수정기준가']:,}", 
        'price_ref_num': numbers['수정기준가'],
        'price_start': '1,000',
        'price_start_num': 1000,
        'inception_date': info['설정일'],
        'input_date': date_ref,
        'maturity_date': info['만기일'],
        'benchmark': info['BM1: 기준'],
        'benchmarks': set_default_benchmarks(info['BM1: 기준'])}
    return data

