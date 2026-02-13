#!/bin/bash
cp -R ./etc/* /etc/
cp -R ./root/* /root/
systemctl daemon-reload
systemctl enable ai-polligenapi4261
systemctl enable ai-polligenapi4290-free
systemctl start ai-polligenapi4261
systemctl start ai-polligenapi4290-free
echo ""
echo "Installed ! Services available by default on 127.0.0.1 ports 4261 (paid) and 4290 (free)"
echo ""
echo "For Paid image generator version, you must set REAL Pollinations API key in : "
echo ""
echo "/root/ai/polligenapi4261/pollitations.key" 
echo ""
echo "and restart service by : "
echo ""
echo "systemctl restart ai-polligenapi4261"
echo ""
echo ""
echo "Check manual on https://github.com/mamontuka/pollinations2openai"
echo ""
echo "for connect services to LiteLLM or OpenwebUI directly"
echo ""
echo ""
