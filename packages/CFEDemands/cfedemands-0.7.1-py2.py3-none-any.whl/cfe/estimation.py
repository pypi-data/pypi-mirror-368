# [[file:../Empirics/cfe_estimation.org::agg_shares_and_mean_shares][agg_shares_and_mean_shares]]
# Tangled on Mon Aug 11 07:17:23 2025
#name: agg_shares_and_mean_shares

import pylab as pl
import pandas as pd
import numpy as np
from cfe.df_utils import broadcast_binary_op, is_none
from itertools import cycle

def expenditure_shares(df):

    df.fillna(0,inplace=True)
    aggshares=df.groupby(level='t').sum()
    aggshares=aggshares.div(aggshares.sum(axis=1),axis=0).T
    meanshares=df.div(df.sum(axis=1),level='j',axis=0).groupby(level='t').mean().T

    mratio=(np.log(aggshares)-np.log(meanshares))
    sharesdf={'Mean shares':meanshares,'Agg. shares':aggshares}

    return sharesdf,mratio

def agg_shares_and_mean_shares(df,figname=None,ConfidenceIntervals=False,ax=None,VERTICAL=False,CycleMarkers=False,sort='first'):
    """Figure of log agg shares - log mean shares.

    Required argument is a pd.DataFrame of expenditures, indexed by (t,j).

    Optional arguments
    ------------------
    figname : string; default None.
        If supplied, will save figure to file named figname.

    ConfidenceIntervals : Boolean or float in (0,1);  default False.
        If True, the returned figure will have 95% confidence intervals.
        If in (0,1) that will be used for the size of the confidence interval instead.

    ax : matplotlib.Axes object; default None.
        If supplied, will draw figure on existing Axes object.

    VERTICAL : Boolean or scalar; default False.
        If True or non-zero scalar produce figure with expenditures arranged in vertical list.
        If non-zero scalar used to control vertical spacing of figure.

    sort : 'first' or 'average', default 'first'.
        If 'first' use aggregate shares from first year to sort;
        otherwise use average (across years) aggregate shares.
    """

    if CycleMarkers:
        markers = cycle(["-o","-v","-^","-<","->","-*","-+","-d"])
    else:
        markers = cycle(["-o"])

    shares,mratio=expenditure_shares(df)
    meanshares=shares['Mean shares']

    tab = pd.concat(shares,axis=1)

    tab.columns.names = ['l','t']

    if sort.lower() == 'first':
        tab['sort'] = tab[('Agg. shares',meanshares.columns[0])]
    elif sort.lower() == 'average':
        tab['sort'] = tab.groupby('l',axis=1).mean()['Agg. shares']
    else:
        raise ValueError("Invalid sort option")

    tab.sort_values(by='sort',ascending=False,inplace=True)
    tab = tab.drop('sort',axis=1)

    if ax is None:
        fig, ax = pl.subplots()

    mratio.sort_values(by=mratio.columns[0],inplace=True)

    if VERTICAL:
        if VERTICAL is not True: # Numeric value supplied
            vertical_scale=VERTICAL
        else:
            vertical_scale=6.
        for i in mratio.columns:
            ax.plot(mratio[i].values, list(range(mratio.shape[0])), next(markers))
        ax.legend(mratio.columns,loc=2,fontsize='small')
        ax.set_xlabel('Log Aggregate shares divided by Mean shares')
        ax.set_yticks(list(range(mratio.shape[0])))
        ax.set_yticklabels(mratio.index.values.tolist(),rotation=0,size='small')
        ax.axvline()
        v = ax.axis()
        ax.figure.set_figheight((v[-1]/24)*vertical_scale)
        pl.tight_layout()
    else:
        for i in mratio.columns:
            ax.plot(list(range(mratio.shape[0])), mratio[i].values, next(markers))
        ax.legend(mratio.columns,loc=2,fontsize='small')
        ax.set_ylabel('Log Aggregate shares divided by Mean shares')

        v=ax.axis()

        if  len(mratio)>=12:
            i=0
            for i in range(len(mratio)):
                name=mratio.index[i] # label of expenditure item

                if mratio.iloc[i,0]>0.2:
                    #pl.text(i,mratio.T.iloc[0][name],name,fontsize='xx-small',ha='right')

                    # The key option here is `bbox`.
                    ax.annotate(name, xy=(i,mratio.T.iloc[0][name]), xytext=(-20,10),
                                textcoords='offset points', ha='right', va='bottom',
                                bbox=dict(boxstyle='round,pad=0.2', fc='yellow', alpha=0.3),
                                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.25',
                                color='red'),fontsize='xx-small')

                if mratio.iloc[i,0] < -0.2:
                    #pl.text(i,mratio.T.iloc[0][name],name,fontsize='xx-small')
                    ax.annotate(name, xy=(i,mratio.T.iloc[0][name]), xytext=(20,-10),
                                textcoords='offset points', ha='left', va='top',
                                bbox=dict(boxstyle='round,pad=0.2', fc='yellow', alpha=0.3),
                                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.25',
                                color='red'),fontsize='xx-small')
        else: #Put labels on xaxis
            ax.set_xticklabels(mratio.index.values.tolist(),rotation=45)

        ax.axhline()



    if ConfidenceIntervals>0: # Bootstrap some confidence intervals
        if ConfidenceIntervals==1: ConfidenceIntervals=0.95
        current=0
        last=1
        M=np.array([],ndmin=3).reshape((mratio.shape[0],mratio.shape[1],0))
        i=0
        mydf=df.loc[:,mratio.index]
        while np.max(np.abs(current-last))>0.001 or i < 1000:
            last=current
            # Sample households in each  round with replacement
            bootdf=mydf.iloc[np.random.randint(0,df.shape[0],df.shape[0]),:]
            bootdf.reset_index(inplace=True)
            bootdf.loc[:,'j']=list(range(bootdf.shape[0]))
            bootdf.set_index(['t','j'],inplace=True)
            shares,mr=expenditure_shares(bootdf)
            M=np.dstack((M,mr.values))
            M.sort(axis=2)
            a = (1-ConfidenceIntervals)/2.
            lb = mratio.values - M[:,:,int(np.floor(M.shape[-1]*a))]
            ub=M[:,:,int(np.floor(M.shape[-1]*(ConfidenceIntervals+a)))] - mratio.values
            current=np.c_[lb,ub]
            i+=1

        T=mratio.shape[1]
        for t in range(T):
            if VERTICAL:
                ax.errorbar(mratio.values[:,t],np.arange(mratio.shape[0]),xerr=current[:,[t,t-T]].T.tolist())
            else:
                ax.errorbar(np.arange(mratio.shape[0]),mratio.values[:,t],yerr=current[:,[t,t-T]].T.tolist())

            tab[(df.index.levels[0][t],'Upper Int')]=current[:,t-T]
            tab[(df.index.levels[0][t],'Lower Int')]=current[:,t]

    if figname:
        pl.savefig(figname)

    return tab,ax
