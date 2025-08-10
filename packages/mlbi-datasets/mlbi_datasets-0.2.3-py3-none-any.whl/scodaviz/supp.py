import time, os, copy, datetime, math, random, warnings
import anndata
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
from matplotlib import cm, colormaps
import matplotlib as mpl
from matplotlib.pyplot import figure
from matplotlib.patches import Rectangle

from importlib_resources import files

SCANVPY = True
try:
    import scanpy as sc
except ImportError:
    print('WARNING: scanpy not installed.')
    SCANVPY = False

STATANNOT = True
try:
    from statannot import add_stat_annotation
except ImportError:
    print('WARNING: statannot not installed or not available. ')
    STATANNOT = False

SEABORN = True
try:
    import seaborn as sns
except ImportError:
    print('WARNING: seaborn not installed or not available. ')
    SEABORN = False

try:
    import plotly.graph_objects as go
except ImportError:
    print('WARNING: plotly not installed.')
    

def get_sample_to_group_dict( samples, conditions ):
    
    samples = np.array(samples)
    conditions = np.array(conditions)
    
    slst = list(set(list(samples)))
    slst.sort()
    glst = []
    for s in slst:
        b = samples == s
        g = conditions[b][0]
        glst.append(g)
        
    dct = dict(zip(slst, glst))
    return dct


def get_sample_to_group_map( samples, conditions ):
    return get_sample_to_group_dict( samples, conditions )


# df_cnt, df_pct= get_population( adata_s.obs['sid'], 
#                                 adata_s.obs['minor'], sort_by = [] )
def get_population( pids, cts, sort_by = [] ):
    
    pid_lst = list(set(list(pids)))
    pid_lst.sort()
    celltype_lst = list(set(list(cts)))
    celltype_lst.sort()

    df_celltype_cnt = pd.DataFrame(index = pid_lst, columns = celltype_lst)
    df_celltype_cnt.loc[:,:] = 0

    for pid in pid_lst:
        b = np.array(pids) == pid
        ct_sel = np.array(cts)[b]

        for ct in celltype_lst:
            bx = ct_sel == ct
            df_celltype_cnt.loc[pid, ct] = np.sum(bx)

    df_celltype_pct = (df_celltype_cnt.div(df_celltype_cnt.sum(axis = 1), axis = 0)*100).astype(float)
    
    if len(sort_by) > 0:
        df_celltype_pct.sort_values(by = sort_by, inplace = True)

    return df_celltype_cnt, df_celltype_pct


def get_gene_expression( adata, items_to_plot = [], 
                         group_col = 'sample' ): 

    sample_col = group_col
    slst = adata.obs[sample_col].unique().tolist()
    slst.sort()

    if items_to_plot is None:
        Xs = adata.to_df()
        df = pd.DataFrame(index = slst, columns = adata.var.index)
    elif len(items_to_plot) == 0:
        Xs = adata.to_df()
        df = pd.DataFrame(index = slst, columns = adata.var.index)
    else:
        Xs = adata[:, items_to_plot].to_df()
        df = pd.DataFrame(index = slst, columns = items_to_plot)
        
    for s in slst:
        b = adata.obs[sample_col] == s
        mns = (Xs.loc[b,:] > 0).mean(axis = 0)
        df.loc[s,:] = list(mns)
    
    df = df.astype(float)
    return df


def cci_get_means( cci_df_dct, cci_idx_lst = None, 
                   cells = [], genes = [], pval_cutoff = 0.05 ):

    if cci_idx_lst is None:
        ## get coomon cci index
        for j, key in enumerate(cci_df_dct.keys()):
            b = cci_df_dct[key]['pval'] <= pval_cutoff
            if len(cells) > 0:
                b = b & (cci_df_dct[key]['cell_A'].isin(cells) | cci_df_dct[key]['cell_B'].isin(cells))
            if len(genes) > 0:
                b = b & (cci_df_dct[key]['gene_A'].isin(genes) | cci_df_dct[key]['gene_B'].isin(genes))
                         
            if j == 0:
                idx_union = list(cci_df_dct[key].index.values[b])
            else:
                idx_union = list(set(idx_union).union(list(cci_df_dct[key].index.values[b])))
        cci_idx_lst = idx_union
    
    tlst = cci_idx_lst
    slst = list(cci_df_dct.keys())
    
    df = pd.DataFrame(index = slst, columns = tlst)
    df.loc[:,:] = None
    
    for s in slst:
        dfv = cci_df_dct[s]
        idx = list(dfv.index.values)
        clst = list(set(tlst).intersection(idx))
        df.loc[s, clst] = dfv.loc[clst, 'mean'].astype(float)   
                
    df = df.astype(float)
    return df
    

