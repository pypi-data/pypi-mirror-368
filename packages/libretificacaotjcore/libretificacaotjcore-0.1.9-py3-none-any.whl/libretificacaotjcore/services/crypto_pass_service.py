from cryptography.fernet import Fernet


class CryptoPassService:
    def hasherPass(self, password:str , key_id_aws: str, region_name: str):
        key = Fernet.generate_key()
        cipher = Fernet(key)
        
        pass_config = password.encode()
        
        