# agg_shares_and_mean_shares ends here

# [[file:../Empirics/cfe_estimation.org::group_expenditures][group_expenditures]]
# Tangled on Mon Aug 11 07:17:23 2025
#name: group_expenditures
def group_expenditures(df,groups):
    myX=pd.DataFrame(index=df.index)
    for k,v in groups.items():
        if len(k):
            myv = [int(i) for i in v if len(str(i))>0]
            try:
                myX[k]=df[['$x_{%d}$' % int(i) for i in myv]].sum(axis=1)
            except KeyError: pass

    return myX
# group_expenditures ends here

# [[file:../Empirics/cfe_estimation.org::svd_rank1_approximation_with_missing_data][svd_rank1_approximation_with_missing_data]]
# Tangled on Mon Aug 11 07:17:23 2025
#name: svd_rank1_approximation_with_missing_data
import pandas as pd
#name: svd_missing

import numpy as np
import warnings

def missing_inner_product(X,min_obs=None):
    """Compute inner product X.T@X, allowing for possibility of missing data."""
    n,m=X.shape

    if n<m:
        axis=1
        N=m
    else:
        axis=0
        N=n

    xbar=X.mean(axis=axis)

    if axis:
        C=(N-1)*X.T.cov(min_periods=min_obs)
    else:
        C=(N-1)*X.cov(min_periods=min_obs)

    return C + N*np.outer(xbar,xbar)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    def unit_vector(vector):
        """ Returns the unit vector of the vector.  """
        return vector / np.linalg.norm(vector)

    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def drop_columns_wo_covariance(X,min_obs=2,VERBOSE=False):
    """Drop columns from pd.DataFrame that lead to missing elements of covariance matrix."""

    m,n=X.shape
    assert m>n, "Fewer rows than columns.  Consider passing the transpose."

    # If good has fewer total observations than min_obs, can't possibly
    # have more cross-products.  Dropping here is faster than iterative procedure below.
    X = X.loc[:,X.count()>=min_obs]

    HasMiss=True
    while HasMiss:
        foo = X.cov(min_periods=min_obs).count()
        if np.sum(foo<X.shape[1]):
            badcol=foo.idxmin()
            del X[badcol] # Drop  good with  most missing covariances
            if VERBOSE: print("Dropping %s, with only %d covariances." % (badcol,foo[badcol]))
        else:
            HasMiss=False

    return X

def heteropca(C,r=1,max_its=50,tol=1e-3,verbose=False):
    """Estimate r factors and factor weights of covariance matrix C."""
    from scipy.spatial import procrustes

    N = C - np.diag(np.diag(C))

    ulast = np.zeros((N.shape[1],r))
    u = np.zeros((N.shape[1],r))
    u[0,0] = 1
    ulast[-1,0] = 1

    t = 0

    # We only get nice estimates of u, not singular values.
    # Use sine of angle between estimates of u for convergence criterion.

    #while np.abs(np.sin(angle_between(u[:,0],ulast[:,0]))) >tol and t<max_its:
    while procrustes(u,ulast)[-1] >tol and t<max_its:
        ulast = u

        u,s,vt = np.linalg.svd(N,full_matrices=False,hermitian=True)

        s = s[:r]
        u = u[:,:r]

        Ntilde = u[:,:r]@np.diag(s[:r])@vt[:r,:]

        N = N - np.diag(np.diag(N)) + np.diag(np.diag(Ntilde))

        t += 1

        if t==max_its:
            warnings.warn("Exceeded maximum iterations (%d)" % max_its)
        if verbose: print(f"Iteration {t}, u[0,:r]={u[0,:r]}.")


    return u,s

