import time
import panoply

KEY = "panoply/2g866xw4oaqt1emi"
SECRET = "MmM0NWNvc2wwYmJ4ZDJ0OS84MmY3MzQ4NC02MDIzLTQyN2QtODdkMS0yY2I0NTAzNDk0NDQvMDM3MzM1OTk5NTYyL3VzLWVhc3QtMQ=="  # noqa

sdk = panoply.SDK(KEY, SECRET)
sdk.write('roi-test', {'hello': 1})



print sdk.qurl

time.sleep(5)
