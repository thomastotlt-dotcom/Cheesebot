import time
import threading
import requests
import random

class Chai():
    def __init__(self, refresh_token, user_uid):
        self.refresh_token = refresh_token
        self.user_uid = user_uid
        
        self.jwt_key = self._get_jwt()
        self._jwt_lock = threading.Lock()
        
        self._refresh_thread = threading.Thread(target=self._jwt_refresh_loop, daemon=True)
        self._refresh_thread.start()
        
        self.bots = {
            "Luna": "_bot_de18e0ac-9552-4604-a305-0d64a44088d2",
            "robot": "_bot_9fd1e755-51fd-4c4c-881a-793816a2d912",
            "bob the chicken": "_bot_57894ba3-c08b-43a6-9a16-a8340c2b4fff",
            "woman cool_monke": "_bot_b735a3c7-1250-44b2-84e1-45b2f1634442",
            "freaky ahh bot": "_bot_40900879-c6f7-4ff2-ac56-842f5d30fae6",
            "actual hater": "_bot_c2d9ba39-0830-4d22-a6ec-c84f0b0f6ae1",
            "Listener": "_bot_ac827bf9-215d-43db-9dc7-3019432579ef",
            "yapper": "_bot_5873d0c8-4801-433c-914e-e871f3dba3dc",
            "transformer": "_bot_c1793d4f-c24d-4d36-b375-f89ce0e71aa8",
            "007n7": "_bot_ba486db7-24f6-444b-87df-d27521988ee6",
            "c00lkid": "_bot_d7d5609b-8898-4693-b79e-d021991deb92",
            "Queen Crimson": "_bot_7d7d6986-1817-4723-884e-6818b7d41357",
            "og cool monke": "_bot_eb6113ab-f9ec-419b-be66-fba2a9d87cb1",
            "pibble": "_bot_7feb3805-172a-4943-9f16-45134705c563",
            "party noob": "_bot_90b18da6-1fdd-43e3-8a92-8d061112d593",
            "azure": "_bot_8569604e-0db7-4d83-80ab-bcc1c5f87586"
        }
    
    def _get_jwt(self):
        token_payload = {
            "grantType": "refresh_token",
            "refreshToken": self.refresh_token
        }

        getToken = requests.post("https://securetoken.googleapis.com/v1/token?key=AIzaSyDlCazdn_bziqDVwQkDroR8eK4GVaEHawU", json=token_payload).json()
        return getToken["access_token"]
    
    def _jwt_refresh_loop(self):
        while True:
            time.sleep(3300)
            
            with self._jwt_lock:
                self.jwt_key = self._get_jwt()
                
    def get_char_info(self, bot_uid="_bot_de18e0ac-9552-4604-a305-0d64a44088d2"):
        with self._jwt_lock:
            token = self.jwt_key
            
        headers = {
            "Authorization": "Bearer " + token
        }
        
        try:
            res = requests.get(f"https://bot-service-us1-shdxwd54ta-uc.a.run.app/chatbots/v2/{bot_uid}", headers=headers, timeout=60).json()
            
            return res["data"]
            
        except:
            return None
        
    def gen_conv_id(self):
        conv_id = random.randint(1000000000000000000, 9999999999999999999)
            
        return conv_id
                
    def message(self, msg="__first", conv_id: int = None, bot_uid="_bot_de18e0ac-9552-4604-a305-0d64a44088d2"):
        with self._jwt_lock:
            token = self.jwt_key
            
        payload = {
            "bot_uid": bot_uid,
            "user_uid": self.user_uid,
            "conversation_id": f"{bot_uid}_{self.user_uid}_{conv_id}",
            "text": msg,
            "remote_config_ids": [
                "",
                "default",
                "default",
                "default",
                "premium_30_ultra_70",
                "default",
                "0323_west_coast_safety_popup_rollout_enable_safety_popup_ios",
                "1120_ad_prompt_rollout_existing_users_app_one_in_18_upsell_ultra",
                "0311_kontext_video_kontext_without_video_ios",
                "20260216_existing_users_daily_feed_trending_feed",
                "0224_t1_discount_existing_ios_70_percent_off_first_month_ios"
            ],
            "model": "default",
            "guanaco": False,
            "user_state": {
                "account_creation_timestamp": 1713663656112,
                "location": "US/tx",
                "operating_system": "android",
                "nsfw_enabled": True,
                "app_version": None,
                "appsflyer_uid": None,
                "subscribed": True,
                "ultra": True
            }
            }
        
        headers = {
            "Authorization": "Bearer " + token
        }
        
        try:
            res = requests.post("https://bot-responder-eu-shdxwd54ta-nw.a.run.app/send_message", json=payload, headers=headers, timeout=60).json()
            
            return res["response"]
            
        except:
            return None


