#!/usr/bin/env python

import os, sys, math
import dr_lib
import hlr_utils
from   sas_utils  import *

import matplotlib
matplotlib.use('WXAgg')
matplotlib.rc('image', origin='lower')

import matplotlib.cm as cm
from   matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from   matplotlib.figure import Figure
import numpy 

import wx

VERSION="0.01"
SMALLNUM=0.1

class RoiFrame(wx.Frame):
    def __init__(self,data):
        wx.Frame.__init__(self,None, -1, 'LENS SANS Roi Selector', size=(500, 500))

        self.data = data
        self.roi  = None
        self.bank = "bank1"
        self.msizer  = wx.BoxSizer (orient=wx.HORIZONTAL) # rows=2,cols=1,hgap=5, vgap=5)
        # command
        self.csizer  = wx.FlexGridSizer(rows=4,cols=3,hgap=5, vgap=5)
        self.msizer.Add(self.csizer, 0, 0, wx.EXPAND)
        # canvas
        self.fig     = Figure(figsize=(8,8))
        self.axes    = self.fig.add_axes([0.1,0.1,0.8,0.8])
        self.canvas  = FigureCanvas(self,-1,self.fig)
        self.msizer.Add(self.canvas, 1, 0, wx.EXPAND)

        self.bplot   = wx.Button  (self,100, label="Plot"   )
        self.bclear  = wx.Button  (self,101, label="Clear"  )
        self.cinvert = wx.CheckBox(self, -1, label="Include")
        self.txtr1   = wx.TextCtrl(self, -1, "0")
        self.txtr2   = wx.TextCtrl(self, -1, "5")
        self.txtx0   = wx.TextCtrl(self, -1, "0")
        self.txty0   = wx.TextCtrl(self, -1, "0")

        self.mainmenu = wx.MenuBar()
        self.menu = wx.Menu()
        self.menu.Append(200, 'E&xit')
        self.mainmenu.Append(self.menu, "&File")
        self.SetMenuBar(self.mainmenu)

        self.csizer.AddMany([
            (self.bplot  , 0 , wx.EXPAND),
            (self.bclear , 0 , wx.EXPAND),
            (self.cinvert, 0 , wx.EXPAND),
            (wx.StaticText(self, -1, "Center (Pixels)"),0, wx.EXPAND),
            (self.txtx0  , 0 , wx.EXPAND),
            (self.txty0  , 0 , wx.EXPAND),
            (wx.StaticText(self, -1, "Radius (Pixels)"),0, wx.EXPAND),
            (self.txtr1  , 0 , wx.EXPAND),
            (self.txtr2  , 0 , wx.EXPAND),
            ])
        

        self.csizer.AddGrowableRow(0)
        self.csizer.AddGrowableRow(2)
        self.csizer.AddGrowableCol(1)
        
        self.Bind(wx.EVT_BUTTON, self.OnPlot       , id=100)
        self.Bind(wx.EVT_BUTTON, self.OnClear      , id=101)
        self.Bind(wx.EVT_MENU  , self.OnExit       , id=200)
        self.Bind(wx.EVT_CLOSE , self.OnCloseWindow)
        
        self.SetSizer(self.msizer)
        self.Fit()
        self.PlotData()

    def OnCloseWindow(self, event):
        self.SaveRoi('close')
        self.Destroy()

    def OnExit(self, event):
        self.Close(True)


    def OnPlot(self,event):        
        self.PlotData()

    def OnClear(self, event):
        self.axes.clear()
        self.Refresh()
        #self.axes.imshow(numpy.zeros(self.data.shape),cmap=cm.hot)

    def PlotData(self):
        c = self.data.copy()
        nx,ny = c.shape

        r1 = float(self.txtr1.GetValue()) 
        r2 = float(self.txtr2.GetValue())
        x0 = float(self.txtx0.GetValue()) + nx/2.0
        y0 = float(self.txty0.GetValue()) + ny/2.0
        r1 *= r1
        r2 *= r2
        exclude = self.cinvert.IsChecked()
        self.roi=[]
        for i in range(nx):
            for j in range(ny):
                xr2  = (i-x0)**2 + (j-y0)**2
                cond = bool(r1 <= xr2 and xr2 <= r2)
                if cond ^ exclude:
                    c[i,j]=math.log(SMALLNUM)
                else:
                    self.roi.append("%s_%d_%d" % (self.bank,i,j))
        self.axes.imshow(c.T,extent=(-40,40,-40,40),interpolation='nearest',cmap=cm.hot)
        self.Refresh()
    def SaveRoi(self,arg):
        print 'Save ROI',arg
        roi_file= open('roi.dat','wt')
        for id in self.roi:
            print >> roi_file,id
        roi_file.close()



class RoiApp(wx.App):
    
    def OnInit(self):
        frame = RoiFrame()
        frame.Show()
        return True



def g(x,y):
    return math.exp(-0.5*x*x)*math.exp(-0.5*y*y)

def debug_image(c,nx,ny):
    for i in range(nx):
        for j in range(ny):
            c[i,j] = 100.0*g((i-nx/2.0)/20.0,(j-ny/2.0)/10.0)
    return c
     
if __name__ == "__main__":
    """TODO: Cleanup this mess below"""
    import optparse
    from   time  import ctime

    nx,ny = 80,80

    # parse options
    argv0   = os.path.basename(sys.argv[0])
    usage   = "%s [options] <run_number>" % argv0
    version = "%s %s" % (argv0,VERSION)
    opt = optparse.OptionParser(usage=usage,version=version)
    
    opt.add_option('--proposal','-P', dest='proposal', default='2008_01_COM',
                   help='set SANS proposal id, default:2008_01_COM')
    opt.add_option('--archive' ,'-A', dest='archive' , default='/LENS/SANS',
                   help='set SANS archive directory, default=/LENS/SANS')
    opt.add_option('--debug','-d', dest='debug', default=False, action='store_true',
                   help='run in debugging mode')
    options, arguments = opt.parse_args()
    c = numpy.zeros((nx,ny))
    if options.debug:
        c = debug_image(c,nx,ny)
    else:
        # for now only single run allowed
        if len(arguments)!=1:
            print "%s: exactly one run number required" % argv0
            opt.print_help()
            sys.exit(-1)
        run = arguments[0]
        nexusFile = nexusFilePath(options.archive,options.proposal,run)
        if not os.path.exists(nexusFile):
            print 'NeXus file',nexusFile, 'does not exist!'
            sys.exit(-1)
                
        s = get_spectrum(nexusFile,verbose=True, debug=True)
        print ctime(),'2dview: summing'
        r = dr_lib.integrate_spectra(s)

        print ctime(),'2dview: converting to numpy 2d array'
        for k in xrange(hlr_utils.get_length(r)):
            c[r[k].id[1]]=r[k].y

    c = numpy.log(c + numpy.ones((nx,ny))*SMALLNUM)
    
    app = wx.PySimpleApp()
    frame = RoiFrame(c)
    frame.Show()
    app.MainLoop()






    
