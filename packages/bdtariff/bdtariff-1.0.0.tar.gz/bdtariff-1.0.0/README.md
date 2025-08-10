tariff rate take from https://customs.gov.bd/files/Tariff-2025-2026(02-06-2025).pdf
------- How to get total duty -------------

from bdtariff import duty
duty()
-----------------------------------------
Enter HSCode and then Assess Value in BDT
you get totat duty in BDT.

------ How to know tariff rate ------------

from bdtariff import rate
rate()
------------------------------------------
Enter HScode
You get Tariff rate

------ How to get one by one --------------

from bdtariff import hscode

result = hscode(HSCODE)
print(result.cd)  # Get the 'cd' field
print(result.sd)  # Get the 'sd' field
print(result.rd)  # Get the 'rd' field
print(result.vat)  # Get the 'vat' field
print(result.at)  # Get the 'at' field
print(result.ait)  # Get the 'ait' field
print(result.tti)  # Get the 'tti' field
print(result.tarriff_description)  # Get the 'Tariff Description' field


################# Sample Program #############

from bdtariff import hscode

result = hscode("01012100")
if result:
    print(result.cd)  # Get the 'cd' field
    print(result.sd)  # Get the 'sd' field
    print(result.as_dict())  # Get the full dictionary
else:
    print("HSCode not found")
	
################# Sample Program for duty calculation #############

from bdtariff import duty

result = duty(hscode("01012100"),100)
if result:
    print(result.cd)  # Get the 'cd'
    print(result.sd)  # Get the 'sd'
    print(result.tti)  # Get the total duty
else:
    print("HSCode not found")