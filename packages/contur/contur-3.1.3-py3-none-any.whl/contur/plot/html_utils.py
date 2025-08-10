import contur.data.static_db as cdb
import os
import contur.config.config as cfg
import contur.util.utils as cutil
import traceback


# some template strings
# stylesheet
stylesheet = '''
    <style>
        html { font-family: sans-serif; font-size: large; }
        img { border: 0; }
        a { text-decoration: none; font-weight: bold; }
        h2 { margin-top: 1.5em; margin-bottom: 1ex; }
        h2:first-child { margin-top: 0em; }

        div.plot{ float: left; margin-right: 40px; font-size:smaller; font-weight:bold;}
        div.pool{ border:1px solid black; background-color:lightblue;}
        div.pool:before,
        div.pool:after {
            content: "";
            display: table;  }
        div.pool:after { clear: both; } 


        div.stattype{ float: left; padding: 5px; }
        div.stattype:before,
        div.stattype:after {
            content: "";
            display: table;  }
        div.stattype:after { clear: both; } 

    </style>
        '''

# Include MathJax configuration
if cfg.offline:
    jax_script = ''
else:        
    jax_script = '''
    <script type="text/x-mathjax-config">
        MathJax.Hub.Config({
        tex2jax: {inlineMath: [["$","$"]]}
        });
    </script>
    <script type="text/javascript"
        src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
    </script>'''


def plot_render_html(file,obsname,analysis,vis=False,size="300"):
    '''
    Constructs an html snippet linking a rivet/contur plot. Writes in to the open file

    arguments:
    :param file: an opened file to write to
    :param obsname: the name of the histogram (last part of the yoda path)
    :param analysis: the analysis the histogram belongs to.
    :type analysis: :class:`contur.data.data_objects.analysis`
    
    '''

    pngfile = obsname + ".png"
    vecfile = obsname + ".pdf"
    srcfile = obsname + ".dat"
    try:
        hname = obsname.split("/")[2]
    except:
        hname = obsname
        
    if vis:
        file.write('    <a href="{{  url_for(\'static\', filename=\'point/%s-%s\')  }}">&#9875;</a><a href="{{  url_for(\'static\', filename=\'point/%s\')  }}">&#8984</a> %s:<br/>\n' %
                    (analysis.poolid+"/"+analysis.name, obsname, srcfile, os.path.splitext(vecfile)[0]))
        file.write('    <a name="%s-%s"><a href="{{  url_for(\'static\', filename=\'point/%s\')  }}">\n' % (analysis.poolid+"/"+analysis.name, obsname, vecfile))
        file.write('      <img src="{{  url_for(\'static\', filename=\'point/%s\')  }}">\n' % pngfile)
    else:

        # anchor link to dat file
        file.write('<a href="{}">{}</a><br/>\n'.format(srcfile,hname))
        # img link to PDF.
        file.write('<a href="{}"> <img width="{}" src="{}"></a>\n'.format(vecfile,size,pngfile))

            
