# PyROOT Multi-histogram plotting assistant

This work introduces a code, EventsFillerClass.py, that can take multiple TH1D histograms as an input, classify backgrounds from signals, stack background histograms and show signals invidudally. 

All you need to do is just to books some histograms. Then append them and while appending them you tell the classs its type (signal, background or data), should the class add it to legend or not, and if yes what is the legend name and showing option?

Then the class will internally handel all the histograms and legends. After doing so you tell the class to save the plot in one or mutiple formats. You can also ask the class to save the histograms in a root file for you on the flight! 

This is some code example of how to use the class:


## 1) Initialization & global ROOT configuration

* Instantiates a standalone plotting assistant object with a single constructor call:

  ```py
  plot = PlottingAssistant(x_title="HT", units="GeV", y_title="Events", n_bins=25, x_range=[400,3000])
  ```
* On construction it sets several global ROOT style flags for the process:

  * `ROOT.gROOT.SetStyle("ATLAS")` — applies the ATLAS style (if available).
  * `ROOT.gROOT.SetBatch(True)` — enables batch mode so canvas drawing doesn’t require an X11 display.
  * `ROOT.gStyle.SetOptStat(0)` — disables the default stat box.
  * `ROOT.TGaxis.SetMaxDigits(4)` — configures axis digit formatting.
* Creates and configures the principal ROOT objects required for plotting:

  * a `TCanvas` (default 800×600),
  * a `TLegend` with a standard default position and zero border,
  * a `THStack` configured with the class’s x/y titles,
  * a `TLatex` label object ready for drawing NDC text.
* Computes and stores axis title strings automatically:

  * builds an x-axis title including units: e.g. `"HT [GeV]"`.
  * computes bin width and builds a y-axis title that indicates count per bin width: e.g. `"Events / 104.0 GeV"`.


## 2) Histogram booking and construction

* Provides a simple programmatic way to create ROOT 1D histograms with the configured binning and titles:

  * `hist = plot.book_histogram("hist_name")` → returns a `TH1D(hist_name, title, n_bins, x_min, x_max)`.
* The booked histogram immediately uses the `x_title` and `y_title` strings formatted in the constructor (no extra user work needed).


## 3) Styling / design of histograms

* Offers a single method to apply common style properties to an individual histogram:

  * `plot.design_histogram(hist, line_color=..., line_style=..., line_width=..., fill_color=..., fill_style=...)`
  * Each supplied property is set if provided, using the standard ROOT `SetLineColor`, `SetLineStyle`, `SetLineWidth`, `SetFillColor`, `SetFillStyle` calls.

## 4) Appending histograms and classification

* Appends booked or externally-created histograms to the assistant and classifies them as background, signal or data at append time:

  * `plot.append_histogram(hist, weight=1.0, is_signal=False, is_background=False, is_data=False, show_legend=False, legend_name="")`
  * Behavior when appending:

    * scales the histogram by `weight` (`TH1::Scale`),
    * if `is_background=True` the histogram is added to `stacked_histograms`,
    * if `is_signal=True` or `is_data=True` it is added to `single_histograms`,
    * optionally creates a legend entry when `show_legend=True` using `legend.AddEntry(hist, legend_name, option)`.
* Automatic legend option selection:

  * background histograms get fill-style legend entries (`"f"`),
  * signal/data histograms get line-style legend entries (`"l"`).
* Tracks and logs (when verbose is enabled) bookkeeping info on each append:

  * histogram maximum,
  * cumulative stacked-histograms height metric,
  * current global peak used for plotting (`y_peak`).


## 5) Two stacking modes (flexible stack strategy)

* Supports two ways to build the background stack, selectable at runtime:

  * **Immediate stacking** (`_stack_in_order = False`): appended background histograms are added to the `THStack` immediately.
  * **Deferred ordered stacking** (`_stack_in_order = True`): background histograms are collected and then ordered by integral and added to the `THStack` at draw time. This allows consistent ordering (small → large) for readable stacked plots.
