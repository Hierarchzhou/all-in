#!/usr/bin/env python3
"""AI-RSS Curator - 让AI成为你的认知分身"""
import yaml, json, requests, anthropic
from pathlib import Path
from datetime import datetime

class RSSAIProcessor:
    def __init__(self):
        with open("config.yaml") as f:
            cfg = yaml.safe_load(f)
        self.client = anthropic.Anthropic(api_key=cfg['anthropic']['api_key'])
        self.miniflux = (cfg['miniflux']['url'], cfg['miniflux']['token'])
        self.threshold = cfg['scoring']['save_threshold']
        self.output = Path(cfg['output']['path'])
        self.output.mkdir(exist_ok=True)
    
    def fetch_unread(self):
        r = requests.get(f"{self.miniflux[0]}/v1/entries?status=unread", 
                        headers={"X-Auth-Token": self.miniflux[1]})
        return r.json().get('entries', [])
    
    def evaluate(self, entry):
        msg = self.client.messages.create(
            model="claude-sonnet-4-5-20250929", max_tokens=512,
            messages=[{"role": "user", "content": f"""评估文章价值(0-100):
标题: {entry['title']}
内容: {entry.get('content', '')[:500]}
返回JSON: {{"score": 分数, "reason": "理由"}}"""}])
        text = msg.content[0].text
        return json.loads(text[text.find('{'):text.rfind('}')+1])
    
    def save(self, entry, result):
        file = self.output / f"{datetime.now():%Y%m%d-%H%M%S}.md"
        file.write_text(f"""# {entry['title']}
**得分**: {result['score']}/100
**理由**: {result['reason']}
---
{entry.get('content', '')}
""", encoding='utf-8')
        print(f"  💾 保存: {file.name}")
    
    def run(self):
        print("🤖 AI-RSS Curator 启动\n")
        for i, entry in enumerate(self.fetch_unread(), 1):
            print(f"[{i}] {entry['title'][:50]}...")
            result = self.evaluate(entry)
            if result['score'] >= self.threshold:
                print(f"  ✅ {result['score']}分 - 保存")
                self.save(entry, result)
            else:
                print(f"  ⏭️  {result['score']}分 - 跳过")

if __name__ == "__main__":
    RSSAIProcessor().run()
