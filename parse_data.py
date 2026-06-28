import re
import json

def parse_questions(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    data = {
        "國字注音": [],
        "注釋": [],
        "默書": []
    }

    # 1. 解析【國字注音】
    ch_pron_section = re.search(r'一、國字注音(.*?)二、注釋', content, re.DOTALL)
    if ch_pron_section:
        lines = ch_pron_section.group(1).strip().split('\n')
        for line in lines:
            line_str = line.strip()
            match = re.match(r'^\d+\.\s*(.+?)：\s*(.+)$', line_str)
            if match:
                q = match.group(1).strip()
                a = match.group(2).strip()
                data["國字注音"].append({"question": q, "answer": a})

    # 2. 解析【注釋】
    annotation_section = re.search(r'二、注釋(.*?)三、默書', content, re.DOTALL)
    if annotation_section:
        lines = annotation_section.group(1).strip().split('\n')
        for line in lines:
            line_str = line.strip()
            if not line_str or line_str == "1":
                continue
            cleaned_line = re.sub(r'^[②④⑥⑧⑨⑩⑫⑬⑰⑱⑲㉑㉓㉔㉕㉚㉛㉞㉟㊱㊲㊳㊴㊵㊷㊸㊺㊻㊽㊾○\d\s]+', '', line_str).strip()
            if '：' in cleaned_line:
                parts = cleaned_line.split('：', 1)
                q = parts[0].strip()
                a = parts[1].strip()
                data["注釋"].append({"question": q, "answer": a})

    # 3. 解析【默書】（全面優化：改用狀態累積，避免漏掉跨行或有空格的詩句）
    dictation_section = re.search(r'三、默書(.*)$', content, re.DOTALL)
    if dictation_section:
        text = dictation_section.group(1)
        # 濾掉大標題如 1.〈赤壁賦〉
        text = re.sub(r'\d+\.〈.*?〉.*?\n', '', text)
        lines = text.strip().split('\n')
        
        current_q = ""
        current_a_chunks = []

        for line in lines:
            line_str = line.strip()
            if not line_str or "班" in line_str or "姓名" in line_str:
                continue
            
            # 判斷是否為「題目提示行」
            is_question_line = ('(' in line_str or ')' in line_str or 
                                any(k in line_str for k in ['表現', '歡唱', '洞簫', '簫聲', '議論', '記敘', '寫景', '詠物', '贊人']))
            
            if is_question_line:
                # 在換下一個題目之前，如果前面已經累積了答案，先存起來
                if current_q and current_a_chunks:
                    full_answer = " ".join(current_a_chunks)
                    data["默書"].append({"question": current_q, "answer": full_answer})
                
                # 切換到新題目
                current_q = line_str
                current_a_chunks = []
            else:
                # 這是答案行（或者答案的一部分），丟進陣列累積起來
                if current_q:
                    current_a_chunks.append(line_str)
        
        # 處理最後一題
        if current_q and current_a_chunks:
            full_answer = " ".join(current_a_chunks)
            data["默書"].append({"question": current_q, "answer": full_answer})

    # 寫入 JSON
    with open('quiz_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print("✨ 資料解析成功！已更新 quiz_data.json ✨")
    print(f"📊 國字注音共：{len(data['國字注音'])} 題")
    print(f"📊 注釋共：{len(data['注釋'])} 題")
    print(f"📊 默書共：{len(data['默書'])} 題 (應為 9 題)")

if __name__ == "__main__":
    parse_questions("questions.txt")