

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

try:
    from adiftools.errors import AdifParserError
except ModuleNotFoundError or ImportError:
    from errors import AdifParserError


def monthly_qso(df, fname):
    ''' plot monthly QSO '''
    if len(df) < 0:
        raise AdifParserError('Empty adif data')

    df['QSO_DATE'] = pd.to_datetime(df['QSO_DATE'])
    df['QSO_DATE'] = df['QSO_DATE'].dt.to_period('M')
    df = df.groupby('QSO_DATE').size().reset_index(name='counts')
    df.set_index('QSO_DATE', inplace=True)

    fig, ax = plt.subplots(figsize=(12, 6))
    bar = ax.bar(df.index.astype(str), df['counts'])

    # basic graph elements
    plt.title('Monthly QSO')
    plt.xlabel('Month')
    plt.ylabel('Number of QSO')
    plt.xticks(rotation=90)
    plt.grid(axis='y')
    ax.set_axisbelow(True)
    plt.legend(['Number of QSO'], loc='upper right')

    # add value on top of each bar
    if len(df) < 24:
        text_rotation = 0
    else:
        text_rotation = 90

    for rect in bar:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2., height + 1,
                '%d' % int(height), ha='center', va='bottom',
                size='small', rotation=text_rotation)

    # set layout and save to file
    plt.subplots_adjust(left=0.08, right=0.98, bottom=0.18, top=0.93)
    plt.savefig(fname)
    plt.close()


def band_percentage(df, fname):
    ''' generate circle graph for band percentage '''
    # caclulate mode percentage
    if len(df) < 0:
        raise AdifParserError('Empty adif data')

    if 'BAND' in df.columns:
        mode_counts = df['BAND'].value_counts()
    else:
        raise ValueError('BAND column not found in DataFrame')

    # plot circle graph
    _, ax = plt.subplots()
    ax.pie(mode_counts, labels=mode_counts.index, autopct='%1.1f%%',
           startangle=90, counterclock=False)
    plt.title('Band Percentage')
    plt.savefig(fname)
    plt.close()


def monthly_band_qso(df, fname):
    '''バンド別の月間QSO数を積み上げ棒グラフで描画'''
    if len(df) < 0:
        raise AdifParserError('Empty adif data')

    if 'BAND' not in df.columns:
        raise ValueError('BAND column not found in DataFrame')

    from pandas.api.types import PeriodDtype
    if isinstance(df['QSO_DATE'].dtype, PeriodDtype):
        df['QSO_DATE'] = df['QSO_DATE'].dt.to_timestamp()
    else:
        df['QSO_DATE'] = pd.to_datetime(df['QSO_DATE'])
    df['QSO_MONTH'] = df['QSO_DATE'].dt.to_period('M').dt.to_timestamp()
    grouped = df.groupby(['QSO_MONTH', 'BAND']).size().unstack(fill_value=0)
    grouped = grouped.reset_index()
    # grouped['QSO_MONTH'] = grouped['QSO_MONTH'].astype(str)
    grouped['QSO_MONTH'] = grouped['QSO_MONTH'].dt.strftime('%Y-%m')

    fig, ax = plt.subplots(figsize=(12, 6))
    bands = [col for col in grouped.columns if col != 'QSO_MONTH']
    grouped.plot(x='QSO_MONTH', y=bands, kind='bar', stacked=True, ax=ax)

    plt.title('Monthly QSO by Band')
    plt.xlabel('Month')
    plt.ylabel('Number of QSO')
    plt.xticks(rotation=90)
    plt.grid(axis='y')
    ax.set_axisbelow(True)
    plt.legend(title='Band', loc='upper right')

    # 各バーの上に合計値を表示
    for idx, row in grouped.iterrows():
        total = sum([row[band] for band in bands])
        if len(grouped) < 24:
            text_rotation = 0
        else:
            text_rotation = 90
        ax.text(idx, total + 1, str(int(total)), ha='center', va='bottom', size='small', rotation=text_rotation)

    plt.subplots_adjust(left=0.08, right=0.98, bottom=0.18, top=0.93)
    plt.savefig(fname)
    plt.close()


def main():
    pass


if __name__ == '__main__':
    main()
