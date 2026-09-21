import os
import requests
from supabase import create_client

# 初始化 Supabase
supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

# 从 Jira API 获取数据
jira_url = "https://your-domain.atlassian.net/rest/api/3/search"
headers = {"Authorization": f"Bearer {os.environ['JIRA_TOKEN']}"}
# 这里可以使用 JQL 过滤出你需要的特定项目或类型的 ticket
response = requests.get(jira_url, headers=headers).json()

for issue in response.get('issues', []):
    fields = issue['fields']
    
    # 根据你 Jira 中的自定义字段判断产品种类
    # 示例逻辑：如果是 OPCC，就归类为 RHAzyme
    raw_product = fields.get('customfield_XXXXX', '')
    product_type = "RHAzyme - OPCC" if "OPCC" in raw_product else f"Emulsion - {raw_product}"

    data = {
        "id": issue['key'],
        "created_date": fields['created'],
        "product_type": product_type,
        "amount": fields.get('customfield_YYYYY', 0),
        "status": fields['status']['name'],
        "resolved_at": fields.get('resolutiondate')
    }
    # upsert 会根据 id 自动覆盖旧数据或创建新数据
    supabase.table('jira_data').upsert(data).execute()
