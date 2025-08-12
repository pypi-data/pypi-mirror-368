SUBDIR_GOALS=	all clean distclean
SUBDIR+=		utils

MODULES+=	__init__.py
MODULES+=	courses.py
MODULES+=	schedule.py
MODULES+=	signupsheets.py
MODULES+=	hr.py

EXTRAS+=	nytid.hourly.sh
EXTRAS+=	nytid.daily.sh
EXTRAS+=	nytid.weekly.sh
EXTRAS+=	nytid.premonthly.sh
EXTRAS+=	nytid.monthly.sh
EXTRAS+=	nytid-ignore.sh

.PHONY: all
all: ${MODULES} ${EXTRAS}

.INTERMEDIATE: init.py
__init__.py: init.py
	${MV} $< $@

${EXTRAS}: init.nw
	${NOTANGLE}
	chmod +x $@

.PHONY: clean
clean:
	${RM} -R ${MODULES} __pycache__
	${RM} *.tex
	${RM} ${EXTRAS}


INCLUDE_MAKEFILES=../../../makefiles
include ${INCLUDE_MAKEFILES}/noweb.mk
include ${INCLUDE_MAKEFILES}/subdir.mk
