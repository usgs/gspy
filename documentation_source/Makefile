# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = ./build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	cp -r $(BUILDDIR)/$@/* ../docs

clean:
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

	find ./source -name "*.md5" -type f -delete
	find ./source -name "*.pickle" -type f -delete
	find ./source -name "sg_execution_times.rst" -type f -delete


	find ./source/examples -name "*.ipynb" -type f -delete
	find ./source/examples -name "plot_*.rst" -type f -delete
	find ./source/examples -name "*.h5" -type f -delete
	find ./source/examples -name "*.vtk" -type f -delete
	find ./source/examples -name "*.png" -type f -delete
	find ./source/examples -name "*codeobj*" -type f -delete
	find ./source/examples -name "*.zip" -type f -delete
	find ./source/examples -name "index.rst" -type f -delete
	find ./source/examples/Creating_GS_Files -name "sg_executino_times.rst" -type f -delete
	find ./source/examples/Interacting_With_GS_Files -name "sg_executino_times.rst" -type f -delete


cleanGallery:
	find ./source/examples -name "*.md5" -type f -delete
