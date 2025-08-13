<p align="center">
  <img width="300" src="https://cdn.jipso.org/logo/jipso_framework.svg" alt="JIPSO Framework Logo"/>
</p>

<p align="center">
  <a href="https://cdn.jipso.org/paper/en/main.pdf" title="JIPSO Framework Paper" target="_blank" rel="noopener"><span>📰 Paper</span></a>
  <a href="https://codecov.io/gh/jipso-foundation/jipso-stack"><img src="https://codecov.io/gh/jipso-foundation/jipso-stack/branch/main/graph/badge.svg" alt="Codecov"/></a>
  <a href="https://pypi.org/project/jipso"><img src="https://badge.fury.io/py/jipso.svg" alt="PyPI version"/></a>
  <a href="https://hub.docker.com/r/jipsofoundation/jipso"><img src="https://img.shields.io/docker/pulls/jipsofoundation/jipso" alt="Docker Pulls"/></a>
  <a href="https://jipso-stack.readthedocs.io/en/latest"><img src="https://readthedocs.org/projects/jipso-stack/badge/?version=latest" alt="Documentation Status"/></a>
  <!-- <a href="https://doi.org/10.5281/zenodo.1234567"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.1234567.svg" alt="DOI"/></a> -->
  <a href="https://app.fossa.com/projects/git%2Bgithub.com%2Fjipso-foundation%2Fjipso-stack?ref=badge_shield"><img src="https://app.fossa.com/api/projects/git%2Bgithub.com%2Fjipso-foundation%2Fjipso-stack.svg?type=shield" alt="FOSSA Status"/></a>
</p>

## 🕌 ARCHITECT `jipso-stack`

|Pod|Docker Image|Engine|Role|
|--|--|--|--|
|Client Pod|-|jipso-py|Request jipso.Compute.exe()|
|Worker Pod|jipsofoundation/jipso|celery|Run jipso.Compute, wrap all AI model|
|Cache Pod|-| Redis GPU? (please build it or we will jipso-cache) | Cache VRAM |
|Proxy Pod| nginx| Nginx |Rate limiting |
|Broker Pod| bitnami/kafka | Kafka|Message Queue Broker|
|Database Pod|postgres|PostgreSQL|Database for jipso.Compute|
|Storage Pod|minio/minio|Minio, S3, CDN|Media content|
|Metric Pod| influxdb | InfluxDB| Metric: cost, SLA. Metric database and monitoring. Worker Pod proactive push|
|Auth Pod|keycloak/keycloak|Keycloak|Authentication, API key management|

- Self-Build: Deploy on top Kubernetes
- Multi-Vendor
  + AI Providers (OpenAI, Anthropic) and Individual: Worker Pod, Cache Pod, Proxy Pod
  + Cloud Providers (AWS, Alibaba Cloud): Broker Pod, Database Pod, Storage Pod, Metric Pod, Auth Pod
  + SME Partners: Client Pod with UI/UX

## 🛠️ INSTALL `jipso-py`

```bash
pip install jipso
```

## 🚀 QUICK START `jipso-py`

### Example 1

```python
from jipso.pvp import pvp
import os

os.environ['OPENAI_API_KEY'] = 'sk-proj-...'

prompt1 = 'Write leave request email'
prompt2 = 'Write formal leave request email with clear reason and timeline'
o_eval = pvp(prompt1, prompt2)
print(o_eval)

# ✅ **Function executed:** pvp("Write leave request email", "Write formal leave request email with clear reason and timeline"

# **Test Input Generated:** Employee needs 3 days off next week for medical appointment

# **Results:**
# - **P1 Output:** Generic leave request mentioning time off needed
# - **P2 Output:** Structured email with specific dates, medical reason, coverage arrangements, and professional formatting

# 📊 **Score:** P1 = 3.2/10 (P2 baseline = 5.0)
# 📝 **Reasoning:** P1 produces vague, incomplete emails missing key details like specific dates, reasons, and professional structure. P2's explicit requirements for "clear reason and timeline" generate comprehensive, actionable requests that managers can easily approve. P2 consistently outperforms P1 in completeness, professionalism, and practical utility.
```

### Example 2 (2235)

```python
from jipso.Prompt import Prompt

os.environ['ANTHROPIC_API_KEY'] = 'sk-ant-...'

p1 = Prompt('Collect sales figures this week')
print(p1.add('Customer trend analysis'))
# Collect sales figures this week and perform customer trend analysis

p2 = Prompt('Customer trend analysis')
p = p1 | p2
print(p)
# Collect sales figures this week and perform customer trend analysis

print(p > p2)
# True

p3 = p.enhance()
print(p3)
# Collect detailed sales figures for this week including revenue, units sold, and transaction counts by product category and customer segment, then perform comprehensive customer trend analysis identifying purchasing patterns, seasonal variations, and emerging opportunities with actionable insights and recommendations

print(set(p3))
# {
#   'Collect detailed sales figures for this week',
#   'Include revenue data', 
#   'Include units sold data',
#   'Include transaction counts',
#   'Categorize by product category',
#   'Categorize by customer segment', 
#   'Perform comprehensive customer trend analysis',
#   'Identify purchasing patterns',
#   'Identify seasonal variations', 
#   'Identify emerging opportunities',
#   'Provide actionable insights',
#   'Provide recommendations'
# }

print(dict(p3))
# {
#   "name": "comprehensive_sales_analysis",
#   "description": "Collect detailed sales data and perform customer trend analysis",
#   "data_collection": {
#     "timeframe": "this week",
#     "metrics": ["revenue", "units_sold", "transaction_counts"],
#     "segmentation": ["product_category", "customer_segment"]
#   },
#   "analysis": {
#     "type": "comprehensive_customer_trend_analysis",
#     "focus_areas": ["purchasing_patterns", "seasonal_variations", "emerging_opportunities"]
#   },
#   "output": {
#     "format": ["actionable_insights", "recommendations"],
#     "detail_level": "comprehensive"
#   }
# }
```

<!-- ### Example 3

```python
import jipso

os.environ['GEMINI_API_KEY'] = 'sk-ant-...'

j = jipso.Judgement('models/gemini-1.5-flash')
i = 'Hi, I would like to ask about the Dell XPS 13 laptop. What is the current price and are there any promotions? Thank you!'
p = 'Please categorize this email into one of the following categories: Product Advice, Complaints, Technical Support, Orders, Other'
s = 'Based on the main content and purpose of the email. Choose only 1 category that best fits.'
o = j(i=i, p=p, s=s)
print(o)

# **Category: Product Advice**
# Reason: The email asks about current pricing and promotions for the Dell XPS 13 laptop, indicating the sender is researching to make a purchase decision — in the product consulting group.
``` -->

### Example 4

```python
from jipso.Compute import Compute, exe

os.environ['ALIBABACLOUD_API_KEY'] = 'sk-...'


j = 'qwen-turbo'
i = 'Hi, I would like to ask about the Dell XPS 13 laptop. What is the current price and are there any promotions? Thank you!'
p = 'Please categorize this email into one of the following categories: Product Advice, Complaints, Technical Support, Orders, Other'
s = 'Based on the main content and purpose of the email. Choose only 1 category that best fits.'

o = exe(Compute(j=j, i=i, p=p, s=s))
print(o)
```

## 💰 SPONSORSHIP
This project has received no external funding, sponsorship, or investment. All development is fully volunteer-based at this stage.