def get_cci_means( cci_df_dct, cci_idx_lst = None, 
                   cells = [], genes = [], pval_cutoff = 0.05 ):

    return cci_get_means( cci_df_dct, cci_idx_lst, 
                          cells, genes, pval_cutoff)


def cci_get_diff_interactions( df_cci_sample, sample_group_map, 
                               ref_group = None, pval_cutoff = 0.05 ):
    df = df_cci_sample
    group = []
    for k in list(df.index.values):
        group.append( sample_group_map[k] )
    glst = list(set(group))
    glst.sort()
    group = pd.Series(group, index = df.index)
    
    df_res = pd.DataFrame(index = list(df.columns.values))
    
    if ref_group is None:
        for i, g1 in enumerate(glst):
            
            b_r = (group == g1) # & (~df[item].isnull())
            n_r = np.sum(b_r)
            if n_r > 0:
                for j, g2 in enumerate(glst):
                    if i > j:
                        b_o = (group == g2) # & (~df[item].isnull())
                        n_o = np.sum(b_o)
                        if n_o > 0:
                            res = stats.ttest_ind(df.loc[b_r,:], 
                                                  df.loc[b_o,:], axis=0, 
                                                  equal_var=False, # (n_r == n_o), 
                                                  nan_policy='omit', # 'propagate', 
                                                  permutations=None, 
                                                  random_state=None, 
                                                  alternative='two-sided', 
                                                  trim=0)
                            df_res.loc[:, '%s_vs_%s' % (g1, g2)] = res.pvalue
            
    elif ref_group in glst:
    
        b_ref = group == ref_group
        for g in glst:
            if g != ref_group:
                b_r = (group == g) # & (~df[item].isnull()) 
                n_r = np.sum(b_r)
    
                b_o = b_ref # & (~df[item].isnull())
                n_o = np.sum(b_o)
    
                res = stats.ttest_ind(df.loc[b_r,:], 
                                      df.loc[b_o,:], axis=0, 
                                      equal_var=False, # (n_r == n_o), 
                                      nan_policy='omit', # 'propagate', 
                                      permutations=None, 
                                      random_state=None, 
                                      alternative='two-sided', 
                                      trim=0)
                df_res.loc[:, '%s_vs_%s' % (g, ref_group)] = res.pvalue
    
    b = df_res.isnull()
    df_res[b] = 1
    
    pv_min = df_res.min(axis = 1)
    df_res = df_res.loc[pv_min <= pval_cutoff,:]

    df_res['ss'] = (df_res <= pval_cutoff).sum(axis = 1)
    df_res['pp'] = -np.log10(df_res.prod(axis = 1))
    df_res.sort_values(by = ['ss', 'pp'], ascending = False, inplace = True)
       
    return df_res.iloc[:,:-2]


def test_group_diff( df_sample_by_items, sample_group_map, 
                     ref_group = None, pval_cutoff = 0.05 ):
    
    return cci_get_diff_interactions( df_sample_by_items, sample_group_map, 
                               ref_group, pval_cutoff )


### Remove common CCI
def cci_remove_common( df_dct ):
    
    idx_dct = {}
    idxo_dct = {}
    celltype_lst = []

    for j, g in enumerate(df_dct.keys()):
        idx_dct[g] = list(df_dct[g].index.values)
        if j == 0:
            idx_c = idx_dct[g]
        else:
            idx_c = list(set(idx_c).intersection(idx_dct[g]))

        ctA = list(df_dct[g]['cell_A'].unique())
        ctB = list(df_dct[g]['cell_B'].unique())
        celltype_lst = list(set(celltype_lst).union(ctA + ctB))

    for g in df_dct.keys():
        idxo_dct[g] = list(set(idx_dct[g]) - set(idx_c))

    dfs_dct = {}
    for g in df_dct.keys():
        dfs_dct[g] = df_dct[g].loc[idxo_dct[g],:]

    celltype_lst.sort()
    # len(idx_c), celltype_lst
    
    return dfs_dct


## Get matrices summarizing the num CCIs for each condition
def cci_get_ni_mat( df_dct, remove_common = True ):
    
    if remove_common: 
        dfs_dct = cci_remove_common( df_dct )
    else:
        dfs_dct = df_dct
        
    celltype_lst = []
    for j, g in enumerate(dfs_dct.keys()):
        ctA = list(dfs_dct[g]['cell_A'].unique())
        ctB = list(dfs_dct[g]['cell_B'].unique())
        celltype_lst = list(set(celltype_lst).union(ctA + ctB))

    celltype_lst.sort()
    
    df_lst = {} 
    for g in dfs_dct.keys():
        b = dfs_dct[g]['cell_A'].isin(celltype_lst) & (dfs_dct[g]['cell_B'].isin(celltype_lst))
        dfs = dfs_dct[g].loc[b,:]
        df = pd.DataFrame(index = celltype_lst, columns = celltype_lst)
        df.loc[:] = 0
        for a, b in zip(dfs['cell_A'], dfs['cell_B']):
            df.loc[a,b] += 1

        df_lst[g] = df
                
    return df_lst

