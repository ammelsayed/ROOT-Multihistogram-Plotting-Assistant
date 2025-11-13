## Helpful functions from the toolbox
from Tools.console import proc_title, msg, err_msg
import ROOT
import gc, os

## Main Class
class PlottingAssistant:

    def __init__(self, x_title):

        # Style settings 
        ROOT.gROOT.SetStyle("ATLAS")
        ROOT.gROOT.SetBatch(True) 
        ROOT.gStyle.SetOptStat(0)
        ROOT.TGaxis.SetMaxDigits(4)

        # Intial colors setting
        ROOT.gStyle.SetPalette(ROOT.kDeepSea)
        self.auto_chose_colors = False

        self.x_title = x_title
        self.histograms = []
        self.single_histograms = []
        self.stacked_histograms = []
        self.num_of_legends = 0
        self.read_histograms_from_root = False

        unique = str(id(self))
        msg(f"Plotting assisting class with unique name {unique} activated.")

        # Initial Canvas Settings
        self.canvas = ROOT.TCanvas(f"Canvas_{unique}", f"Canvas_{unique}")
        self.canvas.SetCanvasSize(800, 600)

        # Initial Legends Settings
        self.legend_position = [0.63, 0.60, 0.92, 0.90]
        self.legend = ROOT.TLegend(self.legend_position[0], self.legend_position[1],
                                   self.legend_position[2], self.legend_position[3])
        self.legend.SetBorderSize(0)
        self.legend.SetFillStyle(0)

        # Inital Stacked Histograms settings
        # Only used if is_background = True
        self.stack = ROOT.THStack(f"Stack_{unique}", f"Stack_{unique}; {self.x_title}; Events")

        # Initial Labels settings
        self.label = ROOT.TLatex()
        self.label.SetNDC()
        self.labels = []
        
    def add_label(self, x1 = 0.20, y1 = 0.80, label = "", text_size = 0.045):
        self.labels.append({
            "x1"        : x1,
            "y1"        : y1,
            "label"     : label,
            "text_size" : text_size
        })
        
    def set_canvas_size(self, width, height):
        try:
            self.canvas.SetCanvasSize(width, height)
            msg(f"Canvas size was set to {width} * {height}")
        except Exception as e:
            err_msg(f"Could not set canvas size to {width} * {height} due to the error {e}")

    def set_legend_ncols(self,n):
        try:
            self.legend.SetNColumns(n)
            msg(f"Legend number of columns was set to {n}")
        except Exception as e:
            err_msg(f"Could not set legend NColumns (={n}) due to the error {e}")

    def set_legend_position(self, x1, y1, x2, y2):
        try:
            self.legend_position = [x1, y1, x2, y2]
            self.legend = ROOT.TLegend(self.legend_position[0], self.legend_position[1],
                                    self.legend_position[2], self.legend_position[3])
            msg("Legend positon set successfully.")
        except Exception as e:
            err_msg(f"Could not set the legend position due to the error {e}")

    def auto_place_legend(self, bool = False):
        """
        This part of code automatically study the amount of text in the legend and the best place to place the legend.
        """
        pass

    def book_histogram(self,
        hist_name = "",
        n_bins    = 25,    
        x_range   = [0,1]):

        x_max = x_range[1]; x_min = x_range[0]
        bin_width = round((x_max - x_min)/n_bins, 1)
        hist_title = f"hist_title; {self.x_title}; Events"
        hist = ROOT.TH1D(hist_name, hist_title, n_bins, x_min, x_max)

        return hist
    
    def append_histogram(self, hist,
        weight        = 1.0, 
        is_signal     = False,
        is_background = False,
        is_data       = False,
        show_legend   = False, 
        legend_name   = "", 
        show_style    = "l" ):

        # Dealing with historgam:
        hist.Scale(weight)
        # hist.Sumw2() # optional

        # If hist is background "auto" stack
        if is_background == True:
            try:
                self.stack.Add(hist)
                self.stacked_histograms.append(hist)
            except Exception as e:
                err_msg(f"{e}")
        else:
            try:
                self.single_histograms.append(hist)
            except Exception as e:
                err_msg(f"{e}")
        
        # "Auto" fill the legends
        if show_legend == True:
            try:
                self.legend.AddEntry(hist, legend_name, show_style)
                self.num_of_legends += 1
            except Exception as e:
                err_msg(f"{e}")
        
        self.histograms.append(hist)
    
    def fill_from_file(self, root_file_path):
        pass

    def design_histogram(self, hist, 
        line_color = None,
        line_style = None,
        line_width = None,
        fill_color = None, 
        fill_style = None ):

        self.auto_chose_colors = False
        
        if line_color:
            hist.SetLineColor(line_color)
        if line_style:
            hist.SetLineStyle(line_style)
        if line_width:
            hist.SetLineWidth(line_width)
        if fill_color:
            hist.SetFillColor(fill_color)
        if fill_style:
            hist.SetFillStyle(fill_style)

    def save_histograms(self, root_file_name):
        proc_title("Saving The Histograms")
        root_file = ROOT.TFile(root_file_name, "RECREATE")
        if self.histograms != []:
            for hist in self.histograms:
                try:
                    name = hist.GetName()
                    hist.Write()
                    msg(f"The histogram '{name}' was saved successfully in '{root_file_name}'.")
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
            
    def draw_plot(self, plot_name, formats = ["pdf", "tex"]):
        proc_title("Drawing The Plot")
        self.canvas.cd()
        if self.stacked_histograms != []: 
            try:
                req = "hist" + ("pfc" if self.auto_chose_colors else "")
                self.stack.Draw(req)
                msg(f"The stacted histogram was drawn successfully.")
            except Exception as e:
                err_msg(f"The stacted histogram was not drawn due to the Error: {e}.")
                
            if self.single_histograms != []:
                for hist in self.single_histograms:
                    try:
                        req = "hist" + ("plc" if self.auto_chose_colors else "") + "same"
                        hist.Draw(req)
                        msg(f"The histogram {hist.GetName()} was drawn successfully.")
                    except Exception as e:
                        err_msg(f"The histogram {hist.GetName()} was not drawn due to the Error: {e}.")
        else:
            if self.single_histograms != []:
                for idx, hist in enumerate(self.single_histograms):
                    try:
                        req1 = "hist" + ("plc" if self.auto_chose_colors else "")
                        req2 = "hist" + ("plc" if self.auto_chose_colors else "") + "same"
                        hist.Draw(req1 if idx == 0 else req2)
                        msg(f"The histogram {hist.GetName()} was drawn successfully.")
                    except Exception as e:
                        err_msg(f"The histogram {hist.GetName()} was not drawn due to the Error: {e}.")

        if self.num_of_legends != 0:
            try:
                self.legend.Draw("same")
                msg(f"The legend box was drawn successfully.")
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
                    msg(f"LaTex label {idx}: '{label["label"]}' was added successfully.")
                except Exception as e:
                    err_msg(f"Could not add the LaTex label '{label["label"]}'' due to the error: {e}.")

        # Saving the plot in required formats
        try:
            has_format = bool(os.path.splitext(plot_name)[1])
            if has_format:
                self.canvas.SaveAs(plot_name)
                msg("Plot was saved in one format.")
            else:
                for format in formats:
                    self.canvas.SaveAs(f"{plot_name}.{format}")
                msg(f"Plot was saved in {len(formats)} format.")
        except Exception as e:
            err_msg(f"Could not save the plot. Returning the error: {e}")
    
    def set_yrange(self, y_range):

        if self.histograms != []:
            for hist in self.histograms:
                try:
                    hist.SetMaximum(y_range[1])
                    hist.SetMinimum(y_range[0])
                    msg(f"The y-axis range of of histogram {hist.GetName()} was set to '({y_range[0]}, {y_range[1]})'.")
                except Exception as e:
                    err_msg(f"Could not set y-range of histogram {hist.GetName()} successfully due to the Error: {e}.")
        else: 
            msg("No single histograms were found.")

        if self.stacked_histograms != []:
            try:
                self.stack.SetMaximum(y_range[1])
                self.stack.SetMinimum(y_range[0])
                msg(f"The y-axis range of the stacked histogram was set to '({y_range[0]}, {y_range[1]})'")
            except Exception as e:
                err_msg(f"Could not set the y-axis range of the stacked histogram due to the Error: {e}.")
        else: 
            msg("No stacked histograms were found.")
    
    def set_x_divisions(self, n):

        if self.histograms != []:
            for hist in self.histograms:
                try:
                    hist.GetXaxis().SetNdivisions(n, ROOT.kTRUE)
                    msg(f"The number of x-axis divisions of the histogram {hist.GetName()} set to {n}.")
                except Exception as e:
                    err_msg(f"Could not set x-axis divisions of the histogram {hist.GetName()} successfully due to the error: {e}.")
        else: 
            msg("No single histograms were found.")

        # if self.stacked_histograms != []:
        #     try:
        #         self.stack.GetXaxis().SetNdivisions(n, ROOT.kTRUE)
        #         msg(f"The number of x-axis divisions of the stacked histogram set to {n}.")
        #     except Exception as e:
        #         err_msg(f"Could not set x-axis divisions of the stacked histogram successfully due to the error: {e}.")
        # else: 
        #     msg("No stacked histograms were found.")

    def set_logy(self, bool):
        try:
            self.canvas.SetLogy(bool)
            msg("Log canvas enables")
        except Exception as e:
            err_msg(f"Could not log the canvas due to the error: {e}")
    
    def set_logx(self, bool):
        self.canvas.SetLogx(bool)

    def clean_memory(self):
        proc_title("Cleaning Memory")

        if self.histograms != []:
            for hist in self.histograms[:]:
                try:
                    name = hist.GetName()
                    hist.Delete()
                    msg(f"The histogram '{name}' is deleted.")
                except Exception as e:
                    err_msg(f"The histogram '{name}' was not deleted successfully due to the Error: {e}.")
            self.histograms = []
        
        try:
            # self.stack.Delete()
            # self.stack = None
            msg("The stacked histogram created by this class was deleted.")
        except Exception as e:
            err_msg(f"The stacked histogram created by this class was not deleted successfully due to the error {e}.")

        try:
            # self.legend.Delete()
            # self.legend = None
            msg("The legend created by this class was deleted.")
        except Exception as e:
            err_msg(f"The legend created by this class was not deleted successfully due to the error {e}.")

        try:
            self.canvas.Close()
            msg("The canvas created by this class was closed.")
        except Exception as e:
            err_msg(f"The canvas created by this class was not closed successfully due to the error {e}.")
        
        # also delete the label box!
            

        gc.collect()
        
        
