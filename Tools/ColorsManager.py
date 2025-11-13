import ROOT
import gc

def RequestColor(number, include_red = False):

    rgb_list = [
        (255, 0, 0),      # Red
        # (0, 0, 255),      # Blue
        (255, 255, 0),    # Yellow
        (255, 0, 255),    # Magenta
        (0, 255, 255),    # Cyan
        (255, 128, 0),    # Orange
        (128, 0, 255),    # Purple
        (0, 128, 255),    # Sky Blue
        (128, 255, 0),    # Lime Green
        (128, 128, 128),  # Gray
        (128, 64, 0),     # Brown
        (0, 64, 128),     # Dark Cyan
        (192, 255, 203),  # Light Green
        (203, 192, 255),  # Light Purple
        (255, 165, 0),    # Orange (classic)
        (0, 128, 0),      # Dark Green
        (0, 0, 128),      # Navy
        (255, 20, 147),   # Deep Pink
        (218, 165, 32),   # Goldenrod
        (0, 100, 0),      # Dark Green 2
        (139, 0, 139),    # Dark Magenta
        (70, 130, 180),   # Steel Blue
        (210, 105, 30),   # Chocolate
        (72, 61, 139)     # Dark Slate Blue
    ]

    red_colors = [c for c in rgb_list if c[0] > 150 and c[0] > max(c[1], c[2])]

    all_colors = [c for c in rgb_list if c not in red_colors]

    if include_red == True:
        ColorList = [ROOT.TColor.GetColor(r, g, b) for (r, g, b) in rgb_list]
    else:
        ColorList = [ROOT.TColor.GetColor(r, g, b) for (r, g, b) in all_colors]

    return ColorList if number == "all" else ColorList[number]
    
def DrawColorsMap():
    colors = RequestColor("all", include_red = False)
    N = len(colors)
    
    c = ROOT.TCanvas("c", "c", 400, 800)
    ROOT.gPad.Range(0.0, 0.0, 1.0, 1.0)
    ROOT.gPad.SetFillStyle(4000)

    box_h = 1/N
    box = ROOT.TBox()
    txt = ROOT.TLatex(); txt.SetTextAlign(22); txt.SetTextSize(0.03)
    for i, col in enumerate(colors):
        y1 = i * box_h
        y2 = y1 + box_h 
        box.SetFillColor(col)    
        box.DrawBox(0.0, y1, 1.0, y2)
        txt.DrawLatex(0.5, 0.5*(y1+y2), f"N{i} : {col}")

    c.Update()
    c.SaveAs("ColorMap.pdf")
    c.Close(); gc.collect()
