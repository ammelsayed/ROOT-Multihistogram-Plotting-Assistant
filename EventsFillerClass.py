

## -------------------------------------------------------------------------- ##
##    Author:    A.M.M Elsayed                                                ##
##    Email:     ahmedphysica@outlook.com                                     ##
##    Institute: University of Science and Technology of China                ##
## -------------------------------------------------------------------------- ##                        
##    A powerful tool for working with TH1D objects,                          ##
##    distinguishing backgrounds from signals, stacking                       ##
##    background histograms, and visualizing signals                          ##
##    individually in an automatic way.                                       ##
##                                                                            ##
##    Updates On:                                                             ##
##    https://github.com/ammelsayed/ROOT-Multihistogram-Plotting-Assistant    ##
## -------------------------------------------------------------------------- ##


import ROOT
import gc, os
import numpy as np


from rich.console import Console
console = Console()

def title(string = "", print = True):
    if print:
        console.print("\n######",string, "######\n", style="green")
    else:
        pass

def proc_title(string = "", print = True):
    if print:
        console.print(">>>>", string, "<<<<", style="blue")
    else:
        pass

def msg(string = "", print = True):
    if print:
        console.print("[INFO]", string, style="white")
    else:
        pass    
    
def err_msg(string = "", print = True):
    if print:
        console.print("[WARN]", string, style="red")
    else:
        pass


