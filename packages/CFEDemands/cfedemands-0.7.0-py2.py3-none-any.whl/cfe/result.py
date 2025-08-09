# [[file:../Empirics/result.org::result_class][result_class]]
# Tangled on Fri Mar 15 07:15:48 2024
import numpy as np
import pandas as pd
from . import estimation 
import warnings

# Funky warning re: cfgrib from xarray we can't do anything about
with warnings.catch_warnings():  
    warnings.filterwarnings("ignore",category=UserWarning)
    import xarray as xr

from collections import namedtuple, OrderedDict
from cfe.df_utils import to_dataframe, is_none, from_dataframe, ols, df_norm, use_indices, drop_missing, arellano_robust_cov

Indices = namedtuple('Indices',['j','t','m','i','k'])

class Result(xr.Dataset):

    """A class which packages together data and results for the CFE demand system.

    Result inherits from xarray.Dataset, and stores data as xarray.DataArrays
    with (as necessary) coordinates i for goods, j for households, t for periods,
    m for markets, and k for household characteristics.

    Typical usage with xarray.DataArrays (y,z)

    >>> z.dims  # Household characteristics
    ('k','j','t','m')
    >>> y.dims  # log expenditures
    ('i', 'j', 't', 'm')
    >>> R = cfe.result.Result(y=y,z=z) 
    >>> R.get_predicted_log_expenditures()
    >>> R.get_loglambdas()
    >>> R.get_alpha()                                                
    >>> R.get_stderrs() # Expensive bootstrap!

    Ethan Ligon                                                 August 2018
    """

    __slots__ = ['y','z','delta','beta','alpha','loglambdas','a','yhat','ce',
                 'prices','logp','characteristics', 
                 'cehat','e','delta_covariance','beta_covariance','se_delta','se_beta','se_alpha',
                 'se_a','firstround','min_proportion_items','min_xproducts',
                 'useless_expenditures','stderr_tol','indices','iterate','verbose',
                 'all_tm','common_alpha']

    def __init__(self, **kwargs):
        """To load data from a netcdf file, use cfe.result.from_dataset().

        To instantiate from data on log expenditures (y) and household
        characteristics (z), supply each as xarray.DataArrays, with
        coordinates for y (i,j,t,m), and for z (j,k,t,m).

        All xarray.DataArrays which may be supplied:

          - y : log expenditures with coordinates (i,j,t,m).

          - z/characteristics : Household characteristics with coordinates (k,j,t,m). 

          - prices : Prices for goods (in levels) with coordinates (i,t,m).
            Supply only one of prices and logp.

          - logp : Log prices for goods (in levels) with coordinates (i,t,m).
            Supply only one of prices and logp.

        The below can be passed or assigned to an instance of Result,
        but would ordinarily be computed.

          - delta : Parameters with coordinates (i,k); the dot product of
            (z,delta) is an additive shifter of log expenditures.
            Estimated by the method get_reduced_form().

          - alpha : Preference parameters with coordinates i; additive
            shifters of log expenditures.

          - beta : Frisch elasticities with coordinates i.
            Estimated by the method get_beta()

          - loglambdas : log of marginal utility of expenditures with
            coordinates (j,t,m).  Estimated by the method
            get_loglambdas()

          - a : Good-period-market fixed effects, indexed by (i,t,m).
            Estimated by the method get_reduced_form().

          - yhat : Predicted log expenditures, indexed by (i,j,t,m).
            Estimated by the method get_predicted_log_expenditures().

          - ce : Residuals from reduced form estimation, indexed by
            (i,j,t,m).  Estimated by the method get_reduced_form().

          - cehat : Optimal rank 1 approximation to ce, indexed by
            (i,j,t,m).  Estimated by the method get_cehat().

          - e : Unexplained residuals from log expenditure equations.
            Estimated by the method get_loglambdas().

          - delta_covariance : Covariance matrix of parameter
            estimates delta; coordinates (i,k,kp).  Estimated by
            get_reduced_form().

          - beta_covariance : Covariance matrix of parameter
            estimates belta; coordinates (i,ip).  Estimated by
            get_stderrs() via (expensive) bootstrap.

          - se_delta : Standard errors of parameter estimates delta;
            coordinates (i,k).  Estimated by get_reduced_form().

          - se_beta : Standard errors of parameter estimates beta,
            with coordinates i. Estimated via the bootstrap method
            get_stderrs().  Note that this may be expensive.

          - se_alpha : Standard errors of parameter estimates alpha
            with coordinates i.  Estimated by method get_alpha().

          - se_a : Standard errors of good-time-market effects a, with
            coordinates (i,t,m).  Estimated by get_reduced_form().

        The following are attributes that may affect estimation or
        interpretation of features of the instance:

          - firstround : The coordinate identifying the earliest round
            of data.  Set automatically if coordinate values for t are
            sensible.

          - min_proportion_items : If a given household (j,t,m) has
            non-missing data for a proportion of all goods less than
            this parameter the household will be dropped from
            estimation. Default is 1/8.

          - min_xproducts : If a given good contributes fewer than
            min_xproducts observations to the estimation of the
            covariance matrix of residuals from the reduced form then
            the good will be dropped.  Default is 30.

          - all_tm : A boolean flag.  If true, only keep goods with obs. 
            in every (t,m).

          - common_alpha : Boolean.  If true, households in all
            markets m are assumed to share a common preference
            parameter \alpha.  Otherwise \alpha will vary across
            markets.  Default True.

          - iterate : A boolean flag. If true, iterate estimation
            until residual is orthogonal to \log\lambda.

          - useless_expenditures : A boolean flag.  Set to true at
            point of instantiation if you want to /keep/ expenditures
            with few observations.  The definition of "useless"
            depends on the attributes =min_proportion_items= and
            =min_xproducts=.

          - stderr_tol : A tolerance parameter governing the precision
            with which se_beta are estimated.  Default is 0.01.

          - indices : A named tuple meant to permit changes in the
            coordinates (j,t,m,i,k).  Not implemented.

          - verbose : A boolean; set to True for a more verbose
            description of progress during estimation.

        """

        arrs = dict(alpha=None, beta=None, delta=None,
                    prices=None, characteristics=None, loglambdas=None, a=None,
                    yhat=None, ce=None, cehat=None, e=None, delta_covariance=None,
                    beta_covariance=None,
                    se_delta=None, se_beta=None, se_alpha=None, se_a = None,
                    y=None, logp=None, z=None)

        attrs = dict(firstround=None,
                     min_proportion_items=1./8, min_xproducts=30,
                     all_tm=True,
                     common_alpha=True,
                     useless_expenditures=None,
                     stderr_tol=0.01,
                     indices = Indices('j', 't', 'm', 'i', 'k'),
                     iterate=False,
                     verbose=False)

        try: # Maybe input is already an xarray.Dataset?
            ds = kwargs.pop('data')
            for k in arrs:
                try:
                    a = xr.DataArray(ds.variables[k])
                    arrs[k] = a.assign_coords({d:ds.coords[d] for d in a.dims})
                except KeyError:
                    pass

            attrs.update(ds.attrs)
            coords = ds.coords

        except KeyError:  # Or maybe it's just a tuple of arrays and attributes.
            for k in arrs:
                try:
                    thing = kwargs.pop(k)
                    try:  # thing may be a dataframe?
                        thing = xr.Dataset.from_dataframe(thing) #,sparse=True)
                        if k in ['y', 'yhat', 'ce', 'cehat', 'e', 'prices']:
                            thing = thing.to_array('i')
                        elif k in ['z', 'characteristics']:
                            thing = thing.to_array('k')
                    except AttributeError:  # Guess not!
                        pass
                    arrs[k] = thing
                except KeyError:
                    pass

            attrs.update(kwargs)
            coords = None

        # Deal with useless expenditures
        if arrs['y'] is not None:
            arrs['y'], attrs = _drop_useless_expenditures(arrs['y'], attrs,VERBOSE=attrs['verbose'])
      
        super(Result,self).__init__(data_vars=arrs, coords=coords, attrs=attrs)

        if is_none(self.z) and not is_none(self.characteristics):
            self['z'] = self.characteristics
        elif not is_none(self.z) and is_none(self.characteristics):
            self['characteristics'] = self.z
        elif is_none(self.characteristics) and not is_none(self.y):
            self['characteristics'] = pd.DataFrame(index=self.y.isel(i=0).index).to_xarray()
            self['z'] = self['characteristics']

        if is_none(self.logp) and not is_none(self.prices):
            self['logp'] = np.log(self.prices)
        elif not is_none(self.logp) and is_none(self.prices):
            self['prices'] = np.exp(self.logp)

        if not is_none(self.beta) and not is_none(self.alpha):
            assert(self.alpha.shape == self.beta.shape)

        if is_none(self.attrs['firstround']) and not is_none(self.coords['t']):
            self.attrs['firstround'] = self.coords['t'][0].item()



    def drop_useless_expenditures(self,as_df=False,VERBOSE=False):
        """Drop expenditure items with too few observations.

        "Too few" depends on the attributes min_proportion_items and min_xproducts.  
        Once called this method sets the attribute 'useless_expenditures' to False.
        """

        y0,attrs = _drop_useless_expenditures(self.y,self.attrs,VERBOSE=VERBOSE)
        
        self['y'] = y0
        self.attrs = attrs

        assert self.y.dims==('i','j','t','m')

        if as_df:
            return to_dataframe(self.y,'i')
        else:
            return self

    
        if self.attrs['useless_expenditures']:
            y = self.y
            min_proportion_items = self.attrs['min_proportion_items']
            min_xproducts = self.attrs['min_xproducts']

            use_goods=y.coords['i'].data

            # Convert to pd.DataFrame
            y = to_dataframe(y.sel(i=use_goods),'i')
            J,n = y.shape

            # The criterion below (hh must have observations for at least min_proportion_items of goods) ad hoc
            using_goods=(y.T.count()>=np.floor(len(use_goods) * min_proportion_items))
            y = y.loc[using_goods,:] # Drop households with too few expenditure observations, keep selected goods

            if VERBOSE:
                print('min_proportion_items test drops %d households.' % (J-y.shape[0]))
                J,n = y.shape

            y = estimation.drop_columns_wo_covariance(y,min_obs=min_xproducts,VERBOSE=VERBOSE)

            if VERBOSE:
                print('drop_columns_wo_covariance test drops %d households and %d goods.' % (J-y.shape[0],n-y.shape[1]))
                J,n = y.shape

            # Only keep goods with observations in each (t,m)
            y = y.loc[:,(y.groupby(level=['t','m']).count()==0).sum()==0]

            if VERBOSE:
                print('good in every (t,m) test drops %d households and %d goods.' % (J-y.shape[0],n-y.shape[1]))
                J,n = y.shape

            y = from_dataframe(y).dropna('i',how='all')

            try:
                self['prices'] = self.prices.sel(i=y.coords['i'])
                self['logp'] = np.log(self.prices)
            except ValueError:
                pass # No prices in self?

            new =  self.sel(i=y.coords['i'],j=y.coords['j'])
            new.attrs['useless_expenditures'] = False

            self = new

        if as_df:
            return to_dataframe(self.y,'i')
        else:
            return self

    def get_reduced_form(self,VERBOSE=False,tol=1e-3):
        """Estimate reduced form expression for system of log expenditures.

        Computes a, ce, delta, se_delta, delta_covariance.          
        """

        if VERBOSE or self.attrs['verbose']: VERBOSE=True

        if self.attrs['iterate']:
            if VERBOSE: print("Iterating...")
            self.iterated_estimation(VERBOSE=VERBOSE,tol=tol)
        else:
            self._get_reduced_form(VERBOSE=VERBOSE)

    def _get_reduced_form(self,VERBOSE=False):
        """Estimate reduced form expression for system of log expenditures.

        Computes a, ce, delta, se_delta, delta_covariance.          
        """

        y = self.drop_useless_expenditures(as_df=True) # Returns a dataframe
        y.dropna(how='all',axis=1,inplace=True)

        z = to_dataframe(self.z,'k')

        a,ce,d,sed,sea,V = estimation.estimate_reduced_form(y,z,return_se=True,return_v=True,VERBOSE=VERBOSE)
        ce.dropna(how='all',inplace=True)

        self['a'] = from_dataframe(a,'i')
        try:
            self['delta'] = from_dataframe(d).to_array('k')
        except AttributeError:
            d.columns.name = 'k'
            self['delta'] = from_dataframe(d)

        self['ce'] = from_dataframe(ce).transpose(*self.y.dims)
        self['se_delta'] = from_dataframe(sed)
        self['se_a'] = from_dataframe(sea)

        self['delta_covariance'] = V

    def iterated_estimation(self,VERBOSE=False,tol=1e-3,max_its=30,cores=None):
        """Estimate (delta,beta,loglambda).

        Sets beta, loglambdas, and cehat.
        """
        z = to_dataframe(self.z,'k')
        y = to_dataframe(self.y,'i')

        dm = use_indices(y,['t','m'])
        dm = sorted(list(set(zip(dm['t'],dm['m']))))

        a,b,d,e,loglambda,se,V = estimation.iterated_regression(y,z,return_se=True,return_v=True,VERBOSE=VERBOSE,cores=cores)

        seb = se['loglambda']
        sea = se[dm]
        sea.columns = pd.MultiIndex.from_tuples(sea.columns)
        sea.columns.names = ['t','m']

        sed = se[z.columns]
        sed.columns.name = 'k'

        self['a'] = from_dataframe(a,'i')
        try:
            self['delta'] = from_dataframe(d).to_array('k')
        except AttributeError:
            d.columns.name = 'k'
            self['delta'] = from_dataframe(d)

        self['e'] = from_dataframe(e.stack()).transpose(*self.y.dims)
        self['se_delta'] = from_dataframe(sed,'i')
        self['se_a'] = from_dataframe(sea,'i')
        self['delta_covariance'] = xr.Dataset(V).to_array(dim='i')

        cehat=np.outer(pd.DataFrame(b),pd.DataFrame(loglambda).T).T
        cehat=pd.DataFrame(cehat,columns=b.index,index=loglambda.index)

        self['cehat'] = from_dataframe(cehat).transpose(*self.y.dims)
        self['ce'] = self['cehat'] + self['e']
        self['loglambdas'] = loglambda.astype(float).to_xarray()
        self['beta'] = -b.to_xarray()
        self['se_beta'] = from_dataframe(seb,'i')

        if self.attrs['common_alpha']:
            self['alpha'] = self.a.sel(t=self.firstround,drop=True).mean('m')
            self['se_alpha'] = np.sqrt((self.se_a.sel(t=self.firstround,drop=True)**2).sum('m'))/len(self.se_a.coords['m'])
        else:
            self['alpha'] = self.a.sel(t=self.firstround,drop=True)
            self['se_alpha'] = self.se_a.sel(t=self.firstround,drop=True)


    def get_loglambdas(self,as_df=False,tol=1e-3):
        """Estimate (beta,loglambda).

        Sets beta, loglambdas, and cehat.  Returns loglambdas.
        """
        if is_none(self.loglambdas):
            if is_none(self.ce):
                self.get_reduced_form(tol=tol)

            min_obs = self.attrs['min_xproducts']

            ce = to_dataframe(self.ce,'i')

            bphi,logL = estimation.get_loglambdas(ce,TEST=False,min_obs=min_obs)

            assert np.abs(logL.groupby(level='t').std().iloc[0] - 1) < 1e-12, \
                "Problem with normalization of loglambdas"

            cehat=np.outer(pd.DataFrame(bphi),pd.DataFrame(-logL).T).T
            cehat=pd.DataFrame(cehat,columns=bphi.index,index=logL.index)

            self['cehat'] = from_dataframe(cehat).transpose(*self.y.dims)
            self['loglambdas'] = logL.to_xarray()
            self['beta'] = bphi.to_xarray()

        if as_df:
            df = self.loglambdas.to_dataframe().squeeze().unstack('t').dropna(how='all')
            return df
        else:
            return self.loglambdas

    def get_beta(self,as_df=False):
        if is_none(self.beta):
            self.get_loglambdas()

        if as_df:
            return self.beta.to_dataframe().squeeze()
        else:
            return self.beta

    def get_delta(self,as_df=False):
        if is_none(self.delta):
            self.get_reduced_form()

        if as_df:
            return self.delta.to_dataframe().squeeze().unstack('k').dropna()
        else:
            return self.delta

    def get_cehat(self,as_df=False,tol=1e-3):
        if is_none(self.beta):
            self.get_loglambdas(tol=tol)

        out = self.cehat

        if as_df:
            df = to_dataframe(out,'i').dropna(how='all')
            return df
        else:
            return out

    def get_stderrs(self,as_df=True,return_v=False):
        if is_none(self.se_beta):
            if is_none(self.ce):
                self.get_reduced_form()

            tol = self.attrs['stderr_tol']
            VB = self.attrs['verbose']

            ce = to_dataframe(self.ce,'i')

            se,V = estimation.bootstrap_elasticity_stderrs(ce,return_v=True,tol=tol,VERBOSE=VB)
            self['se_beta'] = from_dataframe(se)
            self['beta_covariance'] = xr.DataArray(V.values,dims=['i','ip'],coords={'i':self.coords['i'].values,'ip':self.coords['i'].values})

        if not return_v:
            out = self['se_beta']
        else:
            out = self['beta_covariance']

        if as_df:
            df = to_dataframe(out).squeeze().dropna(how='all')
            return df
        else:
            return out

    def anova(self):
        """Returns pandas.DataFrame analyzing variance of expenditures.

        Columns are proportion of variance in log expenditures
        explained by prices, household characteristics, and
        loglambdas; finally the R^2 of the regression and total
        variance of log expenditures.
        """

        yhat = self.get_predicted_log_expenditures()

        y = to_dataframe(self.y,'i') # drop_useless_expenditures(as_df=True) # A dataframe

        miss2nan = self.ce*0 

        df = pd.DataFrame({'Prices':to_dataframe(self.a.var(['t','m'],ddof=0)),
                          'Characteristics':to_dataframe(self.z.dot(self.delta.T).var(['j','t','m'],ddof=0)),
                          r'$\log\lambda$':to_dataframe((self.cehat + miss2nan).var(['j','t','m'],ddof=0))})

        df = df.div(y.var(ddof=0),axis=0)
        df['Total var'] = y.var(ddof=0)

        r2 = 1 - self.e.var(['j','t','m'])/(self.y+(self.e*0)).var(['j','t','m'])  # Make sure both e & y sharing missing elements.

        df['$R^2$'] = to_dataframe(r2)

        df.sort_values(by=r'$\log\lambda$',inplace=True,ascending=False)

        return df

    def get_predicted_log_expenditures(self,as_df=False,tol=1e-3):
        """Return predicted log expenditures.

        Sets yhat and e.
        """
        if is_none(self.yhat):
            cehat = self.get_cehat(tol=tol)
            self['yhat'] = cehat + self.z@self.delta + self.a

            self['e'] = self.y - self.yhat

        out = self.yhat

        if as_df:
            df = out.to_dataframe().squeeze().unstack('i').dropna(how='all')
            df.index.names = ['j','t','m']
            return df
        else:
            return out


    def get_predicted_expenditures(self,as_df=False,tol=1e-3):
        """Return predicted levels of expenditures.

        Assumes residuals e have normal distribution.
        """
        yhat = self.get_predicted_log_expenditures(tol=tol)
        e = self.e

        out = estimation.predicted_expenditures(yhat,e)

        if as_df:
            df = to_dataframe(out,'i').dropna(how='all')
            return df
        else:
            return out

    def get_alpha(self,as_df=False):
        """Return alpha parameters.  

        These are the averages of the first round of data on log
        expenditures, and assumed equal across markets if 
        atttribute =common_alpha= is true.  

        Conversely, if =common_alpha= is false, then each market gets its own separate alpha.
        """
        common = self.attrs['common_alpha']
        
        if is_none(self['alpha']):
            if is_none(self.loglambdas):
                self.get_loglambdas()

            if common:
                self['alpha'] = self.a.sel(t=self.firstround,drop=True).mean('m')
                self['se_alpha'] = np.sqrt((self.se_a.sel(t=self.firstround,drop=True)**2).sum('m'))/len(self.se_a.coords['m'])
            else:
                self['alpha'] = self.a.sel(t=self.firstround,drop=True)
                self['se_alpha'] = self.se_a.sel(t=self.firstround,drop=True)

        out = self.alpha

        if as_df:
            df = out.to_dataframe().squeeze().dropna(how='all')
            return df
        else:
            return out

    def a_decomposition(self):
        """Decompose constant terms from reduced form regression.

        Yields an xr.Dataset containing estimates of differences in
        average \log\lambda and log price level across settings, along
        with standard errors of these estimates.  In addition we provide
        estimates of the "residual" prices.

        Ethan Ligon                                           August 2018
        """ 

        self.get_loglambdas() 
        alpha = self.get_alpha()

        Pbar=[]
        Lbar=[]
        SE=[]
        V=[]
        P=[]
        b = self.beta - self.beta.mean('i')

        RHS = xr.concat([(1 - self.beta*0),-b],'l').T
        RHS = RHS.to_dataframe().unstack('l')
        RHS.columns = RHS.columns.droplevel(0)
        for t in self.coords['t'].values:
            for m in self.coords['m'].values:
                lhs = ((self.a - alpha)/self.se_a).sel(t=t,m=m,drop=True).to_dataframe('')
                rhs = RHS.div(self.se_a.sel(t=t,m=m,drop=True).to_dataframe().squeeze(),axis=0)  
                b,se,v,p = ols(rhs,lhs,return_se=True,return_v=True,return_e=True)
                p = (p.to_xarray()*self.se_a.sel(t=t,m=m,drop=True)).to_array()
                Pbar.append(b.loc[0].values[0])
                P.append(p.values)
                Lbar.append(b.loc[1].values[0])
                SE.append(se.values.T[0])
                V.append(v)

        Pbar = np.array(Pbar).reshape((-1,len(self.coords['m']))).T
        Lbar = np.array(Lbar).reshape((-1,len(self.coords['m']))).T

        Pbar = xr.DataArray(Pbar,dims=['m','t'],coords={'t':self.coords['t'],'m':self.coords['m']},name='pbar')
        Lbar = xr.DataArray(Lbar,dims=['m','t'],coords={'t':self.coords['t'],'m':self.coords['m']},name='lbar')
        Pse = xr.DataArray(np.array(SE)[:,0].reshape((-1,len(self.coords['m']))).T,dims=['m','t'],coords={'t':self.coords['t'],'m':self.coords['m']},name='pbar_se')
        Lse = xr.DataArray(np.array(SE)[:,1].reshape((-1,len(self.coords['m']))).T,dims=['m','t'],coords={'t':self.coords['t'],'m':self.coords['m']},name='lbar_se')
        #P = xr.DataArray(np.array([[x.squeeze() for x in P]]),dims=['m','t','i'],coords=self.a.coords).transpose('i','t','m')

        return xr.Dataset({'pbar':Pbar,'lbar':Lbar,'pbar_se':Pse,'lbar_se':Lse}) #,'p_resid':P})

    def optimal_index(self):
        """Household-specific exact price index.

        For a household j observed at (t,m)=(t0,m0) computes
        proportional change in total expenditures required to keep
        \lambda constant across all observed settings (t,m).
        """
        if is_none(self.yhat):
            self.get_predicted_log_expenditures()

        a = self.a                

        R = estimation.optimal_index(a,self.yhat,self.e)

        return R

    def resample_lambdas(self):
        """Resample loglambdas.

        This produces a new object with preference parameters drawn
        from self and a measurement error process for expenditures
        which is log-normal.
        """

        d = self.dims
        S = np.random.randint(0,d['j'],size=d['j'])

        R = Result(data=self)

        foo = self.loglambdas.isel(j=S)
        foo.coords['j'] = self.loglambdas.coords['j']
        R['loglambdas'] =  foo + self.loglambdas*0.

        foo = self.z.isel(j=S)
        foo.coords['j'] = self.z.coords['j']

        R['z'] = foo
        R['characteristics'] = R.z

        R['cehat'] = R.loglambdas * R.beta

        # Retrieve mean & std of errors
        foo = (self.ce - self.cehat).to_dataframe('e').dropna()
        mu = foo.mean()
        sigma = foo.std()

        # Generate new errors lognormally distributed
        R['e'] = xr.DataArray(np.random.normal(loc=mu,scale=sigma,size=(d['j'],d['t'],d['m'],d['i'])),coords=R.ce.coords)

        # Add missings back in where appropriate
        foo = self.y.isel(j=S)
        foo.coords['j'] = self.z.coords['j']
        R['e'] = R['e'] + 0*foo

        R['ce'] = R.cehat + R.e

        R['yhat'] = R.cehat + R.z.dot(R.delta) + R.a

        R['y'] = R.yhat + R.e

        return R
