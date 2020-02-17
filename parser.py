#!/usr/bin/python3
import os, sys, re, json

raw = os.popen("/usr/bin/pdftotext -raw {} /dev/stdout".format(sys.argv[1])).read()

kv = {}

match_set = {
  'invoice' : r'(?<=Invoice )\d*',
  'date': r'\d{1,2}\/\d{1,2}\/\d{4} \d+:\d+ [AP]M',
  'vin': r'(?<=VIN: )\w*',
  'plate': r'(?<=CA )\w{7}',
  'odo': r'(?<=MILEAGE )[\d,]*',
  'amount': r'(?<=Total )[\d.]*',
  'user': r'(?<=CENTER INFORMATION\n)[^\n]*'
}

for k,v in match_set.items():
  res = re.search(v, raw, re.M)
  if res:
    kv[k] = res.group(0)

if 'user' in kv:
  carname = '(?<={}\n)W[^\n]*'.format(kv['user'])
  res = re.search(carname, raw, re.M)
  if res:
    kv['carname'] = res.group(0)

if 'odo' in kv:
  # We are grabbing the next two lines for the 
  # shop title and the number
  shop = '(?<={}\n)[^\n]*\n[^\n]*'.format(kv['odo'])
  res = re.search(shop, raw, re.M)
  kv['odo'] = re.sub(',', '', kv['odo'])
  if res:
    parts = res.group(0).split('\n')
    second = re.split(r'\-+', parts[1])
    second.insert(0, parts[0])
    kv['shop'] = second

# The itemized list on the receipt is a bit tricky.
# first we capture the beginning, then we get everything up to the end of the receipt
receipt = re.search(r'(?<=AMOUNT.\$.\n)(.|\n)+?(?=\nYOUR SERVICE)', raw, re.M)
if receipt:
  kv['receipt'] = []
  receipt_raw = receipt.group(0)
  for line in receipt_raw.split('\n'):
    item = re.search('([^\(\d]*).+?([\-\d.]+)$', line)
    if item:
      name = item.group(1).strip()
      kv['receipt'].append((name, item.group(2)))

kv['raw'] = raw

print(json.dumps(kv))
