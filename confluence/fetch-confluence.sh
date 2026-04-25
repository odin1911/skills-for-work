#!/bin/bash
# 从 Confluence 获取页面 HTML 内容
# 用法: ./ai-tools/fetch-confluence.sh <pageId> [output.html]
# 示例: ./ai-tools/fetch-confluence.sh 165120525
#       ./ai-tools/fetch-confluence.sh 165120525 ai-tools/api-docs-165120525.html

PAGE_ID="${1:-165120525}"
OUTPUT="${2:-}"
COOKIE="seraph.confluence=165347422%3A64ba62497bebbac350f93d623bd4889344bb5dd8; JSESSIONID=ED106B2EAC6892AB6736A5EA8B777DBA"

RESULT=$(curl -s \
  -H "Cookie: $COOKIE" \
  "https://confluence.alo7.cn/rest/api/content/${PAGE_ID}?expand=body.view" \
| jq -r '.body.view.value')

if [ -n "$OUTPUT" ]; then
  echo "$RESULT" > "$OUTPUT"
  echo "已保存到: $OUTPUT"
else
  echo "$RESULT"
fi