# result_class ends here

# [[file:../Empirics/result.org::result_to_file][result_to_file]]
# Tangled on Fri Mar 15 07:15:48 2024
    def to_dataset(self,fn=None,**kwargs):
        """Convert Result instance to xarray.Dataset."""
        D = xr.Dataset(self)

        if fn is not None:
            D.to_netcdf(fn,**kwargs)

        return D

    def to_pickle(self,fn):
        """Pickle Result instance in file fn."""
        import pickle
      
        d = self.to_dict()
        with open(fn,'wb') as f:
            pickle.dump(d,f)

        return d

def from_dataset(fn,**kwargs):
    """
    Read persistent netcdf (xarray.Dataset) file to Result.
    """

    D = xr.open_dataset(fn,**kwargs)

    R = Result(data=D)

    return R

def from_shelf(fn):
    import shelve

    with shelve.open(fn):
        pass

def from_pickle(fn):
    import xarray as xr
    import pickle

    with open(fn,'rb') as f:
        X = pickle.load(f)

    D = xr.Dataset.from_dict(X)

    R = Result(data=D)

    return R
# result_to_file ends here

# [[file:../Empirics/result.org::*Drop useless expenditures][Drop useless expenditures:1]]
# Tangled on Fri Mar 15 07:15:48 2024
def _drop_useless_expenditures(y0, attrs, VERBOSE=False):
    """Drop expenditure items with too few observations.

    "Too few" depends on the attributes min_proportion_items and min_xproducts.  
    Once called this method sets the attribute 'useless_expenditures' to False.
    """

    if attrs['useless_expenditures'] is False:
        return y0, attrs
    
    _y = to_dataframe(y0,'i')

    min_proportion_items = attrs['min_proportion_items']
    min_xproducts = attrs['min_xproducts']
    all_tm = attrs['all_tm']

    use_goods = [v for v in _y]

    _y = _y[use_goods]
    y = _y
    J, n = y.shape

    # The criterion below (hh must have observations for at least min_proportion_items of goods) ad hoc
    using_goods = (y.T.count()>=np.floor(len(use_goods) * min_proportion_items))
    y = y.loc[using_goods] # Drop households with too few expenditure observations, keep selected goods

    if VERBOSE:
        print('min_proportion_items test drops %d households.' % (J-y.shape[0]))
        J,n = y.shape

    y = estimation.drop_columns_wo_covariance(y,min_obs=min_xproducts,VERBOSE=VERBOSE)

    if VERBOSE:
        print('drop_columns_wo_covariance test drops %d households and %d goods.' % (J-y.shape[0],n-y.shape[1]))
        J,n = y.shape

    # Only keep goods with observations in each (t,m)
    if all_tm:
        y = y.loc[:,(y.groupby(level=['t','m']).count()==0).sum()==0]

        if VERBOSE:
            print('good in every (t,m) test drops %d households and %d goods.' % (J-y.shape[0],n-y.shape[1]))
            J,n = y.shape

    _y = y.to_xarray().to_array('i')
    attrs['useless_expenditures'] = False

    return _y,attrs