def svd_missing(A,max_rank=None,min_obs=None,heteroskedastic=False,verbose=False):
    """Singular Value Decomposition with missing values

    Returns matrices U,S,V.T, where A~=U*S*V.T.

    Inputs:
        - A :: matrix or pd.DataFrame, with NaNs for missing data.

        - max_rank :: Truncates the rank of the representation.  Note
                      that this impacts which rows of V will be
                      computed; each row must have at least max_rank
                      non-missing values.  If not supplied rank may be
                      truncated using the Kaiser criterion.

        - min_obs :: Smallest number of non-missing observations for a
                     row of U to be computed.

        - heteroskedastic :: If true, use the "heteroPCA" algorithm
                       developed by Zhang-Cai-Wu (2018) which offers a
                       correction to the svd in the case of
                       heteroskedastic errors.  If supplied as a pair,
                       heteroskedastic[0] gives a maximum number of
                       iterations, while heteroskedastic[1] gives a
                       tolerance for convergence of the algorithm.

    Ethan Ligon                                        September 2021

    """
    # Defaults; modify by passing a tuple to heteroskedastic argument.
    max_its=50
    tol = 1e-3

    P=missing_inner_product(A,min_obs=min_obs) # P = A.T@A

    sigmas,u=np.linalg.eigh(P)

    order=np.argsort(-sigmas)
    sigmas=sigmas[order]

    # Truncate rank of representation using Kaiser criterion (positive eigenvalues)
    u=u[:,order]
    u=u[:,sigmas>0]
    s=np.sqrt(sigmas[sigmas>0])

    if max_rank is not None and len(s) > max_rank:
        u=u[:,:max_rank]
        s=s[:max_rank]

    r=len(s)

    if heteroskedastic: # Interpret tuple
        try:
            max_its,tol = heteroskedastic
        except TypeError:
            pass

        u,s = heteropca(P,r=r,max_its=max_its,tol=tol,verbose=verbose)

    if A.shape[0]==A.shape[1]: # Symmetric; v=u
        return u,s,u.T
    else:
        us=u@np.diag(s)

        v=np.zeros((len(s),A.shape[1]))
        for j in range(A.shape[1]):
            a=A.iloc[:,j].values.reshape((-1,1))
            x=np.nonzero(~np.isnan(a))[0] # non-missing elements of vector a
            if len(x)>=r:
                v[:,j]=(np.linalg.pinv(us[x,:])@a[x]).reshape(-1)
            else:
                v[:,j]=np.nan

    return u,s,v.T

def svd_rank1_approximation_with_missing_data(x,return_usv=False,max_rank=1,
                                              min_obs=None,VERBOSE=True):
    """
    Return rank 1 approximation to a pd.DataFrame x, where x may have
    elements which are missing.
    """
    x=x.copy()
    m,n=x.shape

    if min_obs is None: min_obs = 1

    if n<m:  # If matrix 'thin', make it 'short'
        x=x.T
        TRANSPOSE=True
    else:
        TRANSPOSE=False

    x=x.dropna(how='all',axis=1) # Drop any column which is /all/ missing.
    x=x.dropna(how='all',axis=0) # Drop any row which is /all/ missing.

    x=drop_columns_wo_covariance(x.T,min_obs=min_obs).T
    u,s,v = svd_missing(x,max_rank=max_rank,min_obs=min_obs)
    if VERBOSE:
        print("Estimated singular values: ",)
        print(s)

    xhat=pd.DataFrame(s*v@u.T,columns=x.index,index=x.columns).T

    if TRANSPOSE:
        out = xhat.T
    else:
        out = xhat

    if return_usv:
        u = u.squeeze()
        if u.shape[0] == xhat.shape[1]:
            u = pd.Series(u.squeeze(),index=xhat.columns)
            v = pd.Series(v.squeeze(),index=xhat.index)
        elif u.shape[0] == xhat.shape[0]:
            u = pd.Series(u.squeeze(),index=xhat.index)
            v = pd.Series(v.squeeze(),index=xhat.columns)
        if TRANSPOSE:
            out = (out,v,s,u)
        else:
            out = (out,u,s,v)

    return out
# svd_rank1_approximation_with_missing_data ends here

# [[file:../Empirics/cfe_estimation.org::estimate_reduced_form][estimate_reduced_form]]
# Tangled on Mon Aug 11 07:17:23 2025
#name: estimate_reduced_form
import pandas as pd
import warnings
import sys
from collections import OrderedDict
from cfe.df_utils import drop_missing, ols, arellano_robust_cov, broadcast_binary_op, use_indices, df_norm

