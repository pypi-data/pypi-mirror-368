import requests
from requests.auth import HTTPBasicAuth

class LambdaAPIClient:
    def __init__(self, api_key: str, base_url: str = "https://cloud.lambda.ai/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.auth = HTTPBasicAuth(api_key, '')
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }

    def list_instances(self):
        url = f"{self.base_url}/instances"
        return requests.get(url, auth=self.auth, headers=self.headers).json()

    def terminate_instances(self, instance_ids):
        url = f"{self.base_url}/instance-operations/terminate"
        payload = {"instance_ids": instance_ids}
        return requests.post(url, json=payload, auth=self.auth, headers=self.headers).json()

    def launch_instance(self, payload):
        url = f"{self.base_url}/instance-operations/launch"
        return requests.post(url, json=payload, auth=self.auth, headers=self.headers).json()

    def update_instance_name(self, instance_id, new_name):
        url = f"{self.base_url}/instances/{instance_id}"
        payload = {"name": new_name}
        return requests.post(url, json=payload, auth=self.auth, headers=self.headers).json()

    def list_instance_types(self):
        url = f"{self.base_url}/instance-types"
        return requests.get(url, auth=self.auth, headers=self.headers).json()

    def get_firewall_rules(self):
        url = f"{self.base_url}/firewall-rules"
        return requests.get(url, auth=self.auth, headers=self.headers).json()

    def get_firewall_rulesets(self):
        url = f"{self.base_url}/firewall-rulesets"
        return requests.get(url, auth=self.auth, headers=self.headers).json()

    def get_firewall_ruleset_by_id(self, ruleset_id):
        url = f"{self.base_url}/firewall-rulesets/{ruleset_id}"
        return requests.get(url, auth=self.auth, headers=self.headers).json()

    def delete_firewall_ruleset(self, ruleset_id):
        url = f"{self.base_url}/firewall-rulesets/{ruleset_id}"
        return requests.delete(url, auth=self.auth, headers=self.headers).json()

    def create_firewall_ruleset(self, name, region, rules):
        url = f"{self.base_url}/firewall-rulesets"
        payload = {
            "name": name,
            "region": region,
            "rules": rules
        }
        return requests.post(url, json=payload, auth=self.auth, headers=self.headers).json()

    def update_firewall_ruleset(self, ruleset_id, name, rules):
        url = f"{self.base_url}/firewall-rulesets/{ruleset_id}"
        payload = {
            "name": name,
            "rules": rules
        }
        return requests.patch(url, json=payload, auth=self.auth, headers=self.headers).json()

    def patch_global_firewall_ruleset(self, rules):
        url = f"{self.base_url}/firewall-rulesets/global"
        payload = {"rules": rules}
        return requests.patch(url, json=payload, auth=self.auth, headers=self.headers).json()

    def get_global_firewall_ruleset(self):
        url = f"{self.base_url}/firewall-rulesets/global"
        return requests.get(url, auth=self.auth, headers=self.headers).json()

    def list_ssh_keys(self):
        url = f"{self.base_url}/ssh-keys"
        return requests.get(url, auth=self.auth, headers=self.headers).json()

    def add_ssh_key(self, name, public_key):
        url = f"{self.base_url}/ssh-keys"
        payload = {"name": name, "public_key": public_key}
        return requests.post(url, json=payload, auth=self.auth, headers=self.headers).json()

    def delete_ssh_key(self, key_id):
        url = f"{self.base_url}/ssh-keys/{key_id}"
        return requests.delete(url, auth=self.auth, headers=self.headers).json()

    def list_file_systems(self):
        url = f"{self.base_url}/file-systems"
        return requests.get(url, auth=self.auth, headers=self.headers).json()

    def create_file_system(self, name, region):
        url = f"{self.base_url}/filesystems"
        payload = {"name": name, "region": region}
        return requests.post(url, json=payload, auth=self.auth, headers=self.headers).json()

    def delete_file_system(self, fs_id):
        url = f"{self.base_url}/filesystems/{fs_id}"
        return requests.delete(url, auth=self.auth, headers=self.headers).json()

    def list_images(self):
        url = f"{self.base_url}/images"
        return requests.get(url, auth=self.auth, headers=self.headers).json()

