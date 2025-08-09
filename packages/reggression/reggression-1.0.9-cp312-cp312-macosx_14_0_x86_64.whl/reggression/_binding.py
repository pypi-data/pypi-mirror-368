def __bootstrap__():
   global __bootstrap__, __file__, __loader__
   import sys, os, importlib.resources as irs, importlib.util
#rtld   import dl
   with irs.files(__name__).joinpath(
     '_binding.cpython-312-darwin.so') as __file__:
      del __bootstrap__
      if '__loader__' in globals():
          del __loader__
#rtld      old_flags = sys.getdlopenflags()
      old_dir = os.getcwd()
      try:
        os.chdir(os.path.dirname(__file__))
#rtld        sys.setdlopenflags(dl.RTLD_NOW)
        spec = importlib.util.spec_from_file_location(
                   __name__, __file__)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
      finally:
#rtld        sys.setdlopenflags(old_flags)
        os.chdir(old_dir)
__bootstrap__()