def selectHistogramsForPlotting(histograms,pool_exclusions,CLs,print_only,include_none, have_chi2_plots=False):
    """
    concatenate the histograms dict into a list of python scripts
    that will be executed based on analysis matching and a CLs cut-off

    returns 
    pyScripts = dict of scripts and output directories
    matchedPools, matchedAnalyses
    

    """
    pyScripts = []
    chi2_scripts = []
    matchedAnalyses = {}
    matchedPools = {}
    matchedHistos = {}

    printDict = {}

    # disable plotting/printing of None exclusion histograms if CLs is specified by user
    if CLs > 0.0: include_none=False

    # iterate over pools, analyses and individual histograms
    for pool, analyses in histograms.items():

        if print_only: 
            printDict[pool] = {}
            printThisPool = False
        for analysis, histograms in analyses.items():
            matchedHistos[analysis] = []
            if print_only:
                printDict[pool][analysis] = []
                printThisAna = False

            anadir = os.path.join(cfg.script_dir, pool.id, analysis.name)
            
            for histogram, excl in histograms.items():

                script = os.path.join(anadir, histogram)
                outdir = os.path.join(cfg.plot_dir,pool.id,analysis.name)
                histogram = histogram.split(".py")[0]

                matchedName = cutil.analysis_select(analysis.name) or cutil.analysis_select(analysis.poolid)
                
                if matchedName:
                    cfg.contur_log.debug("argument matches {}".format(script))
                elif not matchedName:
                    cfg.contur_log.debug("argument did not match {}".format(script))

                # None and 0.0 are equivalent here so set None to zero.
                for stat_type, values in excl.items():
                    if excl[stat_type]['CLs'] is None:
                        excl[stat_type]['CLs']=0.0

                # check if any of the dataBG, SMBG or expected match required CLs level
                matchedCLS = False
                if excl.get(cfg.databg): matchedCLS = excl[cfg.databg]['CLs'] > CLs
                if excl.get(cfg.smbg): matchedCLS = (matchedCLS or excl[cfg.smbg]['CLs'] > CLs)
                if excl.get(cfg.expected): matchedCLS = (matchedCLS or excl[cfg.expected]['CLs'] > CLs)

                if matchedName and matchedCLS:
                    if print_only:
                        histostr = "    -- {}(CLs,mu_lower,mu_upper,muhat):".format(histogram)
                        for stat, val in excl.items():
                            histostr+= " {}({:.2f}".format(stat,val['CLs'])
                            if val['mu_lower_limit'] is not None:
                                histostr+= ",{:.2f}".format(val['mu_lower_limit'])
                            if val['mu_upper_limit'] is not None:
                                histostr+= ",{:.2f}".format(val['mu_upper_limit'])
                            else: 
                                histostr+= ",None"
                            if val['mu_hat'] is not None:                                
                                histostr+= ",{:.2f})".format(val['mu_hat'])
                            else: 
                                histostr+= ",None)"
                                
                        printDict[pool][analysis].append(histostr)
                        printThisPool = printThisAna = True
                        continue

                    pyScripts.append([script,outdir])
                    if have_chi2_plots:
                        chi2_scripts.append([script.replace(".py","_chi2.py"),outdir])

                    # store pool/analyses to create and index.html page for those inidivudally
                    if pool not in matchedPools.keys(): matchedPools[pool] = pool_exclusions[pool]
                    # need to store the subpool exclusion here if here is one!
                    if analysis not in matchedAnalyses:
                        matchedAnalyses[analysis] = excl
                    else:
                        try:
                            if excl[cfg.smbg]['CLs'] > matchedAnalyses[analysis][cfg.smbg]['CLs']:
                                matchedAnalyses[analysis][cfg.smbg]['CLs'] = excl[cfg.smbg]['CLs']
                            if cfg.expected in excl and excl[cfg.expected]['CLs'] > matchedAnalyses[analysis][cfg.expected]['CLs']:
                                matchedAnalyses[analysis][cfg.expected]['CLs'] = excl[cfg.expected]['CLs']
                        except:
                            traceback.print_exc()
                            pass

                        if excl.get(cfg.databg): 
                            if excl[cfg.databg]['CLs'] > matchedAnalyses[analysis][cfg.databg]['CLs']:
                                matchedAnalyses[analysis][cfg.databg]['CLs'] = excl[cfg.databg]['CLs']

                    if histogram not in matchedHistos[analysis]: matchedHistos[analysis].append(histogram)

                elif include_none and matchedName:
                    if print_only: 
                        histostr = "    -- " + histogram + f" : no exclusion."
                        if analysis in printDict[pool]: printDict[pool][analysis].append(histostr)
                        printThisPool = printThisAna = True
                        continue
                    pyScripts.append([script,outdir])

                    # store pool/analyses to create and index.html page for those inidivudally
                    if pool not in matchedPools.keys(): matchedPools[pool] = pool_exclusions[pool]
                    if histogram not in matchedHistos[analysis]: matchedHistos[analysis].append(histogram)
                    if analysis not in matchedAnalyses: matchedAnalyses[analysis] = excl

            # prevent plotting analyses that have no histograms passing the tests
            if print_only and not printThisAna: 
                printDict[pool].pop(analysis)

        # prevent plotting pools with no histograms
        if print_only and not printThisPool:
            printDict.pop(pool)

    if print_only:
        for pool, anas in printDict.items():
            cfg.contur_log.info(pool.id)
            for ana, histos in anas.items():
                cfg.contur_log.info("  - " + ana.name)
                for histo in histos:
                    cfg.contur_log.info(histo)
            cfg.contur_log.info(" ")
        exit(0)

    # sort the pools by SM-as-BG exclusion, pushed those with no SM prediction to the bottom of the list.
    matchedPools = {
    k: v 
    for k, v in sorted(
        matchedPools.items(), 
        key=lambda k_v: -float('inf') if k_v[1][cfg.smbg] is None or 'CLs' not in k_v[1][cfg.smbg] 
        else k_v[1][cfg.smbg]['CLs'], 
        reverse=True
    )
    }
    return pyScripts, matchedPools, matchedAnalyses, matchedHistos, chi2_scripts

