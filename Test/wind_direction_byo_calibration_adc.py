#encoding:UTF-8
# IHS

from gpiozero import MCP3008
import time
adc = MCP3008(channel=0)
print(adc.value)
count = 0
values = []
while True:
    wind =round(adc.value*3.3,1)
    print("wind:%s" % str(wind))
    if not wind in values:
        values.append(wind)
        count+=1
        print(count, values)

    time.sleep(0.3)