def estimate_reduced_form(y,z,return_v=False,return_se=False,VERBOSE=False):
  """Estimate reduced-form Frisch expenditure/demand system.

  Inputs:
      - y : pd.DataFrame of log expenditures or log quantities, indexed by (j,t,m),
            where j indexes the household, t the period, and m the market.
            Columns are different expenditure items, indexed by i.

      - z : pd.DataFrame of household characteristics; index should match that of y.
            Columns are different characteristics, indexed by l.

  Outputs:
      - a : Estimated good-time-market fixed effects.

      - ce : Residuals (can be provided as an input to get_log_lambdas()).

      - d : Estimated coefficients associated with characteristics z.

      - sed : (Optional, if return_se) Estimated standard errors for coefficients d.

      - sea : (Optional, if return_se) Estimated standard errors for coefficients a.

      - V : (Optional, if return_v) Estimated covariance matrix of coefficients d.

  Ethan Ligon                                            February 2017
  """
  try: # Be a little forgiving if t or m index is missing.
      assert y.index.names==['j','t','m'], "Indices should be (j,t,m)?"
      assert y.columns.name == 'i', "Name of column index should be i?"
  except AssertionError:
      y = y.reset_index()
      if not 'm' in y.columns: y['m']=1
      if not 't' in y.columns: y['t']=1
      y = y.set_index(['j','t','m'])
      y.columns.set_names('i',inplace=True)

  try:
      assert z.index.names==['j','t','m'], "Indices should be (j,t,m)?"
      assert z.columns.name == 'k', "Name of column index should be k?"
  except AssertionError:
      z = z.reset_index()
      if not 'm' in z.columns: z['m']=1
      if not 't' in z.columns: z['t']=1
      z = z.set_index(['j','t','m'])

      z.columns.set_names('k',inplace=True)

  assert len(z.index.intersection(y.index))>0, "Indices of z & y don't match."

  periods = list(set(y.index.get_level_values('t')))
  ms = list(set(y.index.get_level_values('m')))

  # Time-market dummies
  DateLocD = use_indices(y,['t','m'])
  DateLocD = pd.get_dummies(list(zip(DateLocD['t'],DateLocD['m'])))
  DateLocD.index = y.index

  sed = pd.DataFrame(columns=y.columns)
  sea = pd.DataFrame(columns=y.columns)
  a = pd.Series(index=y.columns,dtype=float)
  b = OrderedDict()
  d = OrderedDict()
  ce = pd.DataFrame(index=y.index,columns=y.columns)
  V = OrderedDict()

  for i,Item in enumerate(y.columns):
      if VERBOSE: print(Item)

      lhs,rhs=drop_missing([y.iloc[:,[i]],pd.concat([z,DateLocD],axis=1)])
      stdev = rhs.std()
      for constant in stdev[stdev==0].index.tolist():
          warnings.warn("No variation in: %s" % str(constant))
      rhs=rhs.loc[:,rhs.std()>0] # Drop  any X cols with no variation
      useDateLocs=list(set(DateLocD.columns.tolist()).intersection(rhs.columns.tolist()))

      # Calculate deviations
      lhsbar=lhs.mean(axis=0)
      assert ~np.any(np.isnan(lhsbar)), "Missing data in lhs for item %s." % Item
      assert np.all(lhs.std()>0), "No variation in non-missing data for item %s." % Item
      lhs=lhs-lhsbar
      lhs=lhs-lhs.mean(axis=0)

      rhsbar=rhs.mean(axis=0)
      assert ~np.any(np.isnan(rhsbar)), "Missing data in rhs?"
      rhs=rhs-rhsbar
      rhs=rhs-rhs.mean(axis=0)

      # Need to make sure time-market effects sum to zero; add
      # constraints to estimate restricted least squares
      ynil=pd.DataFrame([0],index=[(-1,0,0)],columns=lhs.columns)
      znil=pd.DataFrame([[0]*z.shape[1]],index=[(-1,0,0)],columns=z.columns)
      timednil=pd.DataFrame([[1]*DateLocD.shape[1]],index=[(-1,0,0)],columns=DateLocD.columns)

      # change append to concat: X=rhs.append(znil.join(timednil))
      X=pd.concat([rhs, znil.join(timednil)])
      X=X.loc[:,X.std()>0] # Drop  any X cols with no variation

      # Estimate d & b
      # change append to concat: lhs.append(ynil)
      myb,mye=ols(X,pd.concat([lhs, ynil]) ,return_se=False,return_v=False,return_e=True)
      ce[Item]=mye.iloc[:-1,:] # Drop constraint that sums time-effects to zero

      if return_v or return_se:
          if z.shape[1]:
              V[Item]=arellano_robust_cov(z,ce[Item])
              sed[Item]=pd.Series(np.sqrt(np.diag(V[Item])), index=z.columns) # reduced form se on characteristics

              stderrs = (mye.groupby(['t','m']).std()/np.sqrt(mye.groupby(['t','m']).count()))
              if len(useDateLocs) > 0:
                  sea[Item] = stderrs.squeeze()
              else:
                  sea[Item] = stderrs[Item]

      zvars = z.columns.intersection(myb.index)
      d[Item]= myb.loc[zvars].squeeze() # reduced form coefficients on characteristics

      b[Item] = myb.loc[useDateLocs].squeeze()  # Terms involving prices
      a[Item] = lhsbar.mean() - d[Item].squeeze().dot(rhsbar[zvars]) - np.array(b[Item]).dot(rhsbar[useDateLocs])

  b = pd.DataFrame(b,index=y.groupby(level=['t','m']).mean().index)
  b = b.T
  sed = sed.T
  sea = sea.T

  if b.shape[1]==1: # Only a single time-market
    assert np.all(np.isnan(b)), "Only one good-time effect should mean b not identified"
    b[:]=0

  d = pd.DataFrame(d).T
  d.index.name = 'i'

  out = [b.add(a,axis=0),ce,d]
  if return_se:
      out += [sed,sea]
  if return_v:
      V = xr.Dataset(V).to_array(dim='i')
      out += [V]
  return out
# estimate_reduced_form ends here

# [[file:../Empirics/cfe_estimation.org::get_loglambdas][get_loglambdas]]
# Tangled on Mon Aug 11 07:17:24 2025
#name: get_loglambdas

import pandas as pd

try:
    from joblib import Parallel, delayed
    #import timeit
    PARALLEL=True
except ImportError:
    PARALLEL=False
    #warnings.warn("Install joblib for parallel bootstrap.")

PARALLEL = False # Not yet working.

def get_loglambdas(e,TEST=False,time_index='t',max_rank=1,min_obs=None,VERBOSE=False):
    """
    Use singular-value decomposition to compute loglambdas and price elasticities,
    up to an unknown factor of proportionality phi.

    Input e is the residual from a regression of log expenditures purged
    of the effects of prices and household characteristics.   The residuals
    should be arranged as a matrix, with columns corresponding to goods.
    """

    assert e.shape[0]>e.shape[1], "More goods than observations."

    chat = svd_rank1_approximation_with_missing_data(e,VERBOSE=VERBOSE,max_rank=max_rank,min_obs=min_obs)

    R2 = chat.var()/e.var()

    # Possible that initial elasticity b_i is negative, if inferior goods permitted.
    # But they must be positive on average.
    if chat.iloc[0,:].mean()>0:
        b=chat.iloc[0,:]
    else:
        b=-chat.iloc[0,:]

    loglambdas=(-chat.iloc[:,0]/b.iloc[0])

    # Find phi that normalizes first round loglambdas
    phi=loglambdas.groupby(level=time_index).std().iloc[0]
    loglambdas=loglambdas/phi

    loglambdas=pd.Series(loglambdas,name='loglambda')
    bphi=pd.Series(b*phi,index=e.columns,name=r'\phi\beta')

    if TEST:
        foo=pd.DataFrame(-np.outer(bphi,loglambdas).T,index=loglambdas.index,columns=bphi.index)
        assert df_norm(foo-chat)<1e-4
        #print("blogL norm: %f" % np.linalg.norm(foo-chat))

    return bphi,loglambdas

