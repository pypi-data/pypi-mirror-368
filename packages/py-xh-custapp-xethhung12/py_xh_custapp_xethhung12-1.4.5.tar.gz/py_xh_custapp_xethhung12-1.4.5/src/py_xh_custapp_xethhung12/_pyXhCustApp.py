import os
import sys
from os.path import isfile, join
from pathlib import Path
from typing import Optional
import hashlib
from pathlib import Path
import base64
from Crypto import Random
from Crypto.Cipher import AES
import random

class _EncryptionTools:
    @staticmethod
    def hex_format(data: bytes)->str:
        return data.hex()

    @staticmethod
    def hex_decoding(data: str)->bytes:
        return bytes.fromhex(data)

    @staticmethod
    def b64_format(data: bytes)->str:
        return base64.b64encode(data).decode('utf-8')

    @staticmethod
    def b64_decoding(data: str)->bytes:
        return base64.b64decode(data.encode('utf-8'))

    @staticmethod
    def encrypt_data(key, data: str)->(str, str, str): 
        n = Random.new().read(12)
        cipher = AES.new(key, AES.MODE_GCM, nonce=n)
        ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
        return _EncryptionTools.b64_format(ciphertext), _EncryptionTools.hex_format(n), _EncryptionTools.hex_format(tag)

    @staticmethod
    def decrypt_data(key: str, ciphertext:str, nonce:str, tag:str)->str|None:
        key = _EncryptionTools.b64_decoding(key)
        ciphertext = _EncryptionTools.b64_decoding(ciphertext)
        nonce = _EncryptionTools.hex_decoding(nonce)
        tag = _EncryptionTools.hex_decoding(tag)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        data = cipher.decrypt(ciphertext).decode('utf-8')
        try:
            cipher.verify(tag)
        except Exception as ex:
            print(ex)
            return None
        return data

class Platform:
    @staticmethod
    def is_win():
        return sys.platform == 'win32'

    @staticmethod
    def is_linux():
        return sys.platform == 'linux'

    @staticmethod
    def separator():
        if Platform.is_win():
            return '\\'
        elif Platform.is_linux():
            return '/'
        else:
            raise Exception("Unknown separator")
    
def basicSetup(home: str):
    if not os.path.exists(home):
        os.makedirs(home)

    if os.path.exists(home) and not os.path.isdir(home):
        raise Exception(f"Home {home} is not directory!")

    if Platform.is_win():
        import ctypes
        FILE_ATTRIBUTE_HIDDEN = 0x02
        try:
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(home))
            if attrs == -1:
                raise FileNotFoundError(f"Path not found: {path}")
            new_attributes = attrs | FILE_ATTRIBUTE_HIDDEN
            ctypes.windll.kernel32.SetFileAttributesW(path, new_attributes)
        except Exception as e:
            print(f"Error: {e}")
            return False



def _has_file(home, name: str) -> bool:
    return len([fileName for fileName in os.listdir(home) if fileName == name and isfile(join(home, fileName))]) == 1


def _get_file_content(path: str) -> Optional[str]:
    if os.path.exists(path):
        with open(path, "r") as file:
            return file.read().strip()
    else:
        return None


_PROXY_VAL = "proxy"


class Profile:
    _emtpy:'Profile' = None
    SEP="___"
    def __init__(self, profile: str):
        if getattr(self, '_is_singleton', False):
            if getattr(self, '_initialized', False):
                return 
            self._initialized = True
            self.name = ''
        else:
            self.name = profile
    
    def __new__(cls, profile: str):
        if profile == "" or profile is None:
            if cls._emtpy is None:
                cls._emtpy = super().__new__(cls)
                cls._emtpy._is_singleton = True
            return cls._emtpy
        else:
            instance = super().__new__(cls)
            instance._is_singleton = False
            return instance
    
    def of_key(self, key: str)->str:
        return f"{self.as_prefix()}{key}"

    def as_name(self, key: str)->str:
        return f"{self.name} - {key}"
    
    def as_prefix(self)->str:
        return f"{self.name}{Profile.SEP}"

    def entry_of(key: str) -> 'Entry':
        return Entry(key, self)

    def is_empty(self)->bool:
        return getattr(self, '_is_singleton', False)
    
    @staticmethod
    def emptyProfile() -> 'Profile':
        if Profile._emtpy is None:
            return Profile(None)
        else:
            return Profile._emtpy

Profile.emptyProfile()
    
class Entry:
    def __init__(self, key: str, profile: Profile):
        self.key = key
        self.profile = profile
    
    def name(self):
        return self.profile.as_name(self.key)
    
    def of_key(self):
        return self.profile.of_key(self.key)
    
    def has_profile(self)->bool:
        return not self.profile.is_empty()

    @staticmethod
    def laod_from_str(data: str) -> 'Entry':
        splited = data.split(Profile.SEP)
        if len(splited) == 1:
            return Entry(data, None)
        elif len(splited) == 2:
            return Entry(splited[1], Profile(splited[0]))
        else:
            raise Exception(f"The data passing is not valid entry. [{data}]")
    
    def simple(key: str) -> 'Entry':
        return Entry(key, Profile.emptyProfile())

    def with_profile(key: str, profile_name: str)->'Entry':
        return Entry(key, Profile(profile_name))

    


