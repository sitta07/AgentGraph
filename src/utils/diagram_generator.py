import os
import re
import base64
import requests

def extract_and_save_diagram(text: str, round_num: int):
    """
    [Senior Version: Robust Extraction]
    1. Find ALL diagrams in Mermaid blocks
    2. Convert each to image
    3. Save locally (e.g. diagram_round_1_fig1.png)
    """
    # Use re.findall to extract all blocks found (returns list)
    matches = re.findall(r"```mermaid\n(.*?)\n```", text, re.DOTALL)
    
    if not matches:
        print("ℹ️  [TOOL] No Mermaid Diagram found in this round")
        return

    print(f"🎨 [TOOL] Found {len(matches)} Diagram(s) in round {round_num}! Creating images...")
    
    # Loop through and create each image
    for i, mermaid_code in enumerate(matches, 1):
        mermaid_code = mermaid_code.strip()
        
        # Convert to Base64
        try:
            graphbytes = mermaid_code.encode("utf8")
            base64_bytes = base64.b64encode(graphbytes)
            base64_string = base64_bytes.decode("ascii")
            
            url = f"https://mermaid.ink/img/{base64_string}"
            
            # Download image and save
            response = requests.get(url, timeout=10)  # Add timeout to prevent hanging
            if response.status_code == 200:
                os.makedirs("diagrams", exist_ok=True)
                # Generate unique filename e.g. fig1, fig2
                filename = f"diagrams/round_{round_num}_fig{i}.png"
                
                with open(filename, 'wb') as file:
                    file.write(response.content)
                print(f"✅ [TOOL] Image {i} saved successfully! Location: {filename}")
            else:
                print(f"⚠️  [TOOL] Image {i} creation failed (Status: {response.status_code}). Reason: Mermaid code may be invalid or have character issues")
                
        except Exception as e:
            print(f"⚠️  [TOOL] Error creating image {i}: {e}")