def iqr(x):
    """The interquartile range of a pd.Series of observations x."""
    q=x.quantile([0.25,0.75])

    try:
        return q.diff().iloc[1]
    except AttributeError:
        return np.nan

def bootstrap_elasticity_stderrs(e,clusterby=['t','m'],tol=1e-2,minits=30,return_v=False,return_samples=False,VERBOSE=False,outfn=None,TRIM=True):
    """Bootstrap estimates of standard errors for \\phi\\beta.

    Takes pd.DataFrame of residuals as input.

    Default is to `cluster' by (t,m) via a block bootstrap.

    If optional parameter TRIM is True, then calculations are
    performed using the interquartile range (IQR) instead of the
    standard deviation, with the standard deviation computed as
    IQR*0.7416 (which is a good approximation provided the
    distribution is normal).

    Ethan Ligon                              January 2017
    """

    def resample(e):
        #e = e.iloc[np.random.random_integers(0,e.shape[0]-1,size=e.shape[0]),:]
        e = e.iloc[np.random.randint(0,e.shape[0],size=e.shape[0]),:]
        e = e - e.mean()
        return e

    def new_draw(e,clusterby):
        if clusterby:
            S=e.reset_index().groupby(clusterby,as_index=True)[e.columns].apply(resample)
        else:
            S=resample(e)

        bs,ls=get_loglambdas(S)

        return bs

    if outfn: outf=open(outfn,'a')

    delta=1.
    old = pd.Series([1]*e.shape[1])
    new = pd.Series([0]*e.shape[1])
    i=0
    chunksize=2

    assert chunksize>=2, "chunksize must be 2 or more."
    while delta>tol or i < minits:
        delta=np.nanmax(np.abs(old.values.reshape(-1)-new.values.reshape(-1)))
        if VERBOSE and i>chunksize:
            stat = np.nanmax(np.abs((std0.values.reshape(-1)-std1.values.reshape(-1))/std0.values.reshape(-1)))
            print("Draws %d, delta=%5.4f.  Measure of non-normality %6.5f." % (i, delta, stat))
        old=new

        if PARALLEL:
            #start=timeit.timeit()
            bees = Parallel(n_jobs=chunksize)(delayed(new_draw)(e,clusterby) for chunk in range(chunksize))
            #print(timeit.timeit() - start)
        else:
            #start=timeit.timeit()
            bees = [new_draw(e,clusterby) for chunk in range(chunksize)]
            #print(timeit.timeit() - start)

        if outfn:
            for bs in bees:
                if np.any(np.isnan(bs)):
                    warnings.warn("Resampling draw with no data?")
                outf.write(','.join(['%6.5f' % b for b in bs])+'\n')

        try:
            B=B.append(bees,ignore_index=True)
        except NameError:
            B=pd.DataFrame(bees,index=range(chunksize)) # Create B

        i+=chunksize

        std0=B.std()
        std1=B.apply(iqr)*0.7416 # Estimate of standard deviation, with trimming
        if TRIM:
            new=std1
        else:
            new=std0

    if outfn: outf.close()

    out = [new]
    if return_samples:
        B.dropna(how='all',axis=1,inplace=True) # Drop any goods always missing estimate
        out += [B]

    if return_v:
        B.dropna(how='all',axis=1,inplace=True) # Drop any goods always missing estimate
        out += [B.cov()]

    if len(out)==1:
        return out[0]
    else:
        return out
# get_loglambdas ends here

# [[file:../Empirics/cfe_estimation.org::direct_price_elasticities][direct_price_elasticities]]
# Tangled on Mon Aug 11 07:17:24 2025
#name: direct_price_elasticities

def direct_price_elasticities(y,p,z,VERBOSE=True,return_se=False,return_v=False):
    """Estimate reduced-form Frisch expenditure/demand system.

       Inputs:
         - y : pd.DataFrame of log expenditures or log quantities, indexed by (j,t,m),
               where j indexes the household, t the period, and m the market.
               Columns are different expenditure items.

         - p : pd.DataFrame of log prices, indexed by (t,m), with
               prices for different goods across columns.

         - z : pd.DataFrame of household characteristics; index should match that of y.


      Ethan Ligon                                            March 2017
    """
    assert(y.index.names==['j','t','m'])
    assert(z.index.names==['j','t','m'])

    periods = list(set(y.index.get_level_values('t')))
    ms = list(set(y.index.get_level_values('m')))
    sed = pd.DataFrame(columns=y.columns)
    sea = pd.DataFrame(columns=y.columns)
    a = pd.Series(index=y.columns,dtype=float)
    b = OrderedDict() #pd.DataFrame(index=y.columns)
    d = OrderedDict() #pd.DataFrame(index=y.columns,columns=z.columns).T
    ce = pd.DataFrame(index=y.index,columns=y.columns)
    V = pd.Panel(items=y.columns,major_axis=z.columns,minor_axis=z.columns)

    for i,Item in enumerate(y.columns):
        if VERBOSE: print(Item)
        if np.any(np.isnan(p[Item])): continue # Don't estimate with missing prices

        rhs = z.reset_index('j').join(p[Item]).reset_index().set_index(['j','t','m'])
        rhs.rename(columns={Item:'log p'},inplace=True)

        lhs,rhs=drop_missing([y.iloc[:,[i]],rhs])

        rhs['Constant']=1

        myb,mye=ols(rhs,lhs,return_se=False,return_v=False,return_e=True)
        ce[Item]=mye

        if return_v or return_se:
            V[Item]=arellano_robust_cov(rhs,mye)
            sed[Item]=pd.Series(np.sqrt(np.diag(V[Item])), index=z.columns) # reduced form se on characteristics

        d[Item]=myb[z.columns] # reduced form coefficients on characteristics

        a[Item] = myb['Constant']
        b[Item] = myb['log p'].values[0]

    b = pd.Series(b)

    d = pd.concat(d.values())

    out = [a,b,ce,d]
    if return_se:
        out += [sed]
    if return_v:
        out += [V]
    return out