if __name__ == '__main__':

    # ## Example Usage

    # input_file_path = "/data/ammelsayed/Framework/Channel_2J1L/Output/Data2/MC_events.root"
    
    # root_file = ROOT.TFile(input_file_path, "READ")

    # plot = PlotBuilder()

    # _list = ["WW_Tree", "ZZ_Tree", "WZ_Tree", "tt_Tree", "t_Tree", "VH_Tree"]

    # for proc in _list:

    #     tree = root_file.Get(proc)

    #     hist = plot.book_histogram(
    #         hist_name = f"uniqueName_{proc}",
    #         x_title = "HT [GeV]",
    #         n_bins = 25,
    #         x_range = [200,2000]
    #     )

    #     # plot.design_histogram(
    #     #     hist,
    #     #     line_color=ROOT.kRed
    #     # )

    #     #------------ FILLING -------------#
    #     tree.GetBranch("HT")
    #     tree.Draw(f"HT >> uniqueName_{proc}", "", "goff")
    #     #------------ FILLING -------------#

    #     plot.append_histogram(
    #         hist,
    #         is_background = True,
    #         show_legend = True,
    #         legend_name = f"{proc} Background"
    #     )

    # plot.set_ymax(1.2e3)
    # plot.set_logy(False)
    # plot.save_histograms("file.root")
    # plot.add_label(label="Test")
    # plot.draw_plot("HT.pdf")
    # plot.clean_memory()

    pass