## PyROOT Multi-histogram plotting assistant

This work introduces a code, EventsFillerClass.py, that can take multiple TH1D histograms as an input, classify backgrounds from signals, stack histograms and show signals invidudally. 

All you need to do is just to books some histograms. Then append them and while appending them you tell this the classs its type (signal, background or data), show the class add it to legend or not, and if yes what is the legend name and showing option?

Then the class will internally handel all the histograms and legends. After doing so you tell the class to save the plot in one or mutiple formats. You can also ask the class to save the histograms in a root file for you on the flight! 

This is some code example of how to use the class:
