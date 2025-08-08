# icplot

This is a library used at [The Irish Centre for High End Computing (ICHEC)](https://www.ichec.ie) for generating plots and graphics for technical documents.

# Features #

The project has support for:

* Coverting image formats between pdf, svg and png
* Building pdf and png output from tex files, including tikz.
* Generating plots based on a serializable data model to support reproducible research
* Generating mermaid plots

To covert between image formats you can do:

``` shell
icplot convert --source my_image.svg --target my_image.png
```

To render a Tex tikz image as pdf and png you can do:

``` shell
icplot convert --source my_tikz.tex
```

To render a Mermaid plot as png you can do:

``` shell
icplot convert --source my_mermaid.mmd
```

To generate a plot or collection of plots from a yaml description you can do:

``` shell
icplot plot --config my_plot.yml
```

# Installation #

The package is available on PyPI. For a minimal installation you can do:

``` shell
pip install icplot
```

For full functionality, particularly conversion of image formats, `imagemagick` and `cairo` are required. On Mac you can install them with:

``` shell
brew install imagemagick cairo
```

# Copyright #

Copyright 2024 Irish Centre for High End Computing

The software in this repository can be used under the conditions of the GPLv3+ license, which is available for reading in the accompanying LICENSE file.

