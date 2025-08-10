import numpy as np
import contur
import contur.config.config as cfg
import contur.data.static_db as cdb
import contur.util.utils as cutil
import yoda

class CovarianceBuilder(object):
    """
    `ao` Yoda AO
    apply_min: apply the minimum number of systematic uncertainties criteria when determining
    whether or not to use the error breakdown for correlations.

    Class to handle retrieval of annotations/errors from YODA objects
    """
    def __init__(self, orig_ao, ao, aos, isScaled, scaleFactor, apply_min=True,ignore_corrs=False):
        self.ao=ao
        self.hasBreakdown=self._getBreakdownAttr(orig_ao,apply_min)
        self.readMatrix  =self._getMatrixAttr()
        self.nbins=self.ao.numPoints()
        self.cov=None
        self.uncov=None
        self.covM=None
        self.diagonal=None
        self.errorBreakdown = None
        self.scaleFactor = scaleFactor
        if self.hasBreakdown:
            if 'Estimate0D' in orig_ao.type():
                self.errorBreakdown = dict([ (src, no.array([ orig_ao.errEnv(src) ])) for src in ao.sources() ])
            else:
                self.errorBreakdown = dict([ (src, np.array([ b.errEnv(src) if b.hasSource(src) \
                                                                            else 0.0 for b in orig_ao.bins() ])) \
                                                                                for src in orig_ao.sources() ])

        # always build the diagonal matrix.
        self.buildCovFromErrorBar()

        if self.readMatrix:
            # read the covariance matrix from the dictionary of analysis objects
            try:
                self.read_cov_matrix(isScaled,aos)
            except Exception as ex:
                cfg.contur_log.warning(ex)                
                self.readMatrix = False
            #print("RM",orig_ao.path(),self.covM)
                                
        else:
            if ('Estimate' in orig_ao.type() and orig_ao.dim() > 1):
                if self.hasBreakdown:
                    self.buildCovFromBreakdown(orig_ao,ignore_corrs)                
                else:
                    self.covM = self.diagonal.copy()
            else:
                self.covM = self.diagonal.copy()
                #print("EB",orig_ao.path(),self.covM)
        
    def _getBreakdownAttr(self,ao,apply_min):
        """
        return true if this AO has an error breakdown
        """
        if not 'Estimate' in ao.type():
            cfg.contur_log.debug("{} is of type {}. No breakdown".format(ao.path(),ao.type()))
            return False
        if apply_min and (ao.numErrs() if 'Estimate0D' in ao.type() \
                          else min(b.numErrs() for b in ao.bins())) < cfg.min_num_sys:
            return False


        return True

    def _getMatrixAttr(self):
        """
        return true if this AO has a covariance matrix stored in another AO.

        """

        if cfg.diag:
            return False

        self._covname =  cdb.get_covariance_name(self.ao.path())
        if self._covname:
            return True
        else:
            self._corrname =  cdb.get_correlation_name(self.ao.path())
            if self._corrname:
                return True

        return False

    def read_cov_matrix(self,isScaled,aos):
        """
        read the covariance matrix from another AO and return it.
        """

        from contur.factories.yoda_factories import mkConturFriendlyScatter

        if not self.readMatrix:
            self.covM = None
            return

        # if it has alreader been read, don't do it again.
        if self.covM is not None:
            return

        if self._covname:
            is_cov = True
            name = self._covname
            cfg.contur_log.debug("reading covariance matrix {}".format(self._covname))
        else:
            is_cov = False
            name = self._corrname
            cfg.contur_log.debug("reading correlation matrix {}".format(self._corrname))

        # read the covariance matrix into an array.
        matrix_ao = mkConturFriendlyScatter(aos[name])
            
        try:
            # take the number of bins from the measurement
            nbins = self.ao.numPoints()
            nbins2 = int(np.sqrt(matrix_ao.numPoints()))
            # check this is consistent with the matrix
            if nbins != nbins2:
                raise cfg.ConturError("Inconsistent number of entries ({} vs {}) in cov matrix: {}. Will not use it.".format(nbins,nbins2,self._covname))
            self.covM = np.zeros((nbins,nbins))

            i = 0
            j = 0
            for z in matrix_ao.zVals():
                self.covM[i][j] = z
                i=i+1
                if i==nbins:
                    i=0
                    j=j+1
        except:
            cfg.contur_log.error("Failed to read {}".format(self._covname))
            raise

        if not is_cov:
            # need to pre and post muliply by uncertainties
            cfg.contur_log.debug("Converting correlation to covariance. {}".format(self.covM))
            yErrs = np.diag(self.ao.yErrAvgs())
            self.covM = np.dot(yErrs, np.dot(self.covM, yErrs))
            cfg.contur_log.debug("resulting matrix is: {}".format(self.covM))
        elif isScaled:
            # need to scale the covariance.
            self.covM = self.covM * self.scaleFactor * self.scaleFactor


    def buildCovFromBreakdown(self,orig_ao,ignore_corrs):
        """
        Get the covariance, calculated by YODA from the error breakdown
        """
        ana, hist = cutil.splitPath(orig_ao.path())
        path = "/" + ana + "/" + hist
        over  = cdb.use_overflow(path)
        under = cdb.use_underflow(path)
        
        self.covM = np.array(orig_ao.covarianceMatrix(ignoreOffDiagonalTerms=ignore_corrs,includeOverflows=(over or under),
                                                      includeMaskedBins=False,pat_uncorr="^stat|^uncor|Data stat"))

        if over and not under:
            self.covM = self.covM[1:,1:]
        if under and not over:
            self.covM = self.covM[:-1,:-1]
        
    def buildCovFromErrorBar(self):
        """
        Build the diagonal covariance from error bars
        """

        dummyM = np.outer(range(self.nbins), range(self.nbins))
        self.diagonal = np.zeros(dummyM.shape)
        systErrs = np.zeros(self.nbins)

        for ibin in range(self.nbins):
            #symmetrize the errors (be conservative - use the largest!)
            systErrs[ibin] = max(self.ao.point(ibin).errs(self.ao.dim()-1))
            # Note that yoda will take the average (below) when it computes a covariance matrix from the error breakdown.
            # There can also be round errors depending on the precision of the error breakdown.
            #systErrs[ibin] = (abs(self.ao.points()[ibin].yErrs()[0])+abs(self.ao.points()[ibin].yErrs()[1]))*0.5

        self.diagonal += np.diag(systErrs * systErrs)

    def getErrorBreakdown(self):
        """ return the breakdown of (symmetrised) uncertainties """
        return self.errorBreakdown