def writeIndexHTML(matchedPools, matchedAnalyses, matchedHistos, param_point, exclusions, have_chi2_plots=False):

    """
        write index.html to cfg.plot_dir file for contur plots

    """

    # TODO make command-line arguments?
    mainIndexDir = cfg.plot_dir
    
    title     = 'Constraints On New Theories Using Rivet'
        
    # A timestamp HTML fragment to be used on each page:
    from datetime import datetime
    timestamp = '<p>Generated at {}</p>\n'.format(datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))

    # Open the top-level index file
    index = open(os.path.join(mainIndexDir, "index.html"), "w")

    # Write title
    index.write('<html>\n<head>\n<title>{}</title>\n{}\n{}\n</head>\n<body>'.format(title, stylesheet,jax_script))
    hideError = "this.style.display='none'"
    index.write('<h1><a href=\"https://hepcedar.gitlab.io/contur-webpage/\"><img width=10% style="vertical-align:top;" src="{}" onerror="{}"></a>'.format(os.path.join(cfg.paths.data_path(),"data/Plotting/logo.png"), hideError))
    index.write('{}</h1>\n\n'.format(title))

    index.write('<h2>Model point with the following parameters and full exclusions:</h2>\n')
    index.write('<h3>(Note that the exclusion is from all beams found for this point):</h3>\n<p>')

    index.write('<table>')
    index.write('<tr><td style=\"vertical-align:top\"><ul>')

    for name, value in param_point.items():
        index.write('<li>{} = {}</li>\n'.format(name,value))

    index.write('</td><td style=\"vertical-align:top\"><ul>\n')

    if exclusions.get(cfg.smbg):
        index.write('<p>Exclusion with SM as background = {:.2f}%</p>'.format(100.*exclusions.get(cfg.smbg)['CLs']))
        if cfg.expected in exclusions:
            index.write('<p>Expected exclusion  = {:.2f}%</p>'.format(100.*exclusions.get(cfg.expected)['CLs']))
    else:
        index.write('<p>Exclusion with SM as background not calculated.</p>')
    if exclusions.get(cfg.databg):
        index.write('<p>Exclusion with Data as background = {:.2f}%</p>'.format(100.*exclusions.get(cfg.databg)['CLs']))
    else:
        index.write('<p>Exclusion with Data as background not calculated.</p>')
    index.write('</td></tr>\n')    
    index.write('</table>')

    # make sub-index for every analysis pool
    for pool, exclusion in matchedPools.items():
        poolDir = os.path.join(mainIndexDir, pool.id)
        # clickable link from top-level index
        index.write('<hr><h3><a href="{}">{}</a></h3>\n'.format(os.path.join(pool.id, 'index.html'), pool.id))
        # pool description
        index.write('<h4>{}</h4>\n'.format(pool.description))

        if exclusion[cfg.smbg] is not None:
            index.write('<p>Combined exclusion for this pool is {:.1f}% with SM prediction as background.\n<br/>'.format(exclusion[cfg.smbg]['CLs']*100.))
            if cfg.expected in exclusion:
                index.write('(Expected exclusion was {:.1f}%.)\n<br/>'.format(exclusion[cfg.expected]['CLs']*100.))
            gotSMBG = True
        else:
            index.write('<p>No SM prediction available.<br/>')
            gotSMBG = False
        

        if exclusion.get(cfg.databg):
            index.write('Combined exclusion for this pool is {:.1f}% with data used as background estimate.</p>\n'.format(exclusion[cfg.databg]['CLs']*100.))
        else:
            index.write('Data as background exclusion not calculated.</p>\n')
                        
        thisPoolMatchedAnalyses = {}
        for ana, excl in matchedAnalyses.items():
            if ana.get_pool() == pool: thisPoolMatchedAnalyses[ana] = excl            
        thisPoolMatchedAnalyses = {
            k: v
            for k, v in sorted(
                thisPoolMatchedAnalyses.items(),
                key=lambda k_v: -float('inf') 
                if k_v[1].get(cfg.smbg) is None or 'CLs' not in k_v[1][cfg.smbg] 
                else k_v[1][cfg.smbg]['CLs'],
                reverse=True
            )
        }
         
        writePoolHTML(pool, poolDir, thisPoolMatchedAnalyses, exclusion)

        # make sub-index for every analysis
        for ana, excl in thisPoolMatchedAnalyses.items():
            anaDir = os.path.join(poolDir, ana.name)
            writeAnaHTML(ana, excl, anaDir, matchedHistos[ana], have_chi2_plots=have_chi2_plots)

    # close file
    index.write("</ul>")
    index.write('<br>{}</body>\n</html>'.format(timestamp))
    index.close()

