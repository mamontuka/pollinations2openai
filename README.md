# pollinations2openai

**A proxy for integrating Pollinations.ai image generators into OpenAI-compatible systems**

`pollinations2openai` is a simple but practical proxy service that allows you to connect **Pollinations.ai** image generation (both free and paid) to **OpenAI-compatible APIs**, such as **OpenWebUI** and **LiteLLM**, without modifying client code.

The project exposes Pollinations.ai as an OpenAI-style `/v1/images` endpoint, making it usable anywhere an OpenAI image model is expected.

---

## ✨ What This Project Does

- Accepts OpenAI-compatible image generation requests  
- Translates them into Pollinations.ai API calls  
- Returns responses in OpenAI-compatible format  
- Works with **OpenWebUI**, **LiteLLM**, and any OpenAI-compatible client  
- Runs locally as systemd services

This effectively allows you to use Pollinations.ai as a drop-in replacement for OpenAI image models.

---

## 🚀 Features

- ✅ OpenAI-compatible API (`/v1`)
- ✅ Free and paid Pollinations.ai endpoints
- ✅ No client-side code changes required
- ✅ Works with OpenWebUI and LiteLLM
- ✅ Runs as background system services
- ✅ Simple installation via shell script

---

## 🛠 Requirements

- Linux (Debian / Ubuntu recommended)
- `systemd`
- Root access (for service installation)

---

## 🛠 Requirements

- Linux (Debian / Ubuntu recommended)
- `systemd`
- Root access (for service installation)

---

## 📦 Installation

### 1. Clone the repository

    git clone https://github.com/mamontuka/pollinations2openai.git
    cd pollinations2openai

### 2. Run the installer

    sudo bash install.sh

The installer will:

    Copy service files to /etc/systemd/system

    Deploy application files under /root/ai

    Reload systemd

    Enable and start the services automatically

On success, you should see:

    Installed ! Services available by default on 127.0.0.1 ports 4261 (paid) and 4290 (free)

### ⚙️ Services and Ports
Service Name	Port	Description
ai-polligenapi4261	4261	Paid Pollinations endpoint
ai-polligenapi4290-free	4290	Free Pollinations endpoint

Both services expose an OpenAI-compatible API under /v1.
🔑 API Key Configuration (Paid Mode)

If you want to use paid Pollinations models:

Obtain a Pollinations API key

Save it to:

    /root/ai/polligenapi4261/pollitations.key

Restart the service:

    systemctl restart ai-polligenapi4261

The free service (4290) does not require an API key.

### ⚙️ LLM SYSTEM PROMPT EXAMPLE

        You are a creative proxy for generating images in ART MODE.
        Your tasks as an artist:

           - Accept user requests in any language.
           - Internally translate them into English for the image generator.
           - Accurately preserve the meaning of the request.
           - Actively enhance minimal requests by adding artistic, cinematic, and stylistic details:
               - composition, lighting, atmosphere
               - camera angles, rendering techniques
               - realistic or artistic textures, colors and mood
               - qualities of professional photography, digital or concept art
           - Never change the subject, environment or meaning of the request.
           - Do not explain or reveal internal translation or prompt.
           - Do not produce text.
           - Output only the final image.
#

### ⚙️ Third part custom tool for image auto generation in OpenwebUI

**Created by :**

author_email: nokodo@nokodo.net <br>
author_url: https://nokodo.net <br>
funding_url: https://ko-fi.com/nokodo <br>
repository_url: https://nokodo.net/github/open-webui-extensions <br>
#

Create tool in OpenwebUI Workspace, and add in created tool this one code :

**https://github.com/mamontuka/pollinations2openai/blob/main/openwebui_auto_image_tool.py**

#

### 🧠 Using with OpenWebUI

    Open OpenWebUI → Settings → Connections

    Add a new OpenAI-compatible connection

Free version

Base URL: http://127.0.0.1:4290/v1
API Key: dummy

Paid version

Base URL: http://127.0.0.1:4261/v1
API Key: dummy

After saving, Pollinations will appear as an image generation backend.

**Direct connect to pollinations paid API proxy :**

![screenshot](https://github.com/mamontuka/pollinations2openai/blob/main/pollinations_openwebui_to_direct_proxy_api.jpg)


### 🧩 Using with LiteLLM

**Connection to pollinations proxies over LiteLLM :**

![screenshot](https://github.com/mamontuka/pollinations2openai/blob/main/pollinations_openwebui_to_litellm.jpg)

Example config.yaml entry:

    model_list:
      - model_name: image-gen
        litellm_params:
          model: openai/klein
          mode: image_generation
          api_base: "http://127.0.0.1:4261/v1"
          api_key: "not-needed"
          tpd: 450 # Limit per day (stored in Redis)
          rpm: 5  # Limit per minute

      - model_name: image-gen
        litellm_params:
          model: openai/flux
          mode: image_generation
          api_base: "http://127.0.0.1:4290/v1"
          api_key: "not-needed"

    router_settings:
      routing_strategy: least-busy
      enable_fallbacks: True
      num_retries: 5
      timeout: 300
      context_window_fallbacks: [] 
      allowed_fails: 3
      cooldown_time: 60

    litellm_settings:
      drop_params: True
      set_verbose: False

      cache: True
      cache_params:
        type: redis
        host: "localhost"
        port: 6379
        # password: "redis_password" # password for Redis if present


### 📌 Notes

The API key value passed by clients is ignored; authentication is handled internally

This project focuses only on image generation

Designed to be minimal, stable, and easy to integrate

### 📜 License

This project is licensed under the GNU GPL-3.0 License.

### 🤝 Contributing

Pull requests, issues, and improvements are welcome.
Keep changes minimal and aligned with OpenAI API compatibility.

