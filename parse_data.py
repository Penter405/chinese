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

    # 1. 解析國字注音
    # 匹配例如 "1. 赤鼻「磯」：ㄐㄧ" 或 "2. 「ㄇㄧㄢˇ」懷：緬"
    ch_pron_section = re.search(r'一、國字注音(.*?)二、注釋', content, re.DOTALL)
    if ch_pron_section:
        lines = ch_pron_section.group(1).strip().split('\n')
        for line in lines:
            match = re.match(r'^\d+\.\s*(.+?)：\s*(.+)$', line.strip())
            if match:
                q = match.group(1).strip()
                a = match.group(2).strip()
                data["國字注音"].append({"question": q, "answer": a})

    # 2. 解析注釋
    # 匹配例如 "②「既」望：已經，此指已過。" 或 "縱一葦之所「如」：往。"
    annotation_section = re.search(r'二、注釋(.*?)三、默書', content, re.DOTALL)
    if annotation_section:
        lines = annotation_section.group(1).strip().split('\n')
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            # 移除開頭可能有的序號或圈圈數字如 ②, ⑰, ○51
            cleaned_line = re.sub(r'^[②④⑥⑧⑨⑩⑫⑬⑰⑱⑲㉑㉓㉔㉕㉚㉛㉞㉟㊱㊲㊳㊴㊵㊷㊸㊺㊻㊽㊾○\d\s]+', '', line_str)
            if '：' in cleaned_line:
                parts = cleaned_line.split('：', 1)
                q = parts[0].strip()
                a = parts[1].strip()
                data["注釋"].append({"question": q, "answer": a})

    # 3. 解析默書
    # 默書部分因為表格與提示較多，此處抓取「提示/段落名」作為題目，「詩詞句」作為答案
    dictation_section = re.search(r'三、默書(.*)$', content, re.DOTALL)
    if dictation_section:
        text = dictation_section.group(1)
        # 移除標題如 1.〈赤壁賦〉第二段
        text = re.sub(r'\d+\.〈.*?〉.*?\n', '', text)
        lines = text.strip().split('\n')
        
        current_q = ""
        for line in lines:
            line_str = line.strip()
            if not line_str or "班" in line_str or "姓名" in line_str:
                continue
            
            # 如果包含括號如 (2 句) 或 寫景(淒涼之景)，通常是題目提示
            if '(' in line_str or ')' in line_str or '〈' in line_str or '表現' in line_str or '歡唱' in line_str or '洞簫' in line_str or '簫聲' in line_str or '議論' in line_str or '記敘' in line_str or '詠物' in line_str or '贊人' in line_str:
                current_q = line_str
            else:
                if current_q and line_str:
                    # 避免重複加入
                    data["默書"].append({"question": current_q, "answer": line_str})
                    current_q = "" # 配對完清空

    # 寫入成 JSON 檔案給 HTML 讀取
    with open('quiz_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("成功！已生成 quiz_data.json，共解析了：")
    print(f"國字注音: {len(data['國字注音'])} 題")
    print(f"注釋: {len(data['注釋'])} 題")
    print(f"默書: {len(data['默書'])} 題")

if __name__ == "__main__":
    parse_questions("questions.txt")