class CustApp:

    def _get_credential_file(self)->str:
        return os.path.abspath(join(self.home, "cc"))
    
    def _get_cc_hash_str(self)->str:
        return _EncryptionTools.b64_format(hashlib.sha256(self._get_credential_file().encode('utf-8')).digest())

    def _get_default_cred(self)->bytes:
        """
        Hashes an input string, uses the hash as a seed for the random number generator,
        and returns the first 32 random bits as an integer.
        """
        seed_value = self._get_cc_hash_str()
        random.seed(seed_value)
        random_bits = random.getrandbits(256).to_bytes(32, byteorder='big')
        return random_bits


    def __init__(self, home: Path, name: str):
        self.home = join(CustApp.defaultAppPath(home), name)

        if os.path.exists(self._get_credential_file()) and not os.path.isfile(self._get_credential_file()):
            raise Exception("Credential file path contains non file structure")

        if not os.path.exists(self._get_credential_file()):
            with open(self._get_credential_file(), "w") as f:
                f.write(self._get_cc_hash_str())
        elif Path(self._get_credential_file()).stat().st_size == 0:
            with open(self._get_credential_file(), "w") as f:
                f.write(self._get_cc_hash_str())
        
        if not os.path.exists(self._get_credential_file()):
            raise Exception("Missing the credential file")
        

    def has_proxy(self) -> bool:
        return _has_file(self.home, _PROXY_VAL)

    def proxy_value(self):
        return _get_file_content(os.join(self.home, _PROXY_VAL))

    def proxy_valid(self) -> bool:
        if self.has_proxy():
            value = self.proxy_value()
            os.path.exists(value) and os.path.isdir(value)
            return True
        else:
            return True

    def set_kv(self, key: Entry, value: str):
        self._set_value(key, value)
    

    def _get_deen_key(self)->str:
        return _EncryptionTools.b64_format(self._get_default_cred())

    def get_kv(self, key: Entry) -> Optional[str]:
        if self.has_kv(key):
            data = _get_file_content(self._key_value_name(key.of_key()))
            nonce = _get_file_content(self._key_nonce_name(key.of_key()))
            tag = _get_file_content(self._key_tag_name(key.of_key()))
            if data is None or nonce is None or tag is None:
                raise Exception("The data structure is not completed")
            return _EncryptionTools.decrypt_data(self._get_deen_key(), data, nonce, tag)
        else:
            return None
        return _get_kv(self.home, key)
    
    def _set_value(self, key:Entry, data: str):
        with open(self._key_value_name(key.of_key()), "w") as key_file:
            with open(self._key_nonce_name(key.of_key()), "w") as nonce_file:
                with open(self._key_tag_name(key.of_key()), "w") as tag_file:
                    ciphertext, nonce, tag = _EncryptionTools.encrypt_data(self._get_default_cred(), data)
                    key_file.write(ciphertext)
                    nonce_file.write(nonce)
                    tag_file.write(tag)
            

    def rm_kv(self, key: Entry) -> Optional[str]:
        if self.has_kv(key):
            v = self.get_kv(key)
            os.remove(self._key_value_name(key.of_key()))
            os.remove(self._key_nonce_name(key.of_key()))
            os.remove(self._key_tag_name(key.of_key()))
            return v
        else:
            return None
    

    def has_kv(self, entry: Entry) -> Optional[bool]:
        return True if entry.of_key() in self._keys() else False

    def list(self, profile:Profile=None, no_profile: bool = False):
        if profile is None:
            profile=Profile.emptyProfile()
        if no_profile:
            return list(self._keys(no_profile=True))
        elif not profile.is_empty():
            return list(self._keys(profile=profile))
        else:
            return list(self._keys())

    
    def _key_value_name(self, key: str)->str:
        return join(self.home, f"{key}.kv")

    def _key_nonce_name(self, key: str)->str:
        return join(self.home, f"{key}.kv.nonce")

    def _key_tag_name(self, key: str)->str:
        return join(self.home, f"{key}.kv.tag")

    def _keys(self, profile: Profile=None, no_profile:bool=False):
        if profile is None:
            profile = Profile.emptyProfile()
        for filename in os.listdir(self.home):
            if filename.endswith('.kv'):
                entry_str=filename[0:-3]
                if no_profile:
                    if Entry.laod_from_str(entry_str).has_profile():
                        continue
                    else:
                        yield entry_str
                elif not profile.is_empty():
                    if entry_str.startswith(profile.as_prefix()):
                        yield entry_str
                    else:
                        continue
                else:
                    yield entry_str
        

    @staticmethod
    def defaultAppPath(path: str)->str:
        p= join(path, ".pyXhCustApp")
        basicSetup(p)
        return p

    @staticmethod
    def appDefault(name: str):
        return CustApp(Path.home(), name)