* The user can toggle ordering behavior at initialization or later via `plot.stack_in_order(True/False)`.


## 6) Automated axis scaling and log-scale support

* Automatically computes a plotting y-range candidate (`y_peak`) from appended histograms to select a suitable upper axis limit when drawing.
* Supports drawing with a logarithmic Y axis:

  * `plot.set_logy(True)` sets the canvas to log-y and adjusts a lower y bound to avoid zeros.
  * When log is enabled, a minor axis formatting step is applied (`SetNdivisions(...)`) for the x-axis in the drawing helper to keep ticks readable.


## 7) Drawing and rendering workflow

* Centralized drawing method `plot.draw_plot(plot_name, formats=["pdf","tex"])` that:

  * builds/arranges the THStack and draws it to the canvas with desired draw options,
  * draws single histograms on top of the stack using `same`,
  * draws legends and any NDC LaTeX labels stored via `add_label(...)`,
  * chooses and sets axis range extremes using the current `y_peak` and `y_log` values,
  * saves the canvas to one or more file formats: if `plot_name` already carries an extension it saves once; otherwise it saves multiple files with provided extensions (e.g. `plot.draw_plot("figure", ["pdf","png"])` → `figure.pdf`, `figure.png`).
* Draw option toggles:

  * internal logic supports switching between a minimal default drawing option string and an alternate string when auto-coloring is enabled (the code assembles option tokens for `THStack.Draw` and `TH1.Draw`).

## 8) Legend and label utilities

* Legend configuration methods:

  * `plot.set_legend_position(x1, y1, x2, y2, text_size)` sets legend box coordinates and text size,
  * `plot.set_legend_ncols(n)` controls the number of columns in the legend.
* Add arbitrary NDC LaTeX text labels:

  * `plot.add_label(x1, y1, label, text_size)` stores a label; `draw_plot` will draw every stored label with `TLatex.DrawLatex`.
  * Useful for experiment text, luminosity, selection stage notes, etc.

## 9) Histogram analysis and diagnostics

* Provides a detailed histogram inspection routine `analyze_histogram(hist)` that:

  * reports underflow and overflow bin content and errors,
  * prints total entries, weighted integral (including under/overflow) and total in-range integral,
  * prints per-bin content, absolute error and relative error percentage for the full bin range.
* The analysis step is optional and can be enabled for verbose diagnostics; when enabled this method runs automatically on appended histograms.

## 10) ROOT file export / combined background export

* Saves all appended histograms into a ROOT file via `save_histograms(root_file_name)`:

  * writes every histogram stored in `self.histograms` by calling `hist.Write()`,
  * constructs a combined background histogram `h_bkg` by cloning the first stacked histogram and adding all others to it, and writes that combined `h_bkg` into the same ROOT file — providing easy access to the total background distribution from the single output file.


## 11) Memory and resource management

* `clean_memory()` attempts to free/create a clean process state by:

  * deleting all histograms that were created or appended and stored in the assistant,
  * deleting the internal `THStack` and `TLegend`,
  * closing the `TCanvas`,
  * calling `gc.collect()` to prompt Python garbage collection.
* This supports scripts that create multiple PlottingAssistant instances in sequence and need to reclaim resources.


## 12) Use-cases and recommended scenarios

* Quick publication plots from a ROOT-based analysis where:

  * several background processes must be stacked,
  * a few signal processes are overlaid as lines,
  * common experiment text (energy, luminosity, selection stage) is added via LaTeX labels.
* Automated plot pipelines:

  * book histograms for each process programmatically, fill them from `TTree::Draw` calls, append to the assistant, and call `draw_plot` in a batch job to produce many figures.
* Diagnostic runs:

  * enable histogram analysis and verbose output to inspect underflow/overflow and per-bin relative errors across multiple histograms.