def writeAnaHTML(analysis, excl, anaDir, histoList, prediction=None, have_chi2_plots=False):
    """
    write index.html file corresponding to a particular analysis, showing
    the .png of histograms
    """
    
    # make the directory if not there already.
    cutil.mkoutdir(anaDir)

    
    # if a prediction is supplied we assume this is a SM test
    if prediction is not None:
        pid = prediction.id
        up = "../"
    else:
        pid=""
        up = ""
    
    # create index, title and header
    index = open(os.path.join(anaDir, 'index{}.html'.format(pid)), 'w')
    index.write('<html>\n<head>\n<title>{}</title>\n{}\n{}\n</head>\n<body>'.format(anaDir.split('/')[-1], stylesheet,jax_script))
    hideError = "this.style.display='none'"
    index.write('<h1><a href=\"https://hepcedar.gitlab.io/contur-webpage/\"><img width=10% style="vertical-align:top;" src="{}" onerror="{}"></a>'.format(os.path.join(cfg.paths.data_path(),"data/Plotting/logo.png"), hideError))
    
    index.write('<a href=\"https://rivet.hepforge.org/analyses/{}.html\"</a>{}</h1>'.format(analysis.shortname,analysis.name))
    index.write('<p> <a href="../{}index.html">Back to previous page </a></p>\n'.format(up))
    index.write('<h2>{}</h2>'.format(analysis.summary()))
    if prediction is None:
        if cfg.smbg in excl and excl[cfg.smbg] is not None:
            index.write(' <p>Exclusion with SM as background = {:.1f}%.<br/>\n'.format(100.*excl[cfg.smbg]['CLs']))
            if cfg.expected in excl:
                index.write(' Expected exclusion  = {:.1f}%.\n</br>'.format(100.*excl[cfg.expected]['CLs']))
        else:
            index.write(' No SM prediction available ')
            if excl.get(cfg.databg):
                index.write(' Exclusion with data as background = {:.1f}%.\n</br>'.format(100.*excl[cfg.databg]['CLs']))
            else:
                index.write('Exclusion with data as background not calculated.\n</br>')
            
    else: # sm test
        index.write(' <p>Combined p value for this prediction is {:.2f}<p/>\n'.format(excl[cfg.smbg]))

    index.write('<p>Note that the exclusion from the analysis may be the combined exclusion of several independent histograms.</p>\n')
        
    histoList = sorted(histoList)
    
    # iterate over individual histograms
    for histo in histoList:
        index.write('<a href="{}"><img src="{}" alt="{}"></a>'.format(histo+'.pdf', histo+'.png', histo))

        if have_chi2_plots:
            if os.path.isfile(anaDir.replace(cfg.plot_dir,cfg.script_dir)+"/"+histo+'_chi2.py'):
                index.write('<a href="{}"><img src="{}" alt="{}"></a>'.format(histo+'_chi2.pdf', histo+'_chi2.png', histo))
            index.write('<br>\n') # each histo-chi2 pair is side by side

    # close
    index.write('</body>\n</html>') 
    index.close()

