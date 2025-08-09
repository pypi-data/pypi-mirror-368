# 🤖 commity

使用大语言模型（LLM）生成智能 Git 提交信息的工具，支持 Conventional Commits 格式和 emoji 插入。

## 🔧 安装

```bash
pip install commity
```

## 🔁 更改默认模型为其它模型（如 Gemini、OpenAI 等）

### ✨ 方法一：运行命令时指定模型参数

```Bash
commity --provider gemini --model gemini-2.5-flash --base_url https://generativelanguage.googleapis.com --api_key <your-api-key>
```

or

```Bash
commity \
--provider gemini \
--model gemini-2.5-flash \
--base_url https://generativelanguage.googleapis.com \
--api_key <your-api-key>
```

### 🌱 方法二：设置环境变量作为默认值

你可以在 .bashrc、.zshrc 或 .env 文件中添加：

```Bash
export LLM_PROVIDER=gemini
export LLM_MODEL=gemini-2.5-flash
export LLM_BASE_URL=https://generativelanguage.googleapis.com
export LLM_API_KEY=your-api-key
```

## 🚀 使用

```Bash
commity
commity --lang zh # 使用中文
commity --emoji # 包含 emoji
```