# direct_price_elasticities ends here

# [[file:../Empirics/cfe_estimation.org::*Indirect estimation of price elasticities][Indirect estimation of price elasticities:1]]
# Tangled on Mon Aug 11 07:17:24 2025
def indirect_price_elasticities(a,p,zbar):
    """Estimate reduced-form Frisch expenditure/demand system.

       Inputs:
         - a : pd.DataFrame of good-time-market effects estimated by =estimate_reduced_form=,
               indexed by (t,m), where t indexes the period, and m the market.
               Columns are different expenditure items.

         - p : pd.DataFrame of log prices, indexed by (t,m), with
               prices for different goods across columns.

         - zbar : pd.DataFrame of average household characteristics; index should match that of a.

      Ethan Ligon                                            March 2017
    """
    assert(a.index.names==['t','m'])
    assert(zbar.index.names==['t','m'])

    # Filter p
    X=zbar.copy()
    X['Constant'] = 1
    y = p.dropna(how='any',axis=1)

    # pe are filtered log prices
    bp,pe = ols(X,y,return_se=False,return_e=True)

    X = pe.copy()

    Xm = (X-X.mean()).values

    ym = (a-a.mean()).values

    B=OrderedDict()
    SE=OrderedDict()
    for i,Item in enumerate(y.columns):
        B[Item] = np.linalg.lstsq(Xm[:,i],ym[:,i])[0][0,0]
        e = ym[:,i] - Xm[:,i]@B[Item]
        SE[Item] = np.sqrt(np.var(e)/np.var(Xm[:,i]))

    B = pd.Series(B)
    SE = pd.Series(SE)
    return B,SE
# Indirect estimation of price elasticities:1 ends here

# [[file:../Empirics/cfe_estimation.org::*Iterated Regression][Iterated Regression:1]]
# Tangled on Mon Aug 11 07:17:24 2025
def iterated_regression(y,z,return_se=False,return_v=False,VERBOSE=False,tol=1e-3,max_its=30,cores=None):
    """Estimate (delta,beta,loglambda).
    """

    # Create location-time dummies
    dm = use_indices(y,['t','m'])
    DateLocD = pd.get_dummies(zip(dm['t'],dm['m']))
    dm = sorted(list(set(zip(dm['t'],dm['m']))))

    DateLocD.index = y.index
    DateLocD.columns = pd.MultiIndex.from_tuples(dm)

    loglambda = pd.Series(np.random.randn(z.shape[0]),index=z.index,name='loglambda')
    X = pd.concat([z,DateLocD],axis=1)
    X['loglambda'] = loglambda

    stdev = X.std()
    for constant in stdev[stdev==0].index.tolist():
        warnings.warn("No variation in: %s" % str(constant))

    X = X.loc[:,stdev>0] # Drop  any X cols with no variation

    coeffs_last = np.inf
    coeffs = 0

    its = 0
    while  (its < 5) or (np.linalg.norm(coeffs_last - coeffs) > tol) and (its < max_its):

        if (its>1) and VERBOSE:
            print("Iteration %d, Norm: %g" % (its,np.linalg.norm(coeffs_last-coeffs)))
            print(coeffs - coeffs_last)

        coeffs_last = coeffs

        def _regress(ycol): # Inherits recently defined X and y

            x,_y = drop_missing([X,y[ycol]])
            _y = _y.squeeze()

            stdev = x.std()
            for constant in stdev[stdev==0].index.tolist():
                warnings.warn("No variation in: %s" % str(constant))

            x = x.loc[:,stdev>0] # Drop  any X cols with no variation

            b = pd.Series(np.linalg.lstsq(x,_y,rcond=None)[0],index=x.columns,name=_y.name)

            e = y[ycol] - x@b  # Include missings in e

            return b,e

        if cores is not None:
            ests = cores.map(_regress,[i for i in y.columns])
        else:
            ests = map(_regress,[i for i in y.columns])

        b,e = zip(*ests)
        coeffs = pd.DataFrame(b,index=y.columns)
        e = pd.DataFrame(e,index=y.columns).T

        delta = coeffs[z.columns]
        delta.columns.name = 'k'

        ce = y - z@delta.T
        ce = ce - ce.mean()

        X['loglambda'] = get_loglambdas(ce)[1]

        its += 1

    if VERBOSE and its >= max_its: print("Exceeded max_its")

    my_dm = coeffs.columns.intersection(dm)
    a = coeffs[my_dm]
    a.columns = pd.MultiIndex.from_tuples(my_dm)
    a.columns.names = ['t','m']
    b = coeffs['loglambda']

    d = coeffs[z.columns]

    out = [a,b,d,e,X['loglambda']]

    V = {}
    SE = {}
    if return_se or return_v:
        usecols = z.columns.tolist() + ['loglambda']
        for Item in e.columns:
            v = arellano_robust_cov(X[usecols],e[Item])
            V[Item] = v
            se = dict(zip(usecols,np.sqrt(np.diag(V[Item])))) # reduced form se on characteristics

            stderrs = (e[Item].groupby(['t','m']).std()/np.sqrt(e[Item].groupby(['t','m']).count())).tolist()
            se.update(dict(zip(my_dm,stderrs)))
            SE[Item] = pd.Series(se)

        SE = pd.DataFrame(SE).T
        SE.index.name = 'i'
        out = out + [SE,V]

    return tuple(out)
