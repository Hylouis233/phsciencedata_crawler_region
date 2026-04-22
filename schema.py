METRIC_COLUMNS = ['发病数', '死亡数', '发病率(1/10万)', '死亡率(1/10万)']
DATE_COLUMNS = ['年份', '月份']
DIMENSION_COLUMNS = {
    'age': '年龄分组',
    'region': '地区',
}


def get_dimension_column(data_type: str) -> str:
    if data_type not in DIMENSION_COLUMNS:
        raise ValueError('类型必须是 age 或 region')
    return DIMENSION_COLUMNS[data_type]


def get_final_csv_columns(data_type: str) -> list[str]:
    return [get_dimension_column(data_type), *METRIC_COLUMNS, *DATE_COLUMNS]


def get_summary_required_columns(data_type: str) -> list[str]:
    return [get_dimension_column(data_type), *METRIC_COLUMNS, DATE_COLUMNS[0]]