## Main Class
class PlottingAssistant:

    def __init__(self, 
                 x_title : str = "",
                 units : str = "",
                 y_title : str = "Events",
                 n_bins : int = 25,
                 x_range : list = None
                ):

        # Style settings 
        ROOT.gROOT.SetStyle("ATLAS")
        ROOT.gROOT.SetBatch(True) 
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetHatchesSpacing(1)
        ROOT.gStyle.SetHatchesLineWidth(2)
        ROOT.TGaxis.SetMaxDigits(4)

        # Intial colors setting
        ROOT.gStyle.SetPalette(ROOT.kBird) # kBird / kViridis
        ROOT.gStyle.SetNumberContours(15)
        self.auto_chose_colors_ = True

        # histogram titles 
        if not (len(x_range) == 2 and (x_range[0] > x_range[1])):
            self.x_range = x_range
            self.x_min, self.x_max = self.x_range
        else:
            err_msg("'x_range' must be a list of two numbers, with X1 > X0")
            raise TypeError(f"x_range must be a list of two numbers, with X1 > X0 {type(n_bins)}")

        if not isinstance(n_bins, int):
            raise TypeError(f"n_bins must be int, got {type(n_bins)}")
        
        self.n_bins = n_bins
        self.units = units
        self.x_title = f"{x_title} [{self.units}]" if self.units != "" else f"{x_title}"
        self.bin_width = round((self.x_max -self.x_min)/self.n_bins, 1)
        self.y_title = f"{y_title} / {self.bin_width} {self.units}" if self.units != "" else f"{y_title} / {self.bin_width}"
        self._show_hist_analysis = True
        self.verbose_mode = True

        # class
        self.histograms = []
        self.single_histograms = []
        self.stacked_histograms = []
        self.y_log = False
        self.y_peak = 0
        self.read_histograms_from_root = False
        unique = str(id(self))
        title(f"Plotting Assisting Activated [Unique ID: {unique}].", print = self.verbose_mode)
        msg(f"X Tile: '{self.x_title}'", print = self.verbose_mode)
        msg(f"Y Title: '{self.y_title}'", print = self.verbose_mode)
        msg(f"Range of all histogram = [{self.x_min}, {self.x_max}] {self.units}, with {self.n_bins} bins.\n", print = self.verbose_mode)

        # Initial Canvas Settings
        self.canvas = ROOT.TCanvas(
            f"Canvas_{unique}",
            f"Canvas_{unique}"
        )
        self.canvas.SetCanvasSize(800, 600)
        self.save_formats = ["pdf"]

        # Initial Legends Settings
        self.legend_bkg = ROOT.TLegend(0.60, 0.65, 0.95, 0.90)
        self.legend_bkg.SetName(f"legend_sig_{unique}")
        self.legend_bkg.SetNColumns(2)
        self.legend_bkg.SetBorderSize(0)
        self.legend_bkg.SetFillStyle(0)
        self.legend_bkg.SetTextSize(0.035)
        self.num_of_legends_bkg = 0
        self.bkg_histograms_legends = []

        self.legend_sig = ROOT.TLegend(0.60, 0.55, 0.90, 0.65)
        self.legend_sig.SetName(f"legend_sig_{unique}")
        self.legend_sig.SetNColumns(1)
        self.legend_sig.SetBorderSize(0)
        self.legend_sig.SetFillStyle(0)
        self.legend_sig.SetTextSize(0.034)
        self.num_of_legends_sig = 0
        self.sig_histograms_legends = []

        # Inital Stacked Histograms settings
        # Only used if is_background = True
        self.stack = ROOT.THStack(
            f"Stack_{unique}",
            f"Stack_{unique}; {self.x_title}; {self.y_title}"
        )
        # The order is addiving histograms with less events
        # into the stacked histogram first
        self._stack_in_order = True
        self.stacked_histograms_height = 0

        # Initial Labels settings
        self.label = ROOT.TLatex()
        self.label.SetTextFont(42)
        self.label.SetNDC()
        self.labels = []
    
    def disable_verbose_mode(self, option : bool) -> None:
        self.verbose_mode = option

    def show_hist_analysis(self, option : bool) -> None:
        self._show_hist_analysis = option

    def auto_chose_colors(self, option : bool) -> None:
        self.auto_chose_colors_ = option
    
    def stack_in_order(self, option : bool) -> None:
        self._stack_in_order = option
        
    def add_label(self, x1 = 0.20, y1 = 0.80, label = "", text_size = 0.045) -> None:
        self.labels.append({
            "x1"        : x1,
            "y1"        : y1,
            "label"     : label,
            "text_size" : text_size
        })
        
    def set_canvas_size(self, width, height) -> None:
        try:
            self.canvas.SetCanvasSize(width, height)
            msg(f"Canvas size was set to {width} * {height}", print = self.verbose_mode)
        except Exception as e:
            err_msg(f"Could not set canvas size to {width} * {height} due to the error {e}")

    def set_legend_ncols(self,n) -> None:
        try:
            self.legend_sig.SetNColumns(n)
            msg(f"Legend number of columns was set to {n}", print = self.verbose_mode)
        except Exception as e:
            err_msg(f"Could not set legend NColumns (={n}) due to the error {e}")

    def set_legend_position(self, x1 = 0.63, y1 = 0.60, x2 = 0.92, y2 = 0.90, text_size = 0.025) -> None:

        try:
            self.legend_sig.SetX1(x1)  # Left coordinate
            self.legend_sig.SetY1(y1)  # Bottom coordinate  
            self.legend_sig.SetX2(x2)  # Right coordinate
            self.legend_sig.SetY2(y2)  # Top coordinate
            self.legend_sig.SetTextSize(text_size)
            msg("Legend positon and size set successfully.", print = self.verbose_mode)
        except Exception as e:
            err_msg(f"Could not set the legend position due to the error {e}")

    def auto_place_legend(self, bool = False):
        """
        This part of code automatically study the amount of text in the legend and the best place to place the legend.
        """
        pass

    def book_histogram(self, hist_name = ""):
        proc_title(f"Booking Histogram '{hist_name}'", print = self.verbose_mode)
        try:
            hist_title = f"hist_title; {self.x_title}; {self.y_title}"
            hist = ROOT.TH1D(hist_name, hist_title, self.n_bins, self.x_min, self.x_max)
            msg(f"The histogram was booked successfully.", print = self.verbose_mode)
        except Exception as e:
            err_msg(f"Could not book the histogram due to the error: {e}")

        return hist

    def analyze_histogram(self, hist) -> None:

        """Complete analysis of a histogram"""
        
        nbins = self.n_bins
              
        # Underflow/Overflow
        underflow = hist.GetBinContent(0)
        underflow_error = hist.GetBinError(0)
        overflow = hist.GetBinContent(nbins + 1)
        overflow_error = hist.GetBinError(nbins + 1)
        
        msg("UNDERFLOW/OVERFLOW:")
        msg(f"Underflow (bin 0): {underflow} ± {underflow_error}")
        msg(f"Overflow (bin {nbins + 1}): {overflow} ± {overflow_error}")
        
        # Totals
        total_entries = hist.GetEntries()
        total_weighted = hist.Integral(0, nbins + 1)  # All bins including under/overflow
        total_in_range = hist.Integral()  # Only regular bins
        
        msg("TOTALS:")
        msg(f"Total entries: {total_entries}")
        msg(f"Total weighted events (all bins): {total_weighted}")
        msg(f"Total in range (regular bins only): {total_in_range}")
        
        # Detailed bin information
        msg("DETAILED BIN INFORMATION:")
        msg("Bin\tContent\t\tAbs. Error\tRel. Error (%)")
        for i in range(1, nbins + 1):
            content = hist.GetBinContent(i)
            error = hist.GetBinError(i)
            if content > 0:
                relative_error = (error / content) * 100
            else:
                relative_error = 0
        
            msg(f"{i}\t{content:.6f}\t{error:.6f}\t{relative_error:.2f}%")
    
    def append_histogram(self, hist,
        weight        = 1.0, 
        is_signal     = False,
        is_background = False,
        is_data       = False,
        show_legend   = False, 
        legend_name   = "" ) -> None:

        name = hist.GetName()

        # Dealing with historgam:
        hist.Scale(weight)
        # hist.Sumw2() # optional

        hist_height = hist.GetMaximum()

        # If hist is background "auto" stack
        if is_background == True:
            try:
                self.stacked_histograms.append(hist)
                msg(f"This histogram was deticated for a 'Background' process.", print = self.verbose_mode)

                # Don't add to stack here when stack_in_order=True
                if not self._stack_in_order:
                    self.stack.Add(hist)
                    msg("The histogram was stacked successfully.", print = self.verbose_mode)
                else:    
                    err_msg(f"Background histogram queued for stacking.", print=self.verbose_mode)
                    err_msg(f"Ordered stacking process will take place while plotting.", print=self.verbose_mode)
                
                # calculate total stacked histograms height
                self.stacked_histograms_height += hist_height

                # directly add the legend
                if show_legend == True:
                    try:
                        # self.legend_bkg.AddEntry(hist, legend_name, "f")

                        self.bkg_histograms_legends.append({
                            "hist" : hist,
                            "legend" : legend_name
                        })

                        self.num_of_legends_bkg += 1
                        msg(f"Legend of the historgam was add successfully.", print = self.verbose_mode)
                    except Exception as e:
                        err_msg(f"Could not draw legend of the histogram. Returning the error: {e}")
                
            except Exception as e:
                err_msg(f"Could not append the histogram. Returning the error: {e}")
        else:
            try:
                _type = "Signal" if is_signal == True else "Data"
                self.single_histograms.append(hist)
                msg(f"This histogram was deticated for a '{_type}' process.", print = self.verbose_mode)
            except Exception as e:
                err_msg(f"Could not append the histogram. Returning the error: {e}")
            
            # directly add the legend
            if show_legend == True:
                try:
                    self.legend_sig.AddEntry(hist, legend_name, "l")

                    # self.sig_histograms_legends.append({
                    #         hist : legend_name
                    # })
                    
                    self.num_of_legends_sig += 1
                    msg(f"Legend of the historgam was add successfully.", print = self.verbose_mode)
                except Exception as e:
                    err_msg(f"Could not draw legend of the histogram. Returning the error: {e}")
        
        # # "Auto" fill the legends
        # # Can be used if you want to inlucde a third legend
        # if show_legend == True:
        #     try:
        #         show_option = "f" if is_background == True else "l"
        #         self.legend.AddEntry(hist, legend_name, show_option)
        #         self.num_of_legends += 1
        #         msg(f"Legend of the historgam was add successfully.", print = self.verbose_mode)
        #         msg(f"Legend drawing option = '{show_option}'", print = self.verbose_mode)
        #     except Exception as e:
        #         err_msg(f"Could not draw legend of the histogram. Returning the error: {e}")
        
        ## Getting maximum
        msg(f"Highest point of this histogram: {hist_height} (events)", print = self.verbose_mode)
        msg(f"Total highest point stacked histograms: {self.stacked_histograms_height} (events)", print = self.verbose_mode)  
        try:
            try:
                y_peak_stack = self.stack.GetMaximum()
            except Exception as e:
                y_peak_stack = self.stacked_histograms_height

            y_peak = max(y_peak_stack, hist_height)
            if y_peak > self.y_peak:
                self.y_peak = y_peak
            
            msg(f"Current highest peak among all appeneded histograms is {self.y_peak}.", print = self.verbose_mode)
        except Exception as e:
            err_msg(f"Could not run y maxima calculations due to the error: {e}")

        ## Priniting out some data about the histogram
        if self._show_hist_analysis:
            self.analyze_histogram(hist)

        self.histograms.append(hist)
    
    def fill_from_file(self, root_file_path) -> None:
        pass

    def design_histogram(self, hist, 
        line_color = None,
        line_style = None,
        line_width = None,
        fill_color = None, 
        fill_style = None ) -> None:
        
        if line_color != None:
            hist.SetLineColor(line_color)
        if line_style != None:
            hist.SetLineStyle(line_style)
        if line_width != None:
            hist.SetLineWidth(line_width)
        if fill_color != None:
            hist.SetFillColor(fill_color)
        if fill_style != None:
            hist.SetFillStyle(fill_style)

    def save_histograms(self, root_file_name) -> None:

        proc_title("Saving The Histograms", print = self.verbose_mode)

        root_file = ROOT.TFile(root_file_name, "RECREATE")
        if self.histograms != []:
            for hist in self.histograms:
                try:
                    name = hist.GetName()
                    hist.Write()
                    msg(f"The histogram '{name}' was saved successfully in '{root_file_name}'.", print = self.verbose_mode)
                except Exception as e:
                    err_msg(f"The histogram '{name}' was not saved in '{root_file_name}' due to the Error: {e}.")

        if self.stacked_histograms != []:
            bkg_total = None
            for hist in self.stacked_histograms:
                if bkg_total is None:
                    bkg_total = hist.Clone('h_bkg')
                    bkg_total.SetDirectory(root_file)
                else:
                    bkg_total.Add(hist)
            try:
                if bkg_total:
                    bkg_total.Write()
            except Exception as e:
                err_msg(f"Could not save the stacked histogram in '{root_file_name}' due to the Error: {e}.")

        root_file.Close()
        
    def make_bkg_total_with_uncertainty(self, per_proc_sys_fracs=None, lumi_frac=0.0, shape_variations=None):
        """
        per_proc_sys_fracs: list of arrays (length nbins) — fractional uncorrelated sys per process
        shape_variations: list of tuples per process [(h_up, h_down), ...] or None
        lumi_frac: scalar fractional correlated normalization uncertainty
        Returns: (bkg_total_TH1, bkg_total_TGraphErrors)
        """
        nbins = self.stacked_histograms[0].GetNbinsX()
        # 1) build nominal total
        bkg_total = self.stacked_histograms[0].Clone("bkg_total")
        for h in self.stacked_histograms[1:]:
            bkg_total.Add(h)

        # Ensure Sumw2 present
        bkg_total.Sumw2()

        # 2) start covariance (diagonal) with statistical variances:
        cov_diag = [bkg_total.GetBinError(i+1)**2 for i in range(nbins)]

        # 3) uncorrelated per-process fractional sys
        if per_proc_sys_fracs:
            for p_h, p_frac in zip(self.stacked_histograms, per_proc_sys_fracs):
                for i in range(1, nbins+1):
                    Ni = p_h.GetBinContent(i)
                    cov_diag[i-1] += (p_frac[i-1] * Ni)**2

        # 4) shape variations (up/down): add in quadrature (uncorrelated across processes)
        if shape_variations:
            for (h_up, h_down), p_h in zip(shape_variations, self.stacked_histograms):
                for i in range(1, nbins+1):
                    nom = p_h.GetBinContent(i)
                    d_up = h_up.GetBinContent(i) - nom
                    d_down = nom - h_down.GetBinContent(i)
                    delta = max(abs(d_up), abs(d_down))  # envelope; choose method you prefer
                    cov_diag[i-1] += delta*delta

        # 5) correlated lumi
        if lumi_frac and lumi_frac > 0:
            for i in range(1, nbins+1):
                tot = bkg_total.GetBinContent(i)
                cov_diag[i-1] += (lumi_frac * tot)**2

        # 6) set bin errors in the TH1D object
        for i in range(1, nbins+1):
            bkg_total.SetBinError(i, (cov_diag[i-1])**0.5)
        
        # 7) Create the TGraphErrors object for the error band
        x_values = []
        y_values = []
        x_errors = [] # Half bin width for the horizontal uncertainty
        y_errors = [] # Calculated total uncertainty
        
        for i in range(1, nbins + 1):
            x_values.append(bkg_total.GetBinCenter(i))
            y_values.append(bkg_total.GetBinContent(i))
            x_errors.append(bkg_total.GetBinWidth(i) / 2.0)
            y_errors.append(bkg_total.GetBinError(i))

        # Convert lists to C-type arrays required by TGraphErrors constructor
        from array import array
        ax = array('d', x_values)
        ay = array('d', y_values)
        aex = array('d', x_errors)
        aey = array('d', y_errors)

        # Create the TGraphErrors
        bkg_gr_errors = ROOT.TGraphErrors(nbins, ax, ay, aex, aey)
        bkg_gr_errors.SetName("bkg_total_errors")
        bkg_gr_errors.SetTitle("Background Total with Uncertainty")

        # 8) Set style for the TGraphErrors so it can be drawn directly
        # E2 option with TGraphErrors draws a shaded area for the error bars only
        bkg_gr_errors.SetFillStyle(3004) # Hatched style
        bkg_gr_errors.SetFillColor(ROOT.kBlack)
        bkg_gr_errors.SetMarkerStyle(0) # No markers
        bkg_gr_errors.SetLineWidth(2)
        bkg_gr_errors.SetLineColor(ROOT.kBlack) # Line color for the top/bottom edges of the band

        return bkg_total, bkg_gr_errors

    def draw_plot(self, plot_name) -> None:

        proc_title("Drawing The Plot", print = self.verbose_mode)

        # setting good y-max:
        y_max = self.y_peak * 1e5 if self.y_log else self.y_peak * 3
        y_min = 5e-1 if self.y_log else 0

        def x_div(hist):
            if self.y_log:
                hist.GetXaxis().SetNdivisions(1010, ROOT.kTRUE)
            else:
                pass

        self.canvas.cd()
        if self.stacked_histograms != []: 

            # add histograms by order of smallest (in total events number) to highers
            # if use this option remove self.stack.Add(hist) from append_histogram() function
            if self._stack_in_order:
                try:

                    for hist in sorted(self.stacked_histograms, key=lambda h: h.Integral()):
                        self.stack.Add(hist)
                    
                    for item in sorted(self.bkg_histograms_legends, key=lambda item: item["hist"].Integral(), reverse =  True):
                        self.legend_bkg.AddEntry(item["hist"], item["legend"], "f")
                        
                    msg("Background histograms stacked in order successfully.", print = self.verbose_mode)
                except Exception as e:
                    err_msg(f"Could not stack the background histograms in order due to the error: {e}")

            try:
                self.stack.SetMaximum(y_max)
                self.stack.SetMinimum(y_min)

                req = "hist" + ("pfc plc" if self.auto_chose_colors_ else "")
                self.stack.Draw(req)

                x_div(self.stack)
                msg(f"The stacted histogram was drawn successfully.", print = self.verbose_mode)

                bkg_total, total_errors = self.make_bkg_total_with_uncertainty()
                bkg_total.SetLineColor(ROOT.kBlack)
                bkg_total.SetFillStyle(0)
                bkg_total.SetLineWidth(1)
                bkg_total.Draw("SAME HIST")
                total_errors.Draw("SAME E2")
                self.legend_bkg.AddEntry(total_errors, "Total SM", "fl")
                self.canvas.Update()

            except Exception as e:
                err_msg(f"The stacted histogram was not drawn due to the Error: {e}.")
                
            if self.single_histograms != []:
                for hist in self.single_histograms:
                    try:
                        hist.SetMaximum(y_max)
                        hist.SetMinimum(y_min)
                        x_div(hist)

                        req = "hist"  + "same"
                        hist.Draw(req)
                        msg(f"The histogram {hist.GetName()} was drawn successfully.", print = self.verbose_mode)
                    except Exception as e:
                        err_msg(f"The histogram {hist.GetName()} was not drawn due to the Error: {e}.")
        else:
            if self.single_histograms != []:
                for idx, hist in enumerate(self.single_histograms):
                    try:
                        hist.SetMaximum(y_max)
                        hist.SetMinimum(y_min)
                        x_div(hist)

                        req1 = "hist" 
                        req2 = "hist" + "same"
                        hist.Draw(req1 if idx == 0 else req2)
                        msg(f"The histogram {hist.GetName()} was drawn successfully.", print = self.verbose_mode)
                    except Exception as e:
                        err_msg(f"The histogram {hist.GetName()} was not drawn due to the Error: {e}.")

        if self.num_of_legends_bkg != 0:
            try:
                self.legend_bkg.Draw("same")
                msg(f"The backgrounds legend box was drawn successfully.", print = self.verbose_mode)
            except Exception as e:
                err_msg(f"The legend box was not drawn due to the Error: {e}.")
        
        if self.num_of_legends_sig != 0:
            try:
                self.legend_sig.Draw("same")
                msg(f"The signal legend box was drawn successfully.", print = self.verbose_mode)
            except Exception as e:
                err_msg(f"The legend box was not drawn due to the Error: {e}.")

        if self.labels != []:
            for idx, label in enumerate(self.labels, start = 1):
                try:
                    self.label.SetTextSize(label["text_size"])
                    self.label.DrawLatex(
                        label["x1"],
                        label["y1"],
                        label["label"]
                    )
                    msg(f"LaTex label {idx}: '{label["label"]}' was added successfully.", print = self.verbose_mode)
                except Exception as e:
                    err_msg(f"Could not add the LaTex label '{label["label"]}'' due to the error: {e}.")

        # Saving the plot in required formats
        try:
            has_format = bool(os.path.splitext(plot_name)[1])
            if has_format:
                self.canvas.SaveAs(plot_name)
                msg("Plot was saved in one format.", print = self.verbose_mode)
            else:
                for format in self.save_formats :
                    self.canvas.SaveAs(f"{plot_name}.{format}")
                msg(f"Plot was saved in {len(self.save_formats)} format.", print = self.verbose_mode)
        except Exception as e:
            err_msg(f"Could not save the plot. Returning the error: {e}")

    def set_logy(self, enable: bool) -> None:

        self.y_log = enable

        if enable == True:
            try:
                self.canvas.SetLogy(enable)
                msg("Log canvas enables", print = self.verbose_mode)
            except Exception as e:
                err_msg(f"Could not log the canvas due to the error: {e}")

    def clean_memory(self) -> None:

        proc_title("Cleaning Memory", print = self.verbose_mode)

        if self.histograms != []:
            for hist in self.histograms[:]:
                try:
                    name = hist.GetName()
                    hist.Delete()
                    msg(f"The histogram '{name}' is deleted.", print = self.verbose_mode)
                except Exception as e:
                    err_msg(f"The histogram '{name}' was not deleted successfully due to the Error: {e}.")
            self.histograms = []
        
        try:
            self.stack.Delete()
            msg("The stacked histogram created by this class was deleted.", print = self.verbose_mode)
        except Exception as e:
            err_msg(f"The stacked histogram created by this class was not deleted successfully due to the error {e}.")

        try:
            self.legend_bkg.Delete()
            msg("The lbackgroundegend created by this class was deleted.", print = self.verbose_mode)
        except Exception as e:
            err_msg(f"The background legend created by this class was not deleted successfully due to the error {e}.")
        
        try:
            self.legend_sig.Delete()
            msg("The signal legend created by this class was deleted.", print = self.verbose_mode)
        except Exception as e:
            err_msg(f"The signal legend created by this class was not deleted successfully due to the error {e}.")

        try:
            self.canvas.Close()
            msg("The canvas created by this class was closed.", print = self.verbose_mode)
        except Exception as e:
            err_msg(f"The canvas created by this class was not closed successfully due to the error {e}.")
        
        # try:
        #     self.label.Delete()
        #     msg("All the labels are deleted", print = self.verbose_mode)
        # except Exception as e:
        #     err_msg(f"Could not delete the labels due to the error {e}.")
            
        # cross check
        gc.collect()
        
