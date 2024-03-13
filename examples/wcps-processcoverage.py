# Very simple script demonstrating the use ProcessCoverages request making use WCPS.
# ---
#
# The equivalent ProcessCoverage request that is equivalent ot hte example is:
# https://code-de.rasdaman.com/rasdaman/ows?service=WCS&version=2.0.1&request=ProcessCoverages&query=for%20%24c%20in%20(S2_L2A_32631_B01_60m)%20%0Areturn%0A%20%20encode(%0A%20%20%20%20(%200.20%20*%20(%201050.0%20%2B%20(%20%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20(float)%20%24c%5B%20ansi(%20%222017-04-03%22%20)%20%5D%20-%20%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%24c%5B%20ansi(%20%222017-04-10%22%20)%20%5D%20)%20%0A%20%20%20%20%20%20%20%20%20%20%20%20)%20%0A%20%20%20%20)%5B%20E(%20660000%3A690000%20)%2C%20N(%205090220%3A5115220%20)%20%5D%0A%20%20%20%2C%20%22image%2Fjpeg%22)%0A%27%27%27
# ---
# 
# Example to find the equivalent information using OWSLib is as below:
# 

from owslib.wcs import WebCoverageService
import numpy as np
from io import BytesIO
from PIL import Image as im

my_wcs = WebCoverageService('https://code-de.rasdaman.com/rasdaman/ows', version='2.0.1')

#query performs time-series processing by calculating, in the Sentinel-2 datacube,
#the difference between two timeslices of the B1 band. The result is numerically
#adjusted so that it fits into the range of [0, 255] for encoding in JPEG
query = '''
for $c in (S2_L2A_32631_B01_60m)
return
  encode(
    ( 0.20 * ( 1050.0 + (
                (float) $c[ ansi( "2017-04-03" ) ] -
                        $c[ ansi( "2017-04-10" ) ] )
            )
    )[ E( 660000:690000 ), N( 5090220:5115220 ) ]
   , "image/jpeg")
'''


response = my_wcs.process(query)

#bytes -> BytesIO -> PIL.Image -> np.array
img_arr = np.array(im.open(BytesIO(response)))

#image being extracted from image array
data = im.fromarray(img_arr)

#showing image
data.show()

#saving image as a jpeg file
data.save('test.jpeg')