# Iterated Regression:1 ends here

# [[file:../Empirics/cfe_estimation.org::analysis_omnibus][analysis_omnibus]]
# Tangled on Mon Aug 11 07:17:24 2025
#name: analysis_omnibus

# -*- coding: utf-8 -*-

import tempfile
import numpy as np
import pandas as pd
from numpy.linalg import norm

def analysis_omnibus(y, z=None, prices=None, numeraire=None,min_xproducts=30,min_proportion_items=1./8,
                     VERBOSE=False, BOOTSTRAP=False):

    if BOOTSTRAP is True: # Bootstrap also a tolerance parameter
        BOOTSTRAP = 1e-3

    if z is None:
       z = pd.DataFrame(index=y.index)

    if prices is not None: # Check price indices (t,m) consistent with indices in y
        assert set([tuple(x) for x in prices.index.levels]) == set([tuple(x) for x in y.index.levels[1:]]), \
               "Must have prices for every (t,m) in expenditures y."

    results={'y':y,'z':z}
    if prices is not None: results['prices'] = prices

    firstround=y.reset_index().iloc[0]['t']

    # Deflate expenditures and prices by prices of numeraire good.
    if numeraire is not None and len(numeraire)>0:
        y = broadcast_binary_op(y, lambda foo,bar: foo-bar, np.log(prices[numeraire]))
        logp=np.log(prices).sub(np.log(prices[numeraire]),axis=0)

    use_goods = y.columns.tolist()

    # The criterion below (hh must have observations for at least min_proportion_items of goods) ad hoc
    using_goods=(y[use_goods].T.count()>=np.floor(len(use_goods) * min_proportion_items))
    y=y.loc[using_goods,use_goods] # Drop households with too few expenditure observations, keep selected goods
    y = drop_columns_wo_covariance(y,min_obs=min_xproducts,VERBOSE=False)
    # Only keep goods with observations in each (t,m)
    y = y.loc[:,(y.groupby(level=['t','m']).count()==0).sum()==0]

    a,ce,d,sed,sea,V = estimate_reduced_form(y,z,return_se=True,return_v=True,VERBOSE=VERBOSE)
    ce.dropna(how='all',inplace=True)
    se = sed

    results['ce']=ce
    results['delta_covariance'] = V

    bphi,logL = get_loglambdas(ce,TEST=True,min_obs=30)

    assert np.abs(logL.groupby(level='t').std().iloc[0] - 1) < 1e-12, \
           "Problem with normalization of loglambdas"

    cehat=np.outer(pd.DataFrame(bphi),pd.DataFrame(-logL).T).T
    cehat=pd.DataFrame(cehat,columns=bphi.index,index=logL.index)
    results['cehat']=cehat

    if VERBOSE:
        print("Norm of error in approximation of CE divided by norm of CE: %f" % (df_norm(cehat,ce)/df_norm(ce)))

    # Some naive standard errors & ANOVA
    miss2nan = ce*0
    anova=pd.DataFrame({'Prices':a.T.var(ddof=0),
                        'Characteristics':z.dot(d.T).var(ddof=0),
                        r'$\log\lambda$':(cehat + miss2nan).var(ddof=0),
                        'Residual':(ce-cehat).var(ddof=0)})
    anova=anova.div(y.var(ddof=0),axis=0)
    anova['Total var']=y.var(ddof=0)
    anova.sort_values(by=r'$\log\lambda$',inplace=True,ascending=False)

    results['anova'] = anova

    yhat = broadcast_binary_op(cehat + z.dot(d.T),lambda x,y: x+y,a.T)

    e = y.sub(yhat)

    goodsdf=d.copy()

    pref_params=[r'$\phi\beta_i$']
    if numeraire is not None and len(numeraire)>0:
        # FIXME: Issue here with dividing by a random variable.  What
        # properties do we want estimator of barloglambda_t to have?
        try:
            barloglambda_t=-a.loc[numeraire]/bphi[numeraire]
            logL = broadcast_binary_op(logL,lambda x,y: x+y,barloglambda_t) # Add term associated with numeraire good
            a = a - pd.DataFrame(np.outer(bphi,barloglambda_t),index=bphi.index,columns=barloglambda_t.index)
        except KeyError:
            pass

        # FIXME: Should really use weighted mean, since different precisions for a across different  markets
        logalpha = a[firstround].T.mean()
        goodsdf[r'$\log\alpha_i$'] = logalpha
        pref_params += [r'$\log\alpha_i$']
    else:
        pidx=a.mean()
        logL= broadcast_binary_op(logL,lambda x,y: x+y,pidx) # Add term associated with numeraire good
        a = a - pidx

    if VERBOSE:
        print("Mean of errors:")
        print(e.mean(axis=0))

    goodsdf[r'$\phi\beta_i$']=bphi
    goodsdf['$R^2$']=1-e.var()/y.var()

    goodsdf=goodsdf[pref_params+d.columns.tolist()+['$R^2$']]
    goodsdf['%Zero']=100-np.round(100*(~np.isnan(y[goodsdf.index])+0.).mean(),1)

    ehat=e.dropna(how='all')
    ehat=ehat-ehat.mean()

    if BOOTSTRAP:
        tmpf = tempfile.mkstemp(suffix='.csv')
        if VERBOSE: print("Bootstrapping.  Interim results written to %s." % tmpf[1])

        sel,Bs = bootstrap_elasticity_stderrs(ce,tol=1e-4,VERBOSE=VERBOSE,return_samples=True,outfn=tmpf[1])
        results['Bs'] = Bs
        se[r'$\phi\beta_i$']=sel
    else:
        sel=[]
        for i in ehat:
            foo=pd.DataFrame({'logL':logL.squeeze(),'e':ehat[i]}).dropna(how='any')
            sel.append(np.sqrt(arellano_robust_cov(foo['logL'],foo['e']).values[0,0]))
        se[r'$\phi\beta_i$']=np.array(sel)

    if numeraire is not None:
        se[r'$\log\alpha_i$']=ehat.query('t==%d' % firstround).std()/np.sqrt(ehat.query('t==%d'  % firstround).count())

    se.dropna(how='any',inplace=True)

    results['se'] = sed
    goodsdf=goodsdf.T[se.index.tolist()].T # Drop goods that we can't compute std errs for.

    goodsdf.sort_values(by=[r'$\phi\beta_i$'],inplace=True,ascending=False)
    goodsdf.dropna(how='any',inplace=True)
    results['goods'] = goodsdf

    results['a'] = a
    results['loglambda'] = logL
    results['logexpenditures'] = y
    results['logexpenditures_hat'] = yhat

    return results
