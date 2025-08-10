SHELL := /bin/bash
# PWD := $(shell pwd)

DBDIR = data/DB
ANALYSES = data/Rivet
ifndef CONTUR_USER_DIR
	CONTUR_USER=$(HOME)/contur_users
	SHARE=$(CONTUR_USER)
else
	SHARE=$(CONTUR_USER_DIR)
endif

minimal: mkuser $(SHARE)/Rivet-ConturOverload.so $(SHARE) 

no-local-rivet: mkuser nlr

all : mkuser $(SHARE)/Rivet-ConturOverload.so $(SHARE)  webpages doc

$(SHARE)/Rivet-ConturOverload.so : $(wildcard $(ANALYSES)/*.cc)
	$(ANALYSES)/buildrivet.sh

mkuser :
	@echo "INFO: removing $(SHARE) and remaking"
	@if [[ "$(SHARE)" == "$(HOME)" ]] ; then \
	  echo "ERROR: CONTUR_USER_DIR == HOME. export CONTUR_USER_DIR to another path to avoid deleting your home directory!"; \
	  exit 1; \
	fi
    # the path isn't HOME if we got to here
	rm -rf $(SHARE);
	mkdir $(SHARE)

nlr :
	contur-init -l $(CONTUR_USER_DIR)/contur_make.log -o $(SHARE)
	@echo "INFO: You should now source $(SHARE)/analysis-list to update environment variables"	

.PHONY : $(SHARE)
$(SHARE) :
	contur-init -l $(CONTUR_USER_DIR)/contur_make.log -o $(SHARE)
	@echo "INFO: You should now source $(SHARE)/analysis-list to update environment variables"	


.PHONY : doc
doc :
	cd doc && make html
	@echo "HTML docs built at doc/_build/html/index.html"

.PHONY : check
check :
	cd tests && PYTHONDONTWRITEBYTECODE=1 pytest test_batch_submit.py test_data_objects.py test_likelihood_class.py test_combined_likelihood.py test_teardown.py

.PHONY : check-all
check-all :
	cd tests && PYTHONDONTWRITEBYTECODE=1 pytest

.PHONY : check-keep
check-keep :
	rm -rf $(SHARE)/tests
	cd tests && PYTHONDONTWRITEBYTECODE=1 pytest -k 'not teardown_module'

.PHONY : check-deps
check-deps :
	check-contur-deps -V

.PHONY : check-batch
check-batch :
	cd tests && PYTHONDONTWRITEBYTECODE=1 pytest test_batch_submit.py

.PHONY : check-exec
check-exec :
	cd tests && PYTHONDONTWRITEBYTECODE=1 pytest test_executables.py

.PHONY : docclean
docclean :
	@rm -rf doc/_build/html
	@rm -rf doc/_build/doctrees

.PHONY : clean
clean:
	@echo "Removing all generated files"
	@rm -f contur/*.pyc
	@rm -f contur/*/*.pyc
	@rm -f $(ANALYSES)/*.so
	@rm -rf $(SHARE)
	@rm -rf */__pycache__
	@rm -rf */*/__pycache__
	@rm -rf doc/_build/html
	@rm -rf doc/_build/doctrees
	@rm -rf tests/tmp
	@rm -rf tests/sources/tmp

.PHONY : webpages
webpages:
	@echo "Making the dat files for SM comparisons"
	rm -rf $(SHARE)/sm_plots
	contur-smtest -o $(SHARE)/sm_plots -b all
	@echo "Making the webpage measurements listings, and the plots from the dat files"
	contur-init -l $(CONTUR_USER_DIR)/contur_make.log -o $(SHARE) -w
	@echo "Making the sphinx bibliography"
	contur-mkbib --all
	@echo "This should have made the webpage input. Now go to ${CONTUR_WEBDIR}/Sphinx, and make"

.PHONY : webbib
webbib:
	contur-init -l $(CONTUR_USER_DIR)/contur_make.log -o $(SHARE) -w
	@echo "Making the sphinx bibliography"
	contur-mkbib --all

.PHONY : webpages-offline
webpages-offline:
	@echo "Making the dat files for SM comparisons, without inspire-hep info"
	rm -rf $(SHARE)/sm_plots
	contur-smtest -o $(SHARE)/sm_plots -b all --offline
	@echo "Making the webpage measurements listings, and the plots from the dat files"
	contur-init -o $(SHARE) -w  --offline
	@echo "Making the sphinx bibliography"
	contur-mkbib --all --offline
	@echo "This should have made the webpage input. Now go to ${CONTUR_WEBDIR}, and make"

