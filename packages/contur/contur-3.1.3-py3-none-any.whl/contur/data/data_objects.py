import contur
import numpy as np
import sys
#from contur.util.utils import hack_journal
import contur.config.config as cfg
import contur.data.static_db as cdb

''' 
Module containing python classes which map on to tables in the analysis database.

Many of these are simple structs containing one row from the table per object, with little or no internal functionality.
'''

class Pool:
    """ 
    Class to store information about analysis pools

    Properties:

    * **id** the short string identifying the pool
    * **beamid** the unique ID of the colliding beam type this pool is associated with
    * **description** a short human-readable description of the final state this pool contains.

    """
    def __init__(self, row):
        self.id = row[0]
        self.beamid = row[1]
        self.description = row[2]

class Beam:
    """ 
    Class to store information about beam configurations  

    Properties:

    * **id**
    * **collider** short string identifying the collider
    * **particle_a** short string identifying the first colliding beam
    * **particle_b** short string identifying the second colliding beam
    * **energy_a** energy of first beam
    * **energy_b** energy of second beam
    * **root_s** centre-of-mass energy

    """
    def __init__(self, row):
        self.id = row[0]
        self.collider = row[1]
        self.particle_a = row[2]
        self.particle_b = row[3]
        self.energy_a = row[4]
        self.energy_b = row[5]
        self.root_s = np.sqrt((self.energy_a+self.energy_b)**2 - (self.energy_b-self.energy_a)**2)

class Experiment:
    """ 
    Class to store information about experiments

    Properties:

    * **id**
    * **collider** short string identifying the collider

    """
    def __init__(self, row):
        self.id = row[0]
        self.collider = row[1]

class Analysis:
    """ 
    Class to store information about an analysis.

    Properties:

    * **name** full name of the analysis, including the options string if present
    * **short_name** as above but without the options string
    * **lumi** the integrated luminosity used for this analysis
    * **rivet_analysis** the rivet analysis object
    * **poolid** the unique ID of the contur pool this analysis belongs to

    """
    def __init__(self,row,beamid):
            
        import rivet
        
        self.name, self.poolid = row
        self.beamid = beamid
        self.shortname = rivet.stripOptions(self.name)
        self.rivet_analysis = rivet.AnalysisLoader.getAnalysis(self.shortname)
        if self.rivet_analysis is None:
            if cfg.contur_log is not None:
                cfg.contur_log.warning(
                    "Could not find {} in your Rivet install. Update Rivet, or add analysis to the data/Rivet directory".format(self.name))
            else:
                print("WARNING: Could not find {} in your Rivet install. Update Rivet, or add analysis to the data/Rivet directory".format(self.name))
            raise cfg.ConturError("Missing Analysis")
            #            sys.exit(1)
            
        self.inspireId = self.rivet_analysis.inspireId()
        self._paper_data = None
        self.summary = self.rivet_analysis.summary
        
    def get_pool(self):
        """
        return the pool object associated with this analysis.
        """
        return cdb.get_pool(poolid=self.poolid)

    def bibkey(self):
        """
        return the bibtex key of this analysis
        """
        if self._paper_data is None:
            self._paper_data = contur.util.utils.get_inspire(self.inspireId)                
        return self._paper_data['bibkey']

        
    def bibtex(self):
        """
        return the bibtex of this analysis
        """
        if self._paper_data is None:
            self._paper_data = contur.util.utils.get_inspire(self.inspireId)
        return contur.util.utils.hack_journal(self._paper_data['bibtex'])
    
    def sm(self):
        """
        return a list of the SM theory descriptions associated with this analysis (if any)
        """
        return cdb.get_sm_theory(self.name)

    def experiment(self):
        return self.rivet_analysis.experiment()

    def hasPrediction(self):
        if cdb.get_sm_theory(self.name) is not None:
            return True
        return False

    def toHTML(self,anaindex,adatfiles=[],style="",timestamp="now"):
        """
        Write this analysis to an HTML file called anaindex, with link links to the graphics version
        of the plots in adatfiles. If adatafiles is empty, just write the description etc
        without links to plots.

        optional stylesheet and timestamp.

        to be deprecated in favour of html_utils.writeAnaHTML

        """
        
        from rivet.util import htmlify
        import os
        
        references = []

        ana = self.rivet_analysis

        summary = htmlify("{}".format(self.summary()))
        references = ana.references()

        description = htmlify(ana.description())

        reflist = []
        inspireurl = "http://inspirehep.net/literature/{}".format(self.inspireId)
        reflist.append('<a href="{}">Inspire record</a>'.format(inspireurl))
        reflist += references

        anaindex.write('<html>\n<head>\n')
        anaindex.write('<title>Pool {} &ndash; {}</title>\n'.format(self.name, self.poolid) )
        anaindex.write(style)
        anaindex.write('</head>\n<body>\n')

        anaindex.write('<h1>{}</h1>\n <h3>{} in analysis pool {}</h3>'.format(summary,self.name,self.poolid))

