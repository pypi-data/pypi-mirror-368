def get_table_seasonality(df, index_name):
    df = df[df.index==index_name]
    df = df.T
    df['year'] = df.index.map(lambda x: x.split('-')[0])
    df['month'] = df.index.map(lambda x: x.split('-')[1])
    df = df.pivot(index='year', columns='month', values=df.columns[0]).dropna(axis=0, how='all')
    df.loc['average: month', :] = df.mean(axis=0)
    df.loc[:, 'average: year'] = df.mean(axis=1)
    return df