def get_cci_ni_mat( df_dct, remove_common = True ):
    return cci_get_ni_mat( df_dct, remove_common )


def cci_get_df_to_plot( df_dct, pval_cutoff = 0.01, mean_cutoff = 1, target_cells = None ):

    idx_lst_all = []
    for k in df_dct.keys():
        b = df_dct[k]['pval'] <= pval_cutoff
        b = b & df_dct[k]['mean'] >= mean_cutoff
        if target_cells is not None:
            if isinstance(target_cells, list):
                b1 = df_dct[k]['cell_A'].isin(target_cells)
                b2 = df_dct[k]['cell_B'].isin(target_cells)
                b = b & (b1 | b2)
                
        idx_lst_all = idx_lst_all + list(df_dct[k].index.values[b])

    idx_lst_all = list(set(idx_lst_all))
    display('Union of Interactions: %i' % len(idx_lst_all))    

    df_dct_to_plot = {}
    for k in df_dct.keys():
        df = df_dct[k]
        dfv = pd.DataFrame(index = idx_lst_all, columns = df.columns)
        dfv['mean'] = 0
        dfv['pval'] = 1

        idxt = list(set(idx_lst_all).intersection(list(df.index.values)))
        cols = list(df.columns.values)
        cols.remove('mean')
        cols.remove('pval')
        dfv.loc[idxt, cols] = df.loc[idxt, cols]
        dfv.loc[idxt, 'mean'] = df.loc[idxt, 'mean']
        dfv.loc[idxt, 'pval'] = df.loc[idxt, 'pval']

        gp, cp, ga, gb, ca, cb = [], [], [], [], [], []
        for s in list(dfv.index.values):
            gpt, cpt, gat, gbt, cat, cbt = cpdb_get_gp_n_cp(s)

            gp = gp + [gpt]
            cp = cp + [cpt]
            ga = ga + [gat]
            gb = gb + [gbt]
            ca = ca + [cat]
            cb = cb + [cbt]

        dfv['gene_pair'] = gp
        dfv['cell_pair'] = cp
        dfv['gene_A'] = ga
        dfv['gene_B'] = gb
        dfv['cell_A'] = ca
        dfv['cell_B'] = cb
        
        df_dct_to_plot[k] = dfv
        # print(dfv.shape)
        
    return df_dct_to_plot


def get_markers_from_deg( df_dct, ref_col = 'score',  N_mkrs = 30, 
                          nz_pct_test_min = 0.5, nz_pct_ref_max = 0.1,
                          rem_common = True ):
## Get markers from DEG results

    df_deg = df_dct
    mkr_dict = {}
    b = True
    for key in df_deg.keys():
        if ref_col not in list(df_deg[key].columns.values):
            b = False
            break
    
    if not b:
        print('ERROR: %s not found in column name of DEG results.' % ref_col)
        return None

    for key in df_deg.keys():

        g = key.split('_')[0]
        df = df_deg[key].copy(deep = True)
        b1 = df['nz_pct_test'] >= nz_pct_test_min
        b2 = df['nz_pct_ref'] <= nz_pct_ref_max
        df = df.loc[b1&b2, : ]
        df = df.sort_values([ref_col], ascending = False)

        mkr_dict[g] = list(df.iloc[:N_mkrs].index.values)

    ## Remove common markers
    if rem_common:
        lst = list(mkr_dict.keys())
        cmm = []
        for j, k1 in enumerate(lst):
            for i, k2 in enumerate(lst):
                if (k1 != k2) & (j < i):
                    lc = list(set(mkr_dict[k1]).intersection(mkr_dict[k2]))
                    cmm = cmm + lc
        cmm = list(set(cmm))

        for j, k in enumerate(lst):
            mkr_dict[k] = list(set(mkr_dict[k]) - set(cmm))

    return mkr_dict


def filter_gsa_result( dct, neg_log_p_cutoff ):
    
    dct_t = {}
    for kk in dct.keys():
        dft = dct[kk]
        b = dft['-log(p-val)'] >= neg_log_p_cutoff
        dct_t[kk] = dft.loc[b,:]
    return dct_t
