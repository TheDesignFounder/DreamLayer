# DreamLayer API Key Configuration Guide

## 🔑 Overview

DreamLayer now supports multiple AI service providers through API key integration. This guide explains how to configure and use Gemini and Anthropic APIs alongside existing providers.

## 🌟 Supported API Providers

### **Existing Providers** ✅
- **BFL (Black Forest Labs)**: FLUX models
- **OpenAI**: DALL-E 2, DALL-E 3
- **Ideogram**: Ideogram V3

### **New Providers** 🆕
- **Google Gemini**: Gemini 1.5 Pro, Flash, Vision, Experimental
- **Anthropic**: Claude 3.5 Sonnet, Claude 3.5 Haiku, Claude 3 Opus

---

## 🔧 Environment Configuration

### **1. .env File Setup**

Add the following API keys to your `.env` file in the project root:

```bash
# Existing API Keys
BFL_API_KEY=sk-your-bfl-api-key-here
OPENAI_API_KEY=sk-your-openai-api-key-here  
IDEOGRAM_API_KEY=your-ideogram-api-key-here

# New API Keys
GEMINI_API_KEY=your-gemini-api-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here
```

### **2. API Key Format**

Each provider has a specific key format:

| Provider | Key Format | Example |
|----------|------------|---------|
| **BFL** | `sk-bfl-...` | `sk-bfl-abc123def456...` |
| **OpenAI** | `sk-...` | `sk-proj-abc123def456...` |
| **Ideogram** | `idg-...` | `idg-abc123def456...` |
| **Gemini** | `gsk-...` or `AIza...` | `gsk-abc123def456...` |
| **Anthropic** | `sk-ant-...` | `sk-ant-api03-abc123def456...` |

### **3. Obtaining API Keys**

#### **Google Gemini API Key**
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Go to "Get API Key" → "Create API Key"
4. Copy the generated key (starts with `gsk-` or `AIza`)

#### **Anthropic API Key**
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign up/Sign in to your account
3. Go to "API Keys" → "Create Key"
4. Copy the generated key (starts with `sk-ant-`)

---

## 🚀 Available Models

### **Gemini Models**
- **Gemini 1.5 Pro** (`gemini-1.5-pro`): Advanced reasoning and long context
- **Gemini 1.5 Flash** (`gemini-1.5-flash`): Fast, efficient processing
- **Gemini Pro Vision** (`gemini-pro-vision`): Image understanding and analysis
- **Gemini Experimental** (`gemini-exp-1206`): Latest experimental features

### **Anthropic Models**
- **Claude 3.5 Sonnet** (`claude-3.5-sonnet`): Balanced performance and speed
- **Claude 3.5 Haiku** (`claude-3.5-haiku`): Fast, efficient processing
- **Claude 3 Opus** (`claude-3-opus`): Maximum capability and reasoning
- **Claude 3 Sonnet** (`claude-3-sonnet`): Balanced performance
- **Claude 3 Haiku** (`claude-3-haiku`): Fast responses

---

## 🔄 How It Works

### **Automatic API Key Injection**

The system automatically detects which API services are needed based on the nodes in your workflow and injects the appropriate keys:

```python
# Example workflow with multiple providers
workflow = {
    "prompt": {
        "1": {"class_type": "FluxProImageNode"},      # Uses BFL_API_KEY
        "2": {"class_type": "GeminiVisionNode"},      # Uses GEMINI_API_KEY  
        "3": {"class_type": "AnthropicSonnetNode"}    # Uses ANTHROPIC_API_KEY
    }
}

# Automatic injection result:
# extra_data: {
#     "api_key_comfy_org": "sk-bfl-...",    # BFL key for FLUX
#     "api_key_gemini": "gsk-...",          # Gemini key
#     "api_key_anthropic": "sk-ant-..."     # Anthropic key
# }
```

### **Priority System**

When multiple providers use the same injection point (`api_key_comfy_org`), priority is:

1. **BFL_API_KEY** (highest priority)
2. **OPENAI_API_KEY**
3. **IDEOGRAM_API_KEY** (lowest priority)

### **Supported Node Types**

#### **Gemini Nodes**
- `GeminiImageNode` - Image generation
- `GeminiTextNode` - Text processing
- `GeminiVisionNode` - Image analysis
- `GeminiProNode` - Advanced reasoning
- `GeminiFlashNode` - Fast processing

#### **Anthropic Nodes**
- `AnthropicClaudeNode` - General Claude model
- `AnthropicSonnetNode` - Claude Sonnet variants
- `AnthropicHaikuNode` - Claude Haiku variants
- `AnthropicOpusNode` - Claude Opus model
- `ClaudeImageNode` - Image understanding

---

## 🧪 Testing Your Configuration

### **1. Check API Keys**
```bash
cd /path/to/DreamLayer/dream_layer_backend
python3 test_api_keys.py
```

### **2. Verify Model Availability**
```bash
curl http://localhost:5002/api/models
```

Should return models for all configured API providers.

### **3. Test Workflow**
Create a workflow with Gemini or Anthropic nodes and verify the API keys are properly injected.

---

## 📊 Model Selection in Frontend

### **Model Dropdown**

When API keys are configured, the models automatically appear in the frontend model selector:

**Without API keys:**
- Only local Stable Diffusion models

**With GEMINI_API_KEY:**
- Local models +
- Gemini 1.5 Pro
- Gemini 1.5 Flash
- Gemini Pro Vision
- Gemini Experimental

