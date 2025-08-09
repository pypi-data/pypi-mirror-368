"""
fseconomy.core.data.summary
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains data handling functions for the FBO Monthly Summary data feed.
"""
from typing import Union
from ...exceptions import FseDataParseError
from ...util import xml


def __decode_summary(summary: dict[str, str]) -> dict[str, Union[float, int, str]]:
    """Private function to decode data representing one single FBO monthly summary

    :param summary: Python dictionary derived from FSEconomy server XML output
    :type summary: dict
    :return: dictionary with FBO monthly summary information decoded into native Python data types
    :rtype: dict
    """
    return {
        'Owner': str(summary['Owner']).strip(),
        'ICAO': str(summary['ICAO']).strip(),
        'Month': int(summary['Month']),
        'Year': int(summary['Year']),
        'Assignment_Rental_Expenses': float(summary['Assignment_Rental_Expenses']),
        'Assignment_Income': float(summary['Assignment_Income']),
        'Assignment_Expenses': float(summary['Assignment_Expenses']),
        'Assignment_Pilot_Fees': float(summary['Assgiment_Pilot_Fees']),
        'Assignment_Additional_Crew_Fees': float(summary['Assgiment_Additional_Crew_Fees']),
        'Assignment_Ground_Crew_Fees': float(summary['Assgiment_Ground_Crew_Fees']),
        'Assignment_Booking_Fees': float(summary['Assgiment_Booking_Fees']),
        'Aircraft_Ops_Rental_Income': float(summary['Aircraft_Ops_Rental_Income']),
        'Aircraft_Ops_Refueling_100LL': float(summary['Aircraft_Ops_Refueling_100LL']),
        'Aircraft_Ops_Refueling_JetA': float(summary['Aircraft_Ops_Refueling_JetA']),
        'Aircraft_Ops_Landing_Fees': float(summary['Aircraft_Ops_Landing_Fees']),
        'Aircraft_Ops_Expenses_for_Maintenance': float(summary['Aircraft_Ops_Expenses_for_Maintenance']),
        'Aircraft_Ops_Equipment_Installation': float(summary['Aircraft_Ops_Equipment_Installation']),
        'Aircraft_Sold': float(summary['Aircraft_Sold']),
        'Aircraft_Bought': float(summary['Aircraft_Bought']),
        'Fbo_Ops_Refueling_100LL': float(summary['Fbo_Ops_Refueling_100LL']),
        'Fbo_Ops_Refueling_JetA': float(summary['Fbo_Ops_Refueling_JetA']),
        'Fbo_Ops_Ground_Crew_Fees': float(summary['Fbo_Ops_Ground_Crew_Fees']),
        'Fbo_Ops_Repairshop_Income': float(summary['Fbo_Ops_Repairshop_Income']),
        'Fbo_Ops_Repairshop_Expenses': float(summary['Fbo_Ops_Repairshop_Expenses']),
        'Fbo_Ops_Equipment_Installation': float(summary['Fbo_Ops_Equipment_Installation']),
        'Fbo_Ops_Equipment_Expenses': float(summary['Fbo_Ops_Equipment_Expenses']),
        'PT_Rent_Income': float(summary['PT_Rent_Income']),
        'PT_Rent_Expenses': float(summary['PT_Rent_Expenses']),
        'FBO_Sold': float(summary['FBO_Sold']),
        'FBO_Bought': float(summary['FBO_Bought']),
        'Goods_Bought_Wholesale_100LL': float(summary['Goods_Bought_Wholesale_100LL']),
        'Goods_Bought_Wholesale_JetA': float(summary['Goods_Bought_Wholesale_JetA']),
        'Goods_Bought_Building_Materials': float(summary['Goods_Bought_Building_Materials']),
        'Goods_Bought_Supplies': float(summary['Goods_Bought_Supplies']),
        'Goods_Sold_Wholesale_100LL': float(summary['Goods_Sold_Wholesale_100LL']),
        'Goods_Sold_Wholesale_JetA': float(summary['Goods_Sold_Wholesale_JetA']),
        'Goods_Sold_Building_Materials': float(summary['Goods_Sold_Building_Materials']),
        'Goods_Sold_Supplies': float(summary['Goods_Sold_Supplies']),
        'Group_Payments': float(summary['Group_Payments']),
        'Group_Deletion': float(summary['Group_Deletion']),
        'Net_Total': float(summary['Net_Total']),
        'Current_Ops': int(summary['Current_Ops']),
        'Avg_Ops': int(summary['Avg_Ops'])
    }


def decode(raw_data: str) -> list[dict[str, Union[float, int, str]]]:
    """Decode FSEconomy FBO monthly summary data

    :raises FseDataParseError: in case of malformed data provided

    :param raw_data: string with raw XML data representing an FBO monthly summary data feed
    :type raw_data: str
    :return: list of dictionaries representing each an FBO monthly summary from the data feed
    :rtype: list[dict]
    """
    data = xml.to_python(raw_data)
    result = []
    if isinstance(data, str) and data.strip() == '':
        return result
    try:
        if 'FboMonthlySummary' in data['FboMonthlySummaryItems']:
            result.append(__decode_summary(data['FboMonthlySummaryItems']['FboMonthlySummary']['FboMonthlySummary']))
        elif 'FboMonthlySummarys' in data['FboMonthlySummaryItems']:
            for item in data['FboMonthlySummaryItems']['FboMonthlySummarys']:
                result.append(__decode_summary(item['FboMonthlySummary']))
        return result
    except (KeyError, IndexError) as e:
        raise FseDataParseError(e)
