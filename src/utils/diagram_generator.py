import os
import re
import base64
import requests

def extract_and_save_diagram(text: str, round_num: int):
    """
    [Senior Version: Robust Extraction]
    1. ควานหา Diagram 'ทั้งหมด' ที่อยู่ในบล็อก mermaid
    2. ลองแปลงเป็นภาพทีละอัน
    3. เซฟลงเครื่อง (เช่น diagram_round_1_fig1.png)
    """
    # ใช้ re.findall ดึงทุกบล็อกที่เจอ (คืนค่าเป็น list)
    matches = re.findall(r"```mermaid\n(.*?)\n```", text, re.DOTALL)
    
    if not matches:
        print("ℹ️ [TOOL] ไม่พบ Mermaid Diagram ในข้อความรอบนี้")
        return

    print(f"🎨 [TOOL] พบ {len(matches)} Diagram(s) ในข้อความรอบที่ {round_num}! กำลังลองสร้างภาพ...")
    
    # วนลูปสร้างรูปทีละอัน
    for i, mermaid_code in enumerate(matches, 1):
        mermaid_code = mermaid_code.strip()
        
        # แปลงเป็น Base64
        try:
            graphbytes = mermaid_code.encode("utf8")
            base64_bytes = base64.b64encode(graphbytes)
            base64_string = base64_bytes.decode("ascii")
            
            url = f"https://mermaid.ink/img/{base64_string}"
            
            # โหลดภาพและเซฟ
            response = requests.get(url, timeout=10) # เพิ่ม timeout กันค้าง
            if response.status_code == 200:
                os.makedirs("diagrams", exist_ok=True)
                # ตั้งชื่อไฟล์ให้ไม่ซ้ำ เช่น fig1, fig2
                filename = f"diagrams/round_{round_num}_fig{i}.png"
                
                with open(filename, 'wb') as file:
                    file.write(response.content)
                print(f"✅ [TOOL] เซฟภาพ {i} สำเร็จ! ดูได้ที่: {filename}")
            else:
                print(f"⚠️ [TOOL] ภาพ {i} สร้างไม่สำเร็จ (Status: {response.status_code}). สาเหตุ: โค้ด Mermaid อาจจะเน่า หรือชื่อตัวละครผิด")
                # สำหรับ Senior: แอบ print โค้ดที่เน่ามาดูหน่อย
                # print(f"[DEBUG: Mermaid Code ที่เน่า]\n{mermaid_code}\n")
                
        except Exception as e:
            print(f"⚠️ [TOOL] เกิด Error ตอนสร้างภาพ {i}: {e}")