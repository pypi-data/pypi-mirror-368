# [[file:../Files/input_files.org::*Code for constructing inputs to CFEDemands from *.dta files][Code for constructing inputs to CFEDemands from *.dta files:1]]
# Tangled on Mon Aug 11 07:17:25 2025
import numpy as np
import pandas as pd
from collections import defaultdict

try:  # If we can't load dvc, take a pass and fail only if we call.
    import dvc.api
except ModuleNotFoundError:
    pass

def construct_df(VARS,INDICES,convert_categoricals=False,dvcstream=False,label_mappings=None):
    """
    Compile data on a collection of variables from one or more Stata
    =dta= or =csv= files into a single pandas DataFrame.

    Ethan Ligon                                         February 2020

    """

    def construct_column(df,Mapping):
        try:
            return df[Mapping]
        except KeyError:
            return df.apply(eval(Mapping),axis=1)

    def read_and_index(fn,indices,dvcstream=dvcstream,encoding=None):
        if dvcstream:
            try:
                with dvc.api.open(fn,mode='rb') as f:
                    if fn.split('.')[-1]=='dta':
                        df = pd.read_stata(f,convert_categoricals=convert_categoricals).rename(columns=dict(map(reversed, indices.items())))
                    elif fn.split('.')[-1]=='csv':
                        df = pd.read_csv(f,encoding=encoding).rename(columns=dict(map(reversed, indices.items())))
            except UnicodeDecodeError:
                return read_and_index(fn,indices,dvcstream=dvcstream,encoding='latin-1')
        else:
            if fn.split('.')[-1]=='dta':
                df = pd.read_stata(fn,convert_categoricals=convert_categoricals).rename(columns=dict(map(reversed, indices.items())))
            elif fn.split('.')[-1]=='csv':
                df = pd.read_csv(fn,encoding=None).rename(columns=dict(map(reversed, indices.items())))

        df['t'] = indices['t']

        for index in indices.keys(): # Cast to simplest type (int or str)
            try:
                df[index] = df[index].astype(int)
            except ValueError:
                df[index] = df[index].astype(str)
        df.set_index(list(indices.keys()),inplace=True)
        return df

    DFs = defaultdict(list)
    file_groups = INDICES.groupby('File')
    for group in VARS.groupby(['t','File']):
        fn = group[0][1]
        mydf = read_and_index(group[0][1],INDICES.loc[fn].to_dict())
        d = {}
        for v in group[1].itertuples():
            d[v.Output] = construct_column(mydf,v.Mapping)
            try:
                idx,op = eval(v.Grouping)
                groups = d[v.Output].groupby(INDICES.columns) #[idx,'t'])
                if op == sum:
                    d[v.Output] = groups.sum()
                else:
                    d[v.Output] = groups.apply(op)
            except (ValueError,TypeError): pass

        DFs[group[0][0]].append(pd.DataFrame(d))

    by_year = []
    for t in DFs.keys():
        df_for_year = pd.concat(DFs[t],join='inner',axis=1)
        assert not any(df_for_year.columns.duplicated()), "Duplicate output columns not allowed; t=%s." % t
        if label_mappings is not None:
            df_for_year = df_for_year.rename(index={int(k):v for k,v in label_mappings[t].items()},level='i')
        by_year.append(df_for_year)
    
    df = pd.concat(by_year,axis=0)
    return df
# Code for constructing inputs to CFEDemands from *.dta files:1 ends here
