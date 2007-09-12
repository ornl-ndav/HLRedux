The HLRedux (High-Level Reduction Functions) package is designed to provide 
high-level representations of functions found in the SNS Common Libraries 
(SCL), data reduction requirements not found in the SCL, access to reading 
and writing data via the DOM package and fulfilling the data reduction process 
by providing driver modules that perform the required data reduction steps.

Authors: Michael Reuter <reuterma@ornl.gov>
	 Peter Peterson <petersonpf@ornl.gov

Installation Instructions
=========================

  Software Requirements
  ---------------------

  The HLRedux package has direct dependencies on DOM and SCL, so versions of 
  these packages need to be installed before HLRedux can be used. If the 
  ability to use the timing routines or the use of the SNS file system is 
  required to find run numbers, the ASGUtils package is required. If one wants 
  to (re)create the package documentation, the Epydoc 
  (http://epydoc.sourceforge.net) package is required for this.
  
  HLRedux currently works best under Linux, but has been occasionaly known to 
  work under OSX. The following lists the current versions of software that 
  HLRedux has been known to work under.

    1. Python       - 2.3.4
    2. DOM          - 1.0.0iqc6
    3. SCL          - 1.1.0iqc4
    4. ASGUtils     - 0.3
    5. Epydoc       - 3.0beta1

  Installation
  ------------

  The HLRedux package follows standard Python installations:

  python setup.py install

  The default install location is /usr/local. To override this location, use 
  the --prefix option.

  The default behavior of the setup script is to install drivers for all 
  classes of instruments. If one only wants drivers for a specific class of 
  instruments, the --inst option can be used. The following is the list of 
  accepted options for --inst.

    1. ASG - Analysis Software Group - Drivers for ASG tests
    2. DGS - Direct Geometry Spectrometers
    3. GEN - General - Drivers for general use by all instrument classes
    4. IGS - Inverse Geometry Spectrometers
    5. PD  - Powder Diffractometers
    6. REF - Reflectometers
    7. SAS - Small Angle Scattering
    8. SCD - Single Crystal Diffractometers

  Multiple classes are specified in a comma delimited string to the option 
  (i.e. --inst=SCD,PD,GEN). If the --inst option is used and the GEN tag is 
  not supplied, it is automatically included so those drivers are installed.

  Documentation
  -------------

  To (re)create the package documentation, cd to the doc directory and run the 
  following command:

  sh makedoc


$Id$
