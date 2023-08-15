#Ceeg288/Caleb Gorde crt.sh lookup tool
#Usage: python crt_sh.py -d domain.com

import requests
import argparse

def query_crtsh(domain):

	#crt.sh requires &output=json appended to the end, I wasn't able to find anything on the actual site that dictated this, just did some Googling :)
	request_url = f'https://crt.sh/?q={domain}&output=json'

	#Splitting the passed domain up for a cleaner file name and accounting for potential sub-domains
	file_name = str()
	for n in domain.split('.'):
		file_name += f'{n}_'

	try:
		print(f"[*] Requesting: {request_url}")
		response = requests.get(request_url)
		data = response.json()

		with open(f'{file_name}crtsh.txt', 'w') as f: 
			
			#Grabbing the fields I care about and throwing them in a text file split by new lines
			for i in data:
				f.write(f"Issuer Name: {i['issuer_name']}\n")
				f.write(f"Common Name: {i['common_name']}\n")
				f.write(f"Name Value: {i['name_value']}\n")
				f.write(f"Entry Time: {i['entry_timestamp']}\n")
				f.write(f"Not Before: {i['not_before']}\n")
				f.write(f"Not After: {i['not_after']}\n")
				f.write("\n")
			
			print(f"[*] Finished writing to {f.name}")
			f.close()

	except Exception as e:
		print(f"[!] An error occurred: {e}")

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Run a crt.sh search on a given domain.")
	parser.add_argument("-d", "--domain", required=True, help="The domain you want to search ie. google.com")
	args =parser.parse_args()
	query_crtsh(args.domain)
	print("Exiting...")
	exit()