# analysis_omnibus ends here

# [[file:../Empirics/cfe_estimation.org::elasticities_equal][elasticities_equal]]
# Tangled on Mon Aug 11 07:17:24 2025
#name: elasticities_equal

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.stats.distributions import f as F

def elasticities_equal(b1,b2,v1,v2,N,N2,pvalue=False,criterion=False):

    assert N2<N, "N2 should be size of sub-sample of pooled sample."
    b1 = b1.reshape((-1,1))
    b2 = b2.reshape((-1,1))

    n=len(b1)

    assert n==len(b2), "Length of vectors must be equal"

    def Fcriterion(psi):
        try:
            psi=psi[0,0]
        except (TypeError, IndexError):
            pass

        d = psi*b1 - b2
        if d.shape[0]<d.shape[1]: d = d.T

        W = np.linalg.inv((psi**2)*v1 + v2) # Independent case

        F = N2*(N-n-1)/((N-1)*(n-1)) * d.T@W@d

        if ~np.isscalar(F):
            F=F[0,0]

        return F

    #result = minimize_scalar(Fcriterion,method='bounded',bounds=[0,10])
    Fcriterion(1.)
    result = minimize_scalar(Fcriterion)
    psi=np.abs(result['x'])
    Fstat=result['fun']

    assert result['success'], "Minimization failed?"

    outputs = [psi,Fstat]

    if pvalue:
        p = 1 - F.cdf(Fstat,n-1,N-n-1)
        outputs.append(p)

    if criterion:
        outputs.append(Fcriterion)

    return tuple(outputs)
# elasticities_equal ends here

# [[file:../Empirics/cfe_estimation.org::predicted_expenditures][predicted_expenditures]]
# Tangled on Mon Aug 11 07:17:24 2025
#name: predicted_expenditures

import numpy as np

def predicted_expenditures(yhat,e):
    """
    Return levels of predicted expenditures.

    =yhat= is a dataframe or xarray of predicted log item expenditures,
           with columns corresponding to different items.
       =e= is a dataframe or xarray of the residuals from the estimation which
           yielded =yhat=.
    """
    ebar = e.mean('j')
    evar = e.var('j')

    x = np.exp(yhat + ebar + evar/2)

    return x
# predicted_expenditures ends here

# [[file:../Empirics/cfe_estimation.org::optimal_index][optimal_index]]
# Tangled on Mon Aug 11 07:17:24 2025
#name: optimal_index

import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore",category=UserWarning)
    import xarray as xr

import pandas as pd

def optimal_index(a,yhat,e):
    """Return individual optimal price indices for each household in all settings.

    Given log shadow prices =a=, predicted log expenditures =yhat=,
    and residuals from prediction =e= calculate optimal price indices
    for each household =j= in each setting.

    A "setting" is a pair (t,m).  To get the price index for a
    household j=0 observed at (t0,m0)=(1,2) for the counterfactual
    setting (t,m)=(1,0) one can use something like
    R.sel(j=0,t0=1,m0=2,t=1,m=0).

    Ethan Ligon                                                 July 2018
    """

    # Begin by obtaining predicted expenditure shares in null setting.
    # Subtract relevant actual prices for household;
    # yhat missing for all but actual setting, missings propagate.
    x0 = predicted_expenditures(yhat - a,e)

    # (t0,m0) is 'home' setting
    x0 = x0.rename({'t':'t0','m':'m0'})

    xsum = x0*np.exp(a)    # Predicted x_i in different settings (t,m)
                           # for households in every setting (t0,m0).

    pidx = xsum.sum('i',skipna=False)   # Total expenditures in different settings.

    R=pidx/pidx.sel(t0=pidx.coords['t'],t=pidx.coords['t'],m0=pidx.coords['m'],m=pidx.coords['m'])

    return R.transpose('j','t0','m0','t','m')
# optimal_index ends here
