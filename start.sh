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
    exit_status=$?
    if [ $exit_status -ne 0 ]; then
        echo "Error: $exit_status"
    else
        echo -e "\033[32mBot launched!\033[0m"
    fi
else
    if command -v rpm &> /dev/null; then
        if rpm -q python3 &> /dev/null; then
            echo " "
            echo "Bot is not configured..."
            echo -n "Install using venv? (ONLY VENV) [Y/n]: "
            read -r key
            if [[ $key == "n" || $key == "N" ]]; then
                echo -e "\033[31mExiting script..."
                exit 1
            elif [[ $key == "Y" || $key == "y" || $key == "" ]]; then
                python3 -m venv lenv
                source lenv/bin/activate
                if [[ -f "requirements.txt" ]]; then
                    pip install -r requirements.txt
                    pip install git+https://github.com/DisnakeCommunity/disnake-ext-components.git
                else
                    echo -e "\033[31mError: requirements.txt not found. Please make sure the file exists."
                    exit 1
                fi
                echo " "
                echo -e "\033[32mClose the script and configure the bot parameters in config.py"
                read -r -p "Press Enter to continue..."
                exit 0
            fi
        fi
    elif command -v pacman &> /dev/null; then
        if pacman -Q python3 &> /dev/null; then
            echo " "
            echo "Bot is not configured..."
            echo -n "Install using venv? (ONLY VENV) [Y/n]: "
            read -r key
            if [[ $key == "n" || $key == "N" ]]; then
                echo -e "\033[31mExiting script..."
                exit 1
            elif [[ $key == "Y" || $key == "y" || $key == "" ]]; then
                python3 -m venv lenv
                source lenv/bin/activate
                if [[ -f "requirements.txt" ]]; then
                    pip install -r requirements.txt
                    pip install git+https://github.com/DisnakeCommunity/disnake-ext-components.git
                else
                
                    echo -e "\033[31mError: requirements.txt not found. Please make sure the file exists."
                    exit 1
                fi
                echo " "
                echo -e "\033[32mClose the script and configure the bot parameters in config.py"
                read -r -p "Press Enter to continue..."
                exit 0
            fi
        fi
    elif command -v dpkg &> /dev/null; then
        if dpkg -l python3 &> /dev/null; then
            echo " "
            echo "Bot is not configured..."
            echo -n "Install using venv? (ONLY VENV) [Y/n]: "
            read -r key
            if [[ $key == "n" || $key == "N" ]]; then
                echo -e "\033[31mExiting script..."
                exit 1
            elif [[ $key == "Y" || $key == "y" || $key == "" ]]; then
                python3 -m venv lenv
                source lenv/bin/activate
                if [[ -f "requirements.txt" ]]; then
                    pip install -r requirements.txt
                    pip install git+https://github.com/DisnakeCommunity/disnake-ext-components.git
                else
                    echo -e "\033[31mError: requirements.txt not found. Please make sure the file exists."
                    exit 1
                fi
                echo " "
                echo -e "\033[32mClose the script and configure the bot parameters in config.py"
                read -r -p "Press Enter to continue..."
                exit 0
            fi
        fi
    else
        echo " "
        echo -e "\033[31mPython is not installed. Install Python version 3.11.7 using your package manager"
        exit 1
    fi
fi