def writePoolHTML(pool, poolDir, thisPoolMatchedAnalyses, exclusion):

    from rivet.util import htmlify

    # make the directory if not there already.
    cutil.mkoutdir(poolDir)
        
    # create index, title and header    
    index = open(os.path.join(poolDir, 'index.html'), 'w')
    index.write('<html>\n<head>\n<title>{}</title>\n{}\n{}\n</head>\n<body>'.format(poolDir.split('/')[-1], stylesheet,jax_script))
    hideError = "this.style.display='none'"
    index.write('<h1><a href=\"https://hepcedar.gitlab.io/contur-webpage/\"><img width=10% style="vertical-align:top;" src="{}" onerror="{}"></a>'.format(os.path.join(cfg.paths.data_path(),"data/Plotting/logo.png"), hideError))
    index.write('{}</h1>'.format(poolDir.split('/')[-1]))
    index.write('<p> <a href="../index.html">Back to previous page </a></p>\n')
    index.write('<h2>{}</h2>'.format(pool.description))

    if exclusion[cfg.smbg] is not None:
        index.write('<p>Combined exclusion for this pool is {:.1f}% with SM prediction as background.\n<br/>'.format(exclusion[cfg.smbg]['CLs']*100.))
        if cfg.expected in exclusion:
            index.write('(Expected exclusion was {:.1f}%.)\n<br/>'.format(exclusion[cfg.expected]['CLs']*100.))
    else:
        index.write('<p>No SM prediction available.<br/>')
                        
    if exclusion.get(cfg.databg):
        index.write('Combined exclusion for this pool is {:.1f}% with data use as background estimate.</p>\n<hr>\n'.format(exclusion[cfg.databg]['CLs']*100.))
    else:
        index.write('Data as background exclusion not calculated.</p>\n<hr>\n')
    
    # iterate over individual analyses
    for ana, excl in thisPoolMatchedAnalyses.items():
        if ana.name.endswith('.html'): continue
        index.write('<p><a href="{}">{}</a>:'.format(os.path.join(ana.name, 'index.html'), ana.name))
        index.write(' {}<br/>\n'.format(htmlify(ana.summary())))
        if cfg.smbg in excl and excl[cfg.smbg] is not None:
            index.write(' Exclusion with SM as background = {:.1f}%.</p>\n'.format(100.*excl[cfg.smbg]['CLs']))
        else:
            index.write(' No SM prediction available ')

    # close
    index.write('</body>\n</html>')
    index.close()



def writeAlistHTML(dir,ana_dict):
    """
    write index.html file corresponding to a particular analyses and predictions in the cwd
    """

    # make the directory if not there already.
    cutil.mkoutdir(dir)
    
    # create index, title and header
    index = open(os.path.join(dir,'index.html'), 'w')
    index.write('<html>\n<head>\n<title>{}</title>\n{}\n{}\n</head>\n<body>'.format("List of SM predictions", stylesheet,jax_script))
    hideError = "this.style.display='none'"
    index.write('<h1><a href=\"https://hepcedar.gitlab.io/contur-webpage/\"><img width=10% style="vertical-align:top;" src="{}" onerror="{}"></a>List of SM predictions</h1>'.format(os.path.join(cfg.paths.data_path(),"data/Plotting/logo.png"), hideError))

    index.write("<UL>\n")
        
    # iterate over analysis/prediction pairs
    for filename, pair in ana_dict.items():
        ana = pair[0]
        pred = pair[1]
        try:
            index.write('<LI><a href="{}">{} ({}); {} prediction ID = {}</a></LI>\n'.format(filename,ana.name,ana.summary(),pred.short_description, pred.id))
        except UnicodeEncodeError as ue:
            cfg.contur_log.warn("You have a Unicode error in the text associated with ".format(ana.name))
            print(pred.short_description)
            print(ana.summary())
            traceback.print_exc()
        
    index.write("</UL>\n")
        
    # close
    index.write('</body>\n</html>\n') 
    index.close()
    
