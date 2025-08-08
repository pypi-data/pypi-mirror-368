from typing import Optional

class CNBAPIError(Exception):    
    def __init__(self, 
                 detail: Optional[str] = None, 
                 status_code: Optional[int] = None,
                 ):
        self.detail = detail
        self.status_code = status_code
        self.errcode: Optional[int] = None
        self.errmsg: Optional[str] = None
        # 解析 detail
        if detail:
            try:
                import json
                detail_dict = json.loads(detail)
                self.errcode = detail_dict.get("errcode")
                self.errmsg = detail_dict.get("errmsg")
            except (json.JSONDecodeError, AttributeError):
                self.errmsg = detail        
        super().__init__(f"API request failed with status {status_code}, detail: {detail}")