# Drop useless expenditures:1 ends here

# [[file:../Empirics/result.org::result_demand_interface][result_demand_interface]]
# Tangled on Fri Mar 15 07:15:48 2024
import consumerdemands as demands
import pandas as pd

def _demand_parameters(self,p=None,z=None):
    """Return tuple of (p,alpha,beta,phi) from result.

    Note that the alpha returned is exp(alpha + delta.T z).

    p can be a complete collection (e.g. Series) of prices, or a
    dictionary specifying a subset of prices.  In this case
    unspecified prices are taken to be equal to one.

    If p is an (t,m) tuple will attempt to set prices from self.prices.

    Suitable for passing to =cfe.demand= functions.

    """

    beta = self.get_beta()
    n = len(beta)

    if is_none(z):
        z = self.z.isel(j=0,t=0,m=0,drop=True).fillna(0)*0

    alpha = np.exp(self.get_alpha() + self.delta.dot(z))

    replace = False
    if type(p) is dict:  # Try replacing some prices?
        replace = p.copy()
        p = None
    elif type(p) is tuple and len(p)==2: # Select (t,m) prices
        p = self.prices.sel(t=p[0],m=p[1])

    if is_none(p):
        p = beta*0 # Copy coords, etc from beta
        p.data = [1.]*n
        p.name = 'prices'

    if replace:
        p = p.to_dataframe().squeeze()
        for k,v in replace.items():
            p[k] = v

    # The following hijinks deal with missing values (e.g., in prices)
    foo = xr.Dataset({'beta':beta,'alpha':alpha,'prices':p}).to_dataframe().dropna(how='any')

    if len(foo)==0:
        raise ValueError("No goods have non-missing beta, alpha, and price; can't compute demands.")

    p = foo.prices
    beta = foo.beta
    alpha = foo.alpha

    phi = 0 # phi not (yet?) an attribute of Result.

    return p,{'alpha':alpha,'beta':beta,'phi':phi}

