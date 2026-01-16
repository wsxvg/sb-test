import requests
import json
import time
import urllib3
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 优先从环境变量读取，如果没有则使用默认值
CONFIG = {
    "host": "https://ydh88.sintoyu.cn",
    "img_host": "https://kaifa.sintoyu.cn",
    "_ydhid": os.getenv("YDHID", "925A0C75146730FFF9078159F7E72C9A"),
    "_machineid": os.getenv("MACHINEID", "oztRg413C-XBkvyZdNF4zUYq7i6I"),
    "_username": os.getenv("USERNAME", "13666527113"),
    "_xcxappid": os.getenv("XCXAPPID", "wxebf4afe4b3c9a03d")
}

class StoreDeepScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.trust_env = False 
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MicroMessenger/7.0.20.1781 NetType/WIFI MiniProgramEnv/Windows",
            "Referer": "https://servicewechat.com/wxebf4afe4b3c9a03d/7/page-frame.html",
            "Content-Type": "application/x-www-form-urlencoded",
            "xweb_xhr": "1"
        })
        self.orgaid = None
        self.all_products = {} # FID -> ItemInfo
        self.category_tree = []
        self.leaf_gids = {} # 末端ID -> 家谱[L1, L2, L3]

    def login(self):
        print("🔑 正在登录...")
        url = f"{CONFIG['host']}/YdhLogin/checkLogin"
        data = {"_ydhid": CONFIG["_ydhid"], "_machineid": CONFIG["_machineid"], "_username": CONFIG["_username"], "_pwd": "", "_xcxappid": CONFIG["_xcxappid"], "_device": "X"}
        res = self.session.post(url, data=data, verify=False).json()
        if res.get("success") == 1:
            self.orgaid = res["result"]["orgaid"]
            return True
        return False

    def build_structure(self):
        print("📂 正在解析分类树并锁定末端节点...")
        l1_url = f"{CONFIG['host']}/ydhgoodsgroup/GetGoodsGroupLevel1"
        l1_list = self.session.post(l1_url, data={"_ydhid": CONFIG["_ydhid"], "_parentid": "0", "_orgaid": self.orgaid}).json().get("result") or []
        
        for item1 in l1_list:
            g1_id = item1["FValue1"]
            l2_url = f"{CONFIG['host']}/ydhgoodsgroup/GetGoodsGroupLevel2"
            l2_res = self.session.post(l2_url, data={"_ydhid": CONFIG["_ydhid"], "_topparentid": g1_id, "_depth": "2", "_orgaid": self.orgaid}).json()
            l2_raw = l2_res.get("result", {}).get("FValue2") or []
            
            processed_subs = []
            for sub in l2_raw:
                g2_id = sub.get("FGroupID") or sub.get("FValue1")
                children = sub.get("FChild") or []
                g3_list = []
                
                if children:
                    for child in children:
                        g3_id = child.get("FGroupID")
                        self.leaf_gids[g3_id] = [g1_id, g2_id, g3_id] # 记录家谱
                        g3_list.append({"id": g3_id, "name": child.get("FGroupName"), "img": child.get("FImageUrl")})
                else:
                    self.leaf_gids[g2_id] = [g1_id, g2_id] # 二级即是末端

                processed_subs.append({"id": g2_id, "name": sub.get("FGroupName") or sub.get("FValue2"), "img": sub.get("FImageUrl"), "children": g3_list})
            self.category_tree.append({"id": g1_id, "name": item1["FValue2"], "subs": processed_subs})

    def scrape_category(self, gid, family):
        """针对一个末端分类，爬取它的所有分页"""
        page = 0
        while True:
            url = f"{CONFIG['host']}/ydhgoodsgroup/getgoodslist"
            payload = {
                "_ydhid": CONFIG["_ydhid"], "_orgaid": self.orgaid, "_groupid": gid,
                "_pageno": page, "_pagesize": 100, "_goodslistmode": "5"
            }
            try:
                res = self.session.post(url, data=payload, timeout=15).json()
                items = res.get("result") or []
                if not items: break
                
                for it in items:
                    fid = it["FItemID"]
                    if fid not in self.all_products:
                        self.all_products[fid] = {
                            "id": fid, "name": it.get("FName"), "num": it.get("FNumber"),
                            "price": it.get("FPriceV"), "unit": it.get("FBuyUnit"),
                            "sale_info": it.get("FSaleInfo"), "min_qty": it.get("FOrderMinQtyDesc"),
                            "img": it.get("FImageUrl"), "brand": it.get("FName", "").split(' ')[0],
                            "hot": it.get("FOrderCount", 0), "gids": family # 继承家谱
                        }
                    else:
                        # 如果商品已存在（可能在别的分类也出现了），合并分类ID
                        existing_gids = set(self.all_products[fid]["gids"])
                        existing_gids.update(family)
                        self.all_products[fid]["gids"] = list(existing_gids)

                if len(items) < 36: break
                page += 1
            except: break

    def run(self):
        if not self.login(): return
        self.build_structure()
        
        target_list = list(self.leaf_gids.items())
        total = len(target_list)
        print(f"🚀 开始按分类深度爬取，共 {total} 个末端分类...")

        # 使用多线程加快速度
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self.scrape_category, gid, family) for gid, family in target_list]
            for i, _ in enumerate(as_completed(futures)):
                if (i+1) % 10 == 0:
                    print(f"  ☕ 已完成 {i+1}/{total} 个分类的扫描...")

        with open("products_db.json", "w", encoding="utf-8") as f:
            json.dump({
                "metadata": {"update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                "category_tree": self.category_tree,
                "products": list(self.all_products.values())
            }, f, ensure_ascii=False, indent=2)
        print(f"✨ 深度抓取完成！入库不重复商品: {len(self.all_products)} 个。")

if __name__ == "__main__":
    StoreDeepScraper().run()