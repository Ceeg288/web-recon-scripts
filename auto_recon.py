import platform
import subprocess
import os
import argparse
import requests


SUB_DIRECTORIES = ['nmap', 'ffuf','dig', 'subfinder']
DEPENDENCIES = ['nmap', 'ffuf', 'subfinder']
DIRECTORY_BASE_PATH = 'web-pentesting'
FILES_TO_GRAB = ['robots.txt', 'sitemap.xml','.DS_Store']

#Check to see if you're running Linux and have the right dependencies installed
def os_dep_check():

	print("[*] Verifying OS and dependencies..")
	os = platform.system()
	if os == 'Linux':
		for dep in DEPENDENCIES:
			try:	
				subprocess.check_output(['dpkg', '-s', dep])
				print(f"[*] {dep} verified..")
			except subprocess.CalledProcessError:
				print(f"[!] Missing dependencies {dep}")
				install_input = input("Would you like to install? (y/n):")
				if install_input.lower() == 'y':
					try:
						subprocess.check_output(['sudo', 'apt', 'install', '-y', dep])
						print(f"[+] Program {dep} installed successfully.")
					except subprocess.CalledProcessError as e:
						print(f"[!] Error occurred while installing '{dep}': {str(e)}")
				if install_input.lower() == 'n':
					print("[*] Exiting...")
					exit()
		print("[+] Dependencies verified..")
	else:
		print("[!] No linux OS detected, please run this on a Linux machine.")
		exit()

#Makes our directory for the website we're researching so all of the output is stored in a common, easily accessible location
def make_dirs(domain):

	for dir in SUB_DIRECTORIES:
		dir_path = f'{DIRECTORY_BASE_PATH}/{domain}/{dir}'
		if not os.path.exists(dir_path):
			os.makedirs(dir_path)
			print(f"[*] Directory : {dir_path} created...")
		else:
			print(f"[!] {dir_path} exists, skipping directory creation...")

def run_commands(domain, wordlist=None, wordlist_input=False):

	print("[*] Running Dig query...")
	with open(f'{DIRECTORY_BASE_PATH}/{domain}/dig/{domain}_dig.txt', 'w') as f:
		subprocess.run(['dig', domain], stdout=f, text=True)
	print(f"[+] Finished writing to {f.name}")
	f.close()
	print("[+] Dig query completed...")

	print("[*] Running Nmap scan...")
	with open(f'{DIRECTORY_BASE_PATH}/{domain}/nmap/{domain}_nmap.txt', 'w') as f:
		subprocess.run(['nmap', '-v', '-A', '-F', domain], stdout=f, text=True)
	print(f"[+] Finished writing to {f.name}")
	f.close()
	print("[+] Nmap scan completed...")

	print("[*] Running subfinder...")
	with open(f'{DIRECTORY_BASE_PATH}/{domain}/subfinder/{domain}_subfinder.txt', 'w') as f:
		subprocess.run(['subfinder', '-d', domain], stdout=f, text=True)
	print(f"[+] Finished writing to {f.name}")
	f.close()
	print("[+] Subfinder completed...")

	print("[*] Running ffuf...")
	with open(f'{DIRECTORY_BASE_PATH}/{domain}/ffuf/{domain}_ffuf.txt', 'w') as f:
		if wordlist_input == True:
			subprocess.run(['ffuf', '-w', wordlist, '-u', f'https://{domain}/FUZZ', '-p', '1'], stdout=f, text=True)
		else:
			subprocess.run(['ffuf', '-w', '/usr/share/wordlists/seclists/SecLists-master/Discovery/Web-Content/common.txt', '-u', f'https://{domain}/FUZZ', '-p', '1'], stdout=f, text=True)
	print(f"[+] Finished writing to {f.name}")
	f.close()
	print("[+] Ffuf completed...")

def run_web_requests(domain):
	target_request_url = f'https://{domain}'
	crt_sh_url = f'https://crt.sh/?q={domain}&output=json'

	for file in FILES_TO_GRAB:
		response = requests.get(f'{target_request_url}/{file}')
		if response.status_code != 404:
			print(f'{file} : Status Code {response.status_code}')
			with open(f'{DIRECTORY_BASE_PATH}/{domain}/{domain}_{file}', 'w') as f:
				f.writelines(response.text)
				print(f"[+] Finished writing to {f.name}")
			f.close()
	
	try:
		print(f"Running crt.sh query on {domain}")
		print(f"[*] Requesting: {crt_sh_url}")
		response = requests.get(crt_sh_url)
		data = response.json()

		with open(f'{DIRECTORY_BASE_PATH}/{domain}/{domain}_crtsh.txt', 'w') as f: 
			
			#Grabbing the fields I care about and throwing them in a text file split by new lines
			for i in data:
				f.write(f"Issuer Name: {i['issuer_name']}\n")
				f.write(f"Common Name: {i['common_name']}\n")
				f.write(f"Name Value: {i['name_value']}\n")
				f.write(f"Entry Time: {i['entry_timestamp']}\n")
				f.write(f"Not Before: {i['not_before']}\n")
				f.write(f"Not After: {i['not_after']}\n")
				f.write("\n")
			
			print(f"[+] Finished writing to {f.name}")
			f.close()

	except Exception as e:
		print(f"[!] An error occurred: {e}")


if __name__ == '__main__':
	os_dep_check()
	parser = argparse.ArgumentParser(description="Automates Recon for Bug Bounties")
	parser.add_argument("-d", "--domain", required=True, help="Non-Wildcard domain of the target you're researching")
	parser.add_argument("-w" "--wordlist", required=False, help="Enter the path to the wordlist you would like to use")
	args = parser.parse_args()
	make_dirs(args.domain)
	run_web_requests(args.domain)
	if args.w__wordlist:
		run_commands(args.domain, wordlist=args.w__wordlist, wordlist_input=True)
	else:
		run_commands(args.domain)
	print("[*] Exiting")
	exit()