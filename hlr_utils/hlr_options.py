import optparse

class SNSOptions(optparse.OptionParser):
    def __init__(self,usage=None,option_list=None):
        # parent constructor
        optparse.OptionParser.__init__(self,usage,option_list)

        # options for debug printing
        self.add_option("-v","--verbose",action="store_true",default=False,
                        dest="verbose",
                        help="Enable verbose print statements")
        self.add_option("-q","--quiet",action="store_false",dest="verbose",
                        help="Disable verbose print statements")
        
        # output options
        self.add_option("-o","--output",default=None,
                        help="Specify the output file name (the '.srf' file)")

        # specifying data sets
        self.add_option("","--data",default=None,
                        help="Specify the data file")
        self.add_option("","--ecan",default=None,
                        help="Specify the empty container file")
        self.add_option("","--norm",default=None,
                        help="Specify the normalization file")
        self.add_option("","--data-bkg",default=None,
                        help="Specify the data background file")
        self.add_option("","--ecan-bkg",default=None,
                        help="Specify the empty container background file")
        self.add_option("","--norm-bkg",default=None,
                        help="Specify the normalization background file")
        self.add_option("","--dark-count",default=None,
                        help="Specify the dark count file")
        
