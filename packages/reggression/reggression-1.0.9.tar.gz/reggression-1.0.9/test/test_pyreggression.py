from reggression import Reggression
import pandas as pd

reg = Reggression("test/nasa_battery_1_10min.csv", "", "MSE", "test/nasa_battery.egraph", "", False)
print(reg.top(10))

print(reg.top(10, filters=["size < 10"], pattern="v0 ** v1", negate=True))

print(reg.pareto())
