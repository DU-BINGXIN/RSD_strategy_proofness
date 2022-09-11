###########################################################################################################
## VARIABLES
###########################################################################################################

export PWD=`pwd`
export PYTHONPATH=$PYTHONPATH:$(pwd)
export PROJECT_NAME=vaccine_booking_mechanism
export PYTHON=python
export APPLICANT_STRATEGY=Minimax
export SETTING_NAME=settings


###########################################################################################################
## ADD TARGETS FOR YOU TASK
###########################################################################################################

run: ## run simulate RSD
	$(PYTHON) scripts/run.py --setting_name $(SETTING_NAME) --applicant_strategy $(APPLICANT_STRATEGY)

config: ## make setting json file
	$(PYTHON) vaccine_booking/settings/setting_file_creator.py

multi-run:
	for (( i=0; i<10000; i++ )); \
		do \
			$(PYTHON) run.py --setting_name $(SETTING_NAME) --applicant_strategy $(APPLICANT_STRATEGY) --iter $$i; \
		done