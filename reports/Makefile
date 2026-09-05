PDF = leanflow_phase12_report.pdf
TEX = leanflow_phase12_report.tex

ENTERPRISE_PDF = leanflow_enterprise_edition_evaluation_report.pdf
ENTERPRISE_TEX = leanflow_enterprise_edition_evaluation_report.tex

.PHONY: all clean enterprise

all: $(PDF) $(ENTERPRISE_PDF)

$(PDF): $(TEX)
	pdflatex -interaction=nonstopmode $(TEX)
	pdflatex -interaction=nonstopmode $(TEX)
	@echo "✅ PDF compiled: $(PDF)"

enterprise: $(ENTERPRISE_PDF)

$(ENTERPRISE_PDF): $(ENTERPRISE_TEX)
	pdflatex -interaction=nonstopmode $(ENTERPRISE_TEX)
	pdflatex -interaction=nonstopmode $(ENTERPRISE_TEX)
	@echo "✅ Enterprise PDF compiled: $(ENTERPRISE_PDF)"

clean:
	rm -f *.aux *.log *.out *.bbl *.blg *.toc *.lof *.lot
