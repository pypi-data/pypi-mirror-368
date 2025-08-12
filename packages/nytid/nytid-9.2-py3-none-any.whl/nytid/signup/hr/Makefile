SUBDIR_GOALS=	all clean distclean
SUBDIR+=		timesheet

MODULES+=	__init__.py

.PHONY: all
all: ${MODULES}

.INTERMEDIATE: hr.py
__init__.py: hr.py
	${MV} $^ $@


.PHONY: clean
clean:
	${RM} -R ${MODULES} __pycache__
	${RM} *.tex


INCLUDE_MAKEFILES=../../../../makefiles
include ${INCLUDE_MAKEFILES}/noweb.mk
include ${INCLUDE_MAKEFILES}/subdir.mk