**With ANTHROPIC_API_KEY:**
- Previous models +
- Claude 3.5 Sonnet
- Claude 3.5 Haiku
- Claude 3 Opus
- Claude 3 Sonnet
- Claude 3 Haiku

---

## 🔒 Security Best Practices

### **1. Environment Variables**
- ✅ Store API keys in `.env` file
- ✅ Add `.env` to `.gitignore`
- ❌ Never commit API keys to version control
- ❌ Never hardcode keys in source code

### **2. Key Management**
- 🔄 Rotate API keys regularly
- 🔍 Monitor API usage and costs
- 🛡️ Use environment-specific keys (dev/prod)
- 📊 Set usage limits in provider dashboards

### **3. Access Control**
- 👥 Limit key access to necessary team members
- 🔐 Use IAM/RBAC where available
- 📋 Keep audit logs of key usage
- 🚨 Revoke compromised keys immediately

---

## 🐛 Troubleshooting

### **Common Issues**

#### **"No models for GEMINI_API_KEY"**
- ✅ Check key format (should start with `gsk-` or `AIza`)
- ✅ Verify key is active in Google AI Studio
- ✅ Check API quotas and billing

#### **"No models for ANTHROPIC_API_KEY"**
- ✅ Check key format (should start with `sk-ant-`)
- ✅ Verify key is active in Anthropic Console
- ✅ Check account credits and limits

#### **"API key not injected"**
- ✅ Restart the backend servers after adding keys
- ✅ Check `.env` file location (project root)
- ✅ Verify no extra spaces around key values
- ✅ Check server logs for key loading messages

#### **"Wrong API key used"**
- ✅ Check priority system (BFL > OpenAI > Ideogram)
- ✅ Verify node types match expected providers
- ✅ Check `NODE_TO_API_KEY_MAPPING` in source code

### **Debug Mode**

Enable debug logging to see key injection process:

```bash
# Check if keys are loaded
[DEBUG] Found GEMINI_API_KEY: gsk-abc1...xyz9
[DEBUG] Found ANTHROPIC_API_KEY: sk-ant-...xyz9

# Check workflow scanning
[DEBUG] Found GeminiImageNode node - needs GEMINI_API_KEY
[DEBUG] Found AnthropicSonnetNode node - needs ANTHROPIC_API_KEY

# Check injection results
[DEBUG] Injected GEMINI_API_KEY as api_key_gemini
[DEBUG] Injected ANTHROPIC_API_KEY as api_key_anthropic
```

---

## 📈 Usage Examples

### **Example 1: Image Analysis Workflow**
```json
{
  "workflow": {
    "1": {
      "class_type": "LoadImage",
      "inputs": {"image": "input.jpg"}
    },
    "2": {
      "class_type": "GeminiVisionNode", 
      "inputs": {
        "image": ["1", 0],
        "prompt": "Describe this image in detail"
      }
    },
    "3": {
      "class_type": "AnthropicSonnetNode",
      "inputs": {
        "text": ["2", 0],
        "prompt": "Create a creative story based on this description"
      }
    }
  }
}
```

**Result**: Gemini analyzes the image, Claude creates a story → Uses both API keys

### **Example 2: Multi-Provider Generation**
```json
{
  "workflow": {
    "1": {
      "class_type": "FluxProImageNode",
      "inputs": {"prompt": "A futuristic city"}
    },
    "2": {
      "class_type": "GeminiImageNode",
      "inputs": {"prompt": "A natural landscape"}  
    },
    "3": {
      "class_type": "ClaudeImageNode",
      "inputs": {"prompt": "An artistic interpretation"}
    }
  }
}
```

**Result**: Three different AI providers generate images → Uses all three API keys

---

## 🔄 Migration Guide

### **Upgrading from Previous Version**

1. **Add new environment variables**:
   ```bash
   echo "GEMINI_API_KEY=your-key-here" >> .env
   echo "ANTHROPIC_API_KEY=your-key-here" >> .env
   ```

2. **Restart backend services**:
   ```bash
   # Kill existing processes
   pkill -f "python.*server.py"
   
   # Restart services
   ./start_dream_layer.sh
   ```

3. **Verify configuration**:
   ```bash
   python3 test_api_keys.py
   ```

4. **Update workflows** (if using custom nodes):
   - Replace custom Gemini implementations with `GeminiImageNode`
   - Replace custom Claude implementations with `AnthropicSonnetNode`

---

## 🎯 Implementation Status

### **✅ Completed Features**
- ✅ Gemini API key support and injection
- ✅ Anthropic API key support and injection  
- ✅ Model availability based on configured keys
- ✅ Priority handling for competing keys
- ✅ Comprehensive test suite (6/6 tests passing)
- ✅ Error handling for missing keys
- ✅ Debug logging and troubleshooting

### **🔄 Ready for Extension**
- 🆕 Additional node types (easily added to mappings)
- 🆕 New API providers (follow same pattern)
- 🆕 Custom key routing (modify injection logic)
- 🆕 Provider-specific configurations

---

## 📝 Configuration Summary

**Minimum setup for new providers:**

```bash
# 1. Add to .env
GEMINI_API_KEY=gsk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# 2. Restart servers
./start_dream_layer.sh

# 3. Verify
curl http://localhost:5002/api/models

# 4. Start using in workflows!
```

**Result**: Immediate access to 9 additional AI models (4 Gemini + 5 Anthropic) in DreamLayer! 🚀