#        anaindex.write('<h2>{} in pool {}</h2>\n'.format(htmlify(self.name), self.poolid))
        anaindex.write('<p><a href="../../index.html">Back to index</a></p>\n')
        if description:
            try:
                anaindex.write('<p style="max-width:60em;">\n  {}\n</p>\n'.format(description))
            except UnicodeEncodeError as ue:
                print("Unicode error in analysis description for " + self.name + ": " + str(ue))
        else:
            anaindex.write('<p>\n  No description available \n</p>\n')

        anaindex.write('<div>\n')

        anaindex.write('<p>%s</p>\n' % " &#124; ".join(reflist))

#        anaindex.write('  <p><a href="{}">Inspire record</a></p>\n'.format(inspireurl))

        anaindex.write("  </br>\n\n")

        for datfile in sorted(adatfiles):
            obsname = os.path.basename(datfile).replace(".dat", "").rstrip()

            anaindex.write('  <div style="float:left; font-size:smaller; font-weight:bold;">\n')
            contur.plot.html_utils.plot_render_html(anaindex,obsname,self)                
            anaindex.write('  </div>\n')

        anaindex.write('\n<div style="clear:both" />\n')
        anaindex.write('</div>\n')
        anaindex.write('<div>{}</body>\n</html></div>\n'.format(timestamp))
        anaindex.close()

    

class SMPrediction:
    """ 
    Class to store information about SM predictions

    Properties

    Prediction metadata: (populated from the analysis DB)

    * **id** short string which, together with the analysis name, identifies this prediction
    * **a_name** the analysis name, including any options string
    * **inspids** inspire IDs of the theory references
    * **origin** short description of where the prediciton was obtained  
    * **pattern** regexp. prediction applies to all measurements in this analysis whose name matches this (Only used when making the files in /Theory)
    * **axis** the name of the axis to take the theory from, if coming from a HEPData record. The record used will be the one where the end of the HEPData path matches this (Only used when making the files in /Theory)
    * **file_name** the name of the file the prediction is stored in, in the /Theory directory. 
    * **short_description** for plot legends 
    * **long_description** for web pages, does not need to repeat the short description

    Prediction data: (Populated when the prediction data are read in from the file)

    * **ao** :dict: of yoda analysis objects keyed by name
    * **plotObj** :dict: of plot objects keyed by name
    * **corr** :dict: of correlation matrices keyed by name
    * **uncorr** :dict: of diagonal error matrices keyed by name
    * **errors** :dict: of error breakdowns  keyed by name

    """
    def __init__(self, row):
        self.id      = row[0]
        self.a_name  = row[1]
        self.inspids = row[2]
        self.origin  = row[3]
        self.pattern = row[4]
        self.axis    = row[5]
        self.file_name = row[6]
        self.short_description = row[7]
        self.long_description  = row[8]
        self.ao = {}
        self.plotObj = {}
        self.corr = {}
        self.uncorr = {}
        self.errors = {}
        
