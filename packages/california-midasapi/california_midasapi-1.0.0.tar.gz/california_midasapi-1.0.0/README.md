# california-midasapi
A Python wrapper for the California Energy Comission (CEC)'s Market Informed Demand Automation Server (MIDAS) energy price API.  
This API lets you get info about energy prices in California from utilities regulated by the CEC, which is all the big ones (PG&E, SCE, SDG&E, SMUD, etc.) and some smaller municipal utilities. If you have a Rate Identification Number (RIN) QR Code on your electric bill you can use this API to get your electricity price in real time.


## Usage
1. Start by registering an account with MIDAS. There is no webpage for this so I have provided a helper. You only have to register an account once.
```python
from california_midasapi import Midas
response = Midas.register("username", "password", "email@email.email", "Full Name")
print(response)
```
You should see `User account for username was successfully created. A verification email has been sent to email@email.email. Please click the link in the email in order to start using the API.`.  
Click the link in the email, then you can use the rest of the API as described below.

2. Create a `Midas` object:
```python
from california_midasapi import Midas
midas = Midas("username", "password")
```

3. Access the API methods using this object:
```python
# Get basic info about all rates
from california_midasapi.ratelist import RINFilter
rates = midas.GetAvailableRates(RINFilter.TARIFF)
print(rates) # ~40k+ items at writing

# Get specific info about one rate
ratedata = midas.GetRateInfo('USCA-SMSM-AD00-0000')
print(ratedata)
# Get the currently applicable value from a rate (local filtering)
print(ratedata.GetCurrentTariffs())
```


## Contributing
Contributions are welcome, please submit a PR!


## More Information & Thanks
More info about MIDAS can be found at https://midasapi.energy.ca.gov/  
Thank you to the CEC for providing example code at https://github.com/morganmshep/MIDAS-Python-Repository

## Projects using this library
[ha-midas](https://github.com/MattDahEpic/ha-midas): A Home Assistant integration to expose MIDAS rate data to your smart home

If you have a project using this library, we'd love to hear about it! Let us know and we'll add it to this list.