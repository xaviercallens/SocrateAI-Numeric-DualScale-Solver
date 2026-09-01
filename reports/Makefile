PDF = leanflow_phase12_report.pdf
TEX = leanflow_phase12_report.tex

.PHONY: all clean

all: $(PDF)

$(PDF): $(TEX)
	pdflatex -interaction=nonstopmode $(TEX)
	pdflatex -interaction=nonstopmode $(TEX)
	@echo "✅ PDF compiled: $(PDF)"

clean:
	rm -f *.aux *.log *.out *.bbl *.blg *.toc *.lof *.lot