def _demands(self,x,p=None,z=None,type="Marshallian"):
    """Quantities demanded at prices p for household with observable
    characteristics z, having a utility function with parameters given
    by (possibly estimated) attributes from a Result (i.e., the
    vectors of parameters alpha, beta, delta).

    Default type is "Marshallian", in which case argument x is budget.

    Alternative types:
       - "Frischian" :: argument x is Marginal utility of expenditures
       - "Hicksian" :: argument x is level of utility

    Ethan Ligon                                    April 2019
    """

    p,pparms = _demand_parameters(self,p,z)

    Qs = {'Marshallian':demands.marshallian.demands,
          'Hicksian':demands.hicksian.demands,
          'Frischian':demands.frischian.demands}

    q = pd.Series(Qs[type](x,p,pparms),index=pparms['alpha'].index,name='quantities')

    return q

def _utility(self,x,p=None,z=None):
    """Indirect utility

    Varies with prices p, budget x and observable characteristics z,
    having a utility function with parameters given by (possibly
    estimated) attributes from a Result (i.e., the vectors of
    parameters alpha, beta, delta).

    Ethan Ligon                                    April 2019
    """

    p,pparms = _demand_parameters(self,p,z)

    return demands.marshallian.indirect_utility(x,p,pparms)

def _expenditurefunction(self,U,p=None,z=None):
    """Total Expenditures

    Varies with level of utility U, prices p, and observable
    characteristics z, with a utility function having parameters given
    by (possibly estimated) attributes from a Result (i.e., the
    vectors of parameters alpha, beta, delta).

    Ethan Ligon                                    April 2019
    """

    p,pparms = _demand_parameters(self,p,z)

    return demands.hicksian.expenditurefunction(U,p,pparms)

Result.demands = _demands
Result.indirect_utility = _utility
Result.expenditure = _expenditurefunction
# result_demand_interface ends here
