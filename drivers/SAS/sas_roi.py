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


def signum(x):
    if x:
        return 100 #abs(x)/x
    else:
        return 0

def in_circle(x,y,x0,y0,r,inside=True):
    x -= x0
    y -= y0
    
    ra2 = x**2 + y**2
    rc2 = r*r
        
    if inside:
        return bool(ra2<=rc2)
    else:
        return bool(rc2<=ra2)


def in_ellipse(x,y,x0,y0,a,b,inside=True):
    x -= x0
    y -= y0
    re2 = 1.0
    if a and b:
        ra2 = (x/a)**2 + (y/b)**2
    elif abs(b)>SMALLNUM:
        ra2 = signum(x)**2 + (y/b)**2
    elif abs(a)>SMALLNUM:
        ra2 = (x/a)**2     + signum(y)**2 
    else:
        ra2 = signum(x)**2 + signum(y)**2
        
    if inside:
        return bool(ra2 <= re2)
    else:
        return bool(ra2 <= re2)



class RoiFrame(wx.Frame):
    def __init__(self,data,run):
        wx.Frame.__init__(self,None, -1, 'LENS SANS Roi Selector', size=(500, 500))
        # data
        self.data = data
        self.run  = run
        self.roi  = None
        self.bank = "bank1"
        self.msizer  = wx.BoxSizer (orient=wx.HORIZONTAL) 
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
        self.txtx0   = wx.TextCtrl(self, -1, "0")
        self.txty0   = wx.TextCtrl(self, -1, "0")
        self.txtrx1  = wx.TextCtrl(self, -1, "1")
        self.txtrx2  = wx.TextCtrl(self, -1, "5")
        #self.txtry1  = wx.TextCtrl(self, -1, "1")
        #self.txtry2  = wx.TextCtrl(self, -1, "5")

        self.mainmenu = wx.MenuBar()
        self.menu = wx.Menu()
        self.menu.Append(200, 'P&rint')
        self.menu.Append(201, 'S&ave')
        self.menu.Append(202, 'E&xit')
        self.mainmenu.Append(self.menu, "&File")
        self.SetMenuBar(self.mainmenu)

        self.csizer.AddMany([
            (self.bplot  , 0 , wx.EXPAND),
            (self.bclear , 0 , wx.EXPAND),
            (self.cinvert, 0 , wx.EXPAND),
            (wx.StaticText(self, -1, "Center (Pixels)"),0, wx.EXPAND),
            (self.txtx0  , 0 , wx.EXPAND),
            (self.txty0  , 0 , wx.EXPAND),
            (wx.StaticText(self, -1, "Radii (Pixels)"),0, wx.EXPAND),
            (self.txtrx1  , 0 , wx.EXPAND),
            (self.txtrx2  , 0 , wx.EXPAND),
            #(wx.StaticText(self, -1, "Y Radii (Pixels)"),0, wx.EXPAND),
            #(self.txtry1  , 0 , wx.EXPAND),
            #(self.txtry2  , 0 , wx.EXPAND),
            ])

        self.csizer.AddGrowableRow(0)
        self.csizer.AddGrowableRow(2)
        self.csizer.AddGrowableCol(1)
        self.Bind(wx.EVT_BUTTON, self.OnPlot       , id=100)
        self.Bind(wx.EVT_BUTTON, self.OnClear      , id=101)
        self.Bind(wx.EVT_MENU  , self.OnPrint      , id=200)
        self.Bind(wx.EVT_MENU  , self.OnSave       , id=201)
        self.Bind(wx.EVT_MENU  , self.OnExit       , id=202)
        self.Bind(wx.EVT_CLOSE , self.OnCloseWindow)
        self.SetSizer(self.msizer)
        self.Fit()
        self.PlotData()

    def OnCloseWindow(self, event):
        self.OnSave(None)
        self.Destroy()

    def OnExit(self, event):
        self.Close(True)


    def OnPrint(self, event):
        self.fig.savefig('SANS-%s-img.png' % (self.run),format='png')

    def OnSave(self, event):
        roi_file= open('roi_%s.dat' % self.run ,'wt')
        for id in self.roi:
            print >> roi_file,id
        roi_file.close()

    def OnPlot(self,event):        
        self.PlotData()

    def OnClear(self, event):
        self.axes.clear()
        self.Refresh()
        #self.axes.imshow(numpy.zeros(self.data.shape),cmap=cm.hot)

    def PlotData(self):
        c = self.data.copy()
        nx,ny = c.shape

        rx1 = float(self.txtrx1.GetValue()) 
        rx2 = float(self.txtrx2.GetValue())
        #ry1 = float(self.txtry1.GetValue()) 
        #ry2 = float(self.txtry2.GetValue())
        x0  = float(self.txtx0.GetValue()) + nx/2.0
        y0  = float(self.txty0.GetValue()) + ny/2.0

        exclude = self.cinvert.IsChecked()
        self.roi=[]
        for i in range(nx):

            for j in range(ny):
                cond1 = in_circle(i,j,x0,y0,rx1,inside=False)
                cond2 = in_circle(i,j,x0,y0,rx2,inside=True)
                cond  = bool(cond1 and cond2)
                if cond ^ exclude:
                    c[i,j]= 0 # math.log(SMALLNUM)
                else:
                    self.roi.append("%s_%d_%d" % (self.bank,i,j))
        self.axes.imshow(c.T,extent=(-40,40,-40,40),interpolation='nearest',cmap=cm.hot)
        self.Refresh()
        
        

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
    
    opt.add_option('--log','-l', dest='logscale', default=False, action='store_true',
                   help='display in log scale')
    opt.add_option('--proposal','-P', dest='proposal', default='2008_01_COM',
                   help='set SANS proposal id, default:2008_01_COM')
    opt.add_option('--archive' ,'-A', dest='archive' , default='/LENS/SANS',
                   help='set SANS archive directory, default=/LENS/SANS')
    opt.add_option('--debug','-d', dest='debug', default=False, action='store_true',
                   help='run in debugging mode')
    options, arguments = opt.parse_args()
    c = numpy.zeros((nx,ny))
    if options.debug:
        run = 0
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
   
    if options.logscale: 
    	c = numpy.log(c + numpy.ones((nx,ny)))
    
    app = wx.PySimpleApp()
    frame = RoiFrame(c,run)
    frame.Show()
    app.MainLoop()
    
