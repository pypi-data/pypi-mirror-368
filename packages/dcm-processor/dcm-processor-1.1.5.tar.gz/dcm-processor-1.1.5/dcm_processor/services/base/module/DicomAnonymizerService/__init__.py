import os, json
from .anonymize import anonymize

DATA = os.getenv('DATA', '/data')
MODULES = os.getenv('MODULES', '/modules')


def worker(jobName, headers, params, added_params, **kwargs):
  disabled = False
  
  if not params is None:
    disabled = params.get("disabled", False)

  if disabled:
    return

  if "seriesIds" in headers:
    seriesIds = headers.get("seriesIds")
    for seriesId in seriesIds:
      dcmpath = os.path.join(DATA, headers.get("dcmpath"), seriesId)
      anonymize(dcmpath, params=params)
    
