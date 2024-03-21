#!/bin/bash

echo -e """\033[35m
  ██╗     ██╗   ██╗███╗   ███╗██╗██╗  ██╗    ██╗   ██╗██████╗    ███████╗
  ██║     ██║   ██║████╗ ████║██║╚██╗██╔╝    ██║   ██║╚════██╗   ╚════██║
  ██║     ██║   ██║██╔████╔██║██║ ╚███╔╝     ██║   ██║ █████╔╝       ██╔╝
  ██║     ██║   ██║██║╚██╔╝██║██║ ██╔██╗     ╚██╗ ██╔╝ ╚═══██╗      ██╔╝ 
  ███████╗╚██████╔╝██║ ╚═╝ ██║██║██╔╝ ██╗     ╚████╔╝ ██████╔╝██╗   ██║  
  ╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝╚═╝  ╚═╝      ╚═══╝  ╚═════╝ ╚═╝   ╚═╝  \033[0m
"""

echo "Welcome to Lumix v3.7 startup script!"
echo "if you have questions join our support Discord server - discord.gg/SpTBwz4xsa"

if [ -e ./lenv ]; then
    echo " "
    echo "Launching venv..."
    source ./lenv/bin/activate
    echo -e "\033[32mVenv launched!\033[0m"
    echo "Launching bot..."
    python3 ./bot.py
else
    PYTHON_VERSION=$(python3 --version)
    if [[ $PYTHON_VERSION == *"Python 3."* ]]; then
        echo " "
        echo "Bot is not configured..."
        echo -n "Install using venv? (ONLY VENV) [Y/n]: "
        read -r key
        if [[ $key == "n" || $key == "N" ]]; then
            echo -e "\033[31mUse outside venv is not supported."
            echo -e "Exiting..."
            exit 1
        elif [[ $key == "Y" || $key == "y" || $key == "" ]]; then
            python3 -m venv lenv
            source lenv/bin/activate
            if [[ -f "requirements.txt" ]]; then
                pip install -r requirements.txt
            else
                echo -e "\033[31mError: requirements.txt not found. Please make sure the file exists."
                exit 1
            fi
            echo " "
            echo -e "\033[32mClose the script and configure the bot parameters in config.py"
            read -r -p "Press Enter to continue..."
            exit 0
        fi
    else
        echo -e "\033[31mPython 3 is not installed. Please install Python 3 to proceed.\033[0m"
        exit 1
